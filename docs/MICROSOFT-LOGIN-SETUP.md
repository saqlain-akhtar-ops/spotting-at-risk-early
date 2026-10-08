# Microsoft sign-in with Microsoft Entra ID

The integration is prepared but disabled until all configuration values are set. Existing project password login continues to work. No Microsoft tenant or app registration was created by this code change, and a real Microsoft login has not yet been tested.

## Design

Single-tenant server-side OpenID Connect authorization-code flow with PKCE S256, encrypted short-lived flow cookie, state and nonce checks, signature/issuer/audience/expiry validation and an explicit mapping from Microsoft object ID to an existing local user ID. Microsoft email/name claims never grant access or assign roles.

The mapped user's existing role, class/student scope, CSRF rules and eight-hour session apply. Unmapped or inactive users cannot enter the workspace. This login does not connect Power BI Service, import Microsoft users, enable Graph access or grant Microsoft report permissions.

## Registration steps

1. Use an Entra tenant you are authorized to administer. University tenants may require university IT to register/approve the application.
2. In Microsoft Entra admin center, open **App registrations → New registration**. Choose **Accounts in this organizational directory only**. Use a clear project name.
3. Add a **Web** redirect URI, exactly:
   `https://spotting-at-risk-early.vercel.app/api/auth/microsoft/callback`
4. Record Directory (tenant) ID and Application (client) ID. Leave implicit access-token/ID-token grant options disabled; this application uses authorization code flow.
5. Create a client secret under Certificates & secrets. Configure its **value**, not its ID, as a server environment secret. Never put it in chat, frontend code, screenshots or GitHub. Record its expiry and rotate it before expiry.
6. Find each authorized user's **Object ID in this tenant**. Map it to the existing project's user ID. Verify the user and intended scope first. Seeded Advisor A is ID 2 and Advisor B ID 3; confirm live records before mapping. Do not automatically map all university users or give a new user an administrator role.
7. Configure the six variables below in Vercel for the intended environment, then redeploy. Preview domains require their own registered callback/configuration; do not expect a production callback to return to a preview.

## Environment variables

| Variable | Value |
|---|---|
| ENTRA_TENANT_ID | Directory tenant UUID |
| ENTRA_CLIENT_ID | Registered application UUID |
| ENTRA_CLIENT_SECRET | Secret value, kept server-side |
| ENTRA_REDIRECT_URI | Exact registered Web callback URL |
| ENTRA_STATE_SECRET | Independently generated random secret of at least 32 characters |
| ENTRA_USER_MAP | JSON mapping Microsoft object UUID to existing numeric project user ID |

Mapping shape only (replace the example UUID):

```json
{"33333333-3333-3333-3333-333333333333": 2}
```

For local testing, register a separate Web redirect URI `http://localhost:8000/api/auth/microsoft/callback` and put configuration in the ignored local environment file. Do not reuse production secrets in sample files. Configure session cookie security appropriately for HTTPS production versus local HTTP.

## Activation and acceptance check

- GET `/api/auth/options` returns `microsoft_enabled: true` only when configuration is complete and structurally valid. The login page then shows **Sign in with Microsoft**.
- Register/configure a permitted test teacher. Use a private browser session, complete Microsoft login, confirm the expected identity and 240-student scope.
- Verify a different/unmapped object ID is rejected; another teacher's students remain inaccessible.
- Verify existing password login, CSRF protection, sign-out and session restoration still work.
- Cancel login and restart it; an expired or mismatched flow must not create a session.
- Tenant policy may impose MFA, consent or conditional-access requirements. Follow the institution's policy instead of bypassing it.

Automated checks cover disabled configuration, PKCE/state construction, signed-token validation, incorrect signature/audience/issuer/nonce/tenant/expiry, scope preservation and rejection of unmapped users. Provider calls are mocked in callback tests. Successful end-to-end Microsoft sign-in remains dependent on actual registration and tenant testing.

## Troubleshooting

- Button hidden: incomplete/malformed environment configuration, or deployed environment has not been redeployed.
- Redirect mismatch: registered URI must exactly match scheme, hostname and callback path.
- Account not authorized: its tenant object ID is not mapped to an active local user.
- Sign-in failed: expired/cancelled flow, provider rejection, token validation failure or connectivity. Do not expose tokens/provider error bodies in logs or screenshots.
- Remove all ENTRA configuration to disable the provider while retaining project-password access.

Microsoft references: [authorization code flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow), [OpenID Connect](https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc), [ID token claims and stable identity](https://learn.microsoft.com/en-us/entra/identity-platform/id-token-claims-reference).
