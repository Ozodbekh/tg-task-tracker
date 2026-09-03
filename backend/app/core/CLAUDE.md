# core

Settings and shared primitives.

- `config.py` — `Settings` loaded from the project-root `.env`, exposed as the
  `settings` singleton. Paths default under `backend/data/`.
- `security.py` — `PasswordHasher` (scrypt, salted, constant-time compare) and
  `TokenIssuer` (HS256 JWT with an expiry).
- `links.py` — `message_link` builds the `t.me/c/...` deep link for a
  supergroup message. A private chat has no linkable form and gets `None`.
- `hash_password.py` — run through `make hash-password`. Asks for a password
  twice and prints the hash for `ADMIN_PASSWORD_HASH`.

Nothing else reads environment variables.
