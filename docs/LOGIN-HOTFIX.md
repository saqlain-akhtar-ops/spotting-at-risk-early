# Hackathon login diagnosis — 7 October 2026

```yaml
Expected: Login -> authenticated session -> dashboard
Actual: Local installation password -> HTTP 401 -> login screen without visible feedback
Error: Invalid email or password (message obscured behind the login overlay)
Root cause: Hosted Neon and laptop MySQL use different demo passwords; the deployed frontend displayed failure feedback outside the opaque login cover.
```

The correct hosted administrator password returned HTTP 200, a Secure/HttpOnly session cookie, successful `/api/auth/me`, metadata, live dashboard and extra-class responses. The laptop password and an intentionally invalid password returned HTTP 401 with no cookie. No server-side session, database-connectivity or HTTPS-cookie failure was reproduced. Browser console errors were empty during this reproduction. This establishes a reproducible failure mechanism, not a claim about an unseen password entered by the presenter.

Authentication is custom FastAPI authentication: form -> POST `/api/auth/login` -> active SQLAlchemy User -> PBKDF2 password verification -> random token with hashed session record -> Secure/HttpOnly/SameSite=Strict cookie -> `/api/auth/me` -> authorized metadata and dashboard API -> hide the login cover. There is no Supabase/NextAuth provider or redirect callback.

The hosted app uses its secret DATABASE_URL to reach Neon PostgreSQL. Demo accounts are seeded during the build only when the database is empty. Runtime login never reads the laptop credential JSON. Cloud sessions and records persist in the database; `/tmp` is not authoritative session storage. Existing passwords and database records were not reset.

## Minimal fix

- Put a keyboard-accessible error alert inside the login form.
- Explain that hosted and local demo credentials differ.
- Show signing-in progress, recover from malformed/proxy errors and timeouts.
- Dismiss the login cover only after authenticated dashboard initialization succeeds.
- Preserve existing layout, auth boundaries and backend behavior.

The private presentation credentials are saved outside Git in `data/HACKATHON_LOGIN.txt` in the main project folder. They must not be committed, placed in public frontend assets or copied into an issue. The audit work remains separate from this emergency release.

## Verification

Six Node regression tests exercise the actual frontend functions. The existing isolated backend suite covers login, CSRF, logout, role scope, dashboard filters, student profiles and support workflows. Post-deployment browser verification must cover login -> dashboard -> At-Risk Triage -> Student 360 -> Extra Classes, then a reload to confirm session continuity.
