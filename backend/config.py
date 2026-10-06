"""Validate deployment configuration without printing connection secrets."""
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    production: bool
    demo_seed: bool
    cookie_secure: bool
    allowed_hosts: tuple[str, ...]
    api_docs: bool

def load_settings(env=None):
    env=os.environ if env is None else env
    mode=env.get('APP_ENV','development').lower()
    if mode not in ('development','production'):raise ValueError('APP_ENV must be development or production')
    production=mode=='production'
    def boolean(key,default):
        value=env.get(key,default).lower()
        if value not in ('true','false','1','0'):raise ValueError(f'{key} must be true/false or 1/0')
        return value in ('true','1')
    demo=boolean('DEMO_SEED','0' if production else '1')
    secure=boolean('COOKIE_SECURE','true' if production else 'false')
    hosts=tuple(h.strip() for h in env.get('ALLOWED_HOSTS','' if production else '*').split(',') if h.strip())
    if production:
        if demo:raise ValueError('Production requires DEMO_SEED=0')
        if not secure:raise ValueError('Production requires COOKIE_SECURE=true')
        if not hosts or any('*' in h for h in hosts):raise ValueError('Production requires explicit ALLOWED_HOSTS without wildcards')
        if not env.get('DATABASE_URL'):raise ValueError('Production requires an explicit DATABASE_URL')
    return Settings(production,demo,secure,hosts or ('*',),boolean('API_DOCS','false' if production else 'true'))
