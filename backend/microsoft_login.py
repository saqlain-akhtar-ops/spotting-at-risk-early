"""Optional single-tenant Entra OIDC login with explicit local-user mapping."""
import base64
import hashlib
import json
import os
import secrets
import time
from functools import lru_cache
from urllib.parse import urlencode, urlsplit
from urllib.request import Request as UrlRequest, urlopen
from uuid import UUID
import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from .models import User

COOKIE = 'entra_flow'

def configuration():
    keys = ('ENTRA_TENANT_ID', 'ENTRA_CLIENT_ID', 'ENTRA_CLIENT_SECRET',
            'ENTRA_REDIRECT_URI', 'ENTRA_STATE_SECRET', 'ENTRA_USER_MAP')
    values = {key: os.getenv(key, '') for key in keys}
    if not all(values.values()):
        return None
    tenant = str(UUID(values['ENTRA_TENANT_ID']))
    client = str(UUID(values['ENTRA_CLIENT_ID']))
    redirect = values['ENTRA_REDIRECT_URI']
    parsed = urlsplit(redirect)
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError('Entra callback must not include credentials, query or fragment')
    local = parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1')
    if not (parsed.scheme == 'https' and parsed.hostname) and not local:
        raise ValueError('Use an HTTPS Entra callback or local development loopback')
    if parsed.path != '/api/auth/microsoft/callback':
        raise ValueError('Entra callback must end in /api/auth/microsoft/callback')
    if len(values['ENTRA_STATE_SECRET']) < 32:
        raise ValueError('Entra state secret must contain at least 32 characters')
    mapping = json.loads(values['ENTRA_USER_MAP'])
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError('Configure an explicit Entra object-ID to local-user-ID map')
    mapping = {str(UUID(key)): int(value) for key, value in mapping.items()}
    if any(value < 1 for value in mapping.values()):
        raise ValueError('Mapped user IDs must be positive')
    return {'tenant': tenant, 'client': client, 'secret': values['ENTRA_CLIENT_SECRET'],
            'redirect': redirect, 'state_secret': values['ENTRA_STATE_SECRET'],
            'users': mapping, 'secure': parsed.scheme == 'https'}

def signed_flow(config):
    now = int(time.time())
    payload = {'state': secrets.token_urlsafe(32), 'nonce': secrets.token_urlsafe(32),
               'verifier': secrets.token_urlsafe(48), 'iat': now, 'exp': now + 600}
    # The verifier is a proof secret: encrypt it, not just a readable signed JWT.
    from cryptography.fernet import Fernet
    key = base64.urlsafe_b64encode(hashlib.sha256(config['state_secret'].encode()).digest())
    cookie = Fernet(key).encrypt(json.dumps(payload).encode()).decode()
    return payload, cookie

def read_flow(config, cookie, state):
    from cryptography.fernet import Fernet, InvalidToken
    key = base64.urlsafe_b64encode(hashlib.sha256(config['state_secret'].encode()).digest())
    try:
        payload = json.loads(Fernet(key).decrypt(cookie.encode(), ttl=600))
        if payload['exp'] <= time.time() or not secrets.compare_digest(payload['state'], state):
            raise ValueError('Invalid state')
        return payload
    except (InvalidToken, ValueError, KeyError, TypeError):
        raise HTTPException(400, 'Microsoft sign-in expired or state did not match. Start again.')

def exchange_code(config, code, verifier):
    url = f"https://login.microsoftonline.com/{config['tenant']}/oauth2/v2.0/token"
    body = urlencode({'client_id': config['client'], 'client_secret': config['secret'],
                      'grant_type': 'authorization_code', 'code': code,
                      'redirect_uri': config['redirect'], 'code_verifier': verifier}).encode()
    request = UrlRequest(url, data=body, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    with urlopen(request, timeout=15) as response:
        return json.load(response)['id_token']

@lru_cache(maxsize=4)
def signing_keys(tenant):
    return jwt.PyJWKClient(f'https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys', timeout=10)

def validate_identity(config, token, nonce):
    key = signing_keys(config['tenant']).get_signing_key_from_jwt(token).key
    claims = jwt.decode(token, key, algorithms=['RS256'], audience=config['client'],
                        issuer=f"https://login.microsoftonline.com/{config['tenant']}/v2.0",
                        options={'require': ['exp', 'iat', 'iss', 'aud', 'nonce', 'oid', 'tid']})
    if str(UUID(claims['tid'])) != config['tenant'] or not secrets.compare_digest(claims['nonce'], nonce):
        raise ValueError('Invalid tenant or nonce')
    return str(UUID(claims['oid']))

def install_microsoft_login(app, database, issue_session):
    def configured():
        try:
            config = configuration()
        except (ValueError, TypeError, json.JSONDecodeError):
            raise HTTPException(503, 'Microsoft sign-in configuration needs administrator review')
        if not config:
            raise HTTPException(503, 'Microsoft sign-in is not configured yet')
        return config

    @app.get('/api/auth/options')
    def options():
        try:
            enabled = configuration() is not None
        except (ValueError, TypeError):
            enabled = False
        return {'success': True, 'data': {'microsoft_enabled': enabled}, 'message': 'Success'}

    @app.get('/api/auth/microsoft/start')
    def start():
        config = configured()
        flow, cookie = signed_flow(config)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(flow['verifier'].encode()).digest()).rstrip(b'=').decode()
        params = {'client_id': config['client'], 'response_type': 'code', 'response_mode': 'query',
                  'redirect_uri': config['redirect'], 'scope': 'openid profile',
                  'state': flow['state'], 'nonce': flow['nonce'],
                  'code_challenge': challenge, 'code_challenge_method': 'S256'}
        response = RedirectResponse(f"https://login.microsoftonline.com/{config['tenant']}/oauth2/v2.0/authorize?" + urlencode(params))
        response.set_cookie(COOKIE, cookie, httponly=True, secure=config['secure'],
                            samesite='lax', max_age=600, path='/api/auth/microsoft')
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/api/auth/microsoft/callback')
    def callback(request: Request, db=Depends(database)):
        config = configured()
        try:
            flow = read_flow(config, request.cookies.get(COOKIE, ''), request.query_params.get('state', ''))
            code = request.query_params.get('code', '')
            if request.query_params.get('error') or not code or len(code) > 8192:
                raise ValueError('Microsoft sign-in not completed')
            token = exchange_code(config, code, flow['verifier'])
            oid = validate_identity(config, token, flow['nonce'])
            user_id = config['users'].get(oid)
            user = db.get(User, user_id) if user_id else None
            if not user or not user.active:
                response = RedirectResponse('/?microsoft_error=not_authorized', status_code=303)
            else:
                response = RedirectResponse('/', status_code=303)
                issue_session(db, user, response, method='microsoft')
        except Exception:
            db.rollback()
            # Never expose provider codes, tokens or exception bodies in URLs/logs.
            response = RedirectResponse('/?microsoft_error=sign_in_failed', status_code=303)
        response.delete_cookie(COOKIE, path='/api/auth/microsoft')
        response.headers['Cache-Control'] = 'no-store'
        return response
