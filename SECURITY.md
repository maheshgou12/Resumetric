# Security Policy

## 🔒 Supported Versions

We actively maintain and provide security updates for the latest production release on the `main` branch.

| Version | Supported |
| :--- | :--- |
| `main` (Latest) | ✅ Supported |
| `< 1.0.0` | ❌ End of Life |

---

## 🛡️ Security Architecture

CareerLens AI enforces strict enterprise security practices:

1. **Password Security**: Passwords are encrypted with `bcrypt` (12 rounds) and never stored in plaintext.
2. **Session & Token Management**:
   - Short-lived JSON Web Tokens (30-minute access lifetime).
   - Rotating cross-origin `httpOnly`, `Secure`, `SameSite=None` refresh tokens stored in hashed format in the database.
3. **Email Verification & Password Reset**:
   - Single-use cryptographically random tokens (`secrets.token_urlsafe(32)`) expiring in 15 minutes.
   - Delivered exclusively to the verified email address via TLS-encrypted SMTP (Port 465 SSL / 587 STARTTLS).
   - Zero on-screen token leaks or dev fallback links in production mode.
4. **CORS & Domain Whitelisting**: Strict origin controls restricting API requests to authorized deployment origins (`https://resumetric-1.onrender.com` and `https://*.vercel.app`).
5. **Database Isolation**: Support for SQLAlchemy 2.0 parameterized queries preventing SQL injection vulnerabilities.

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability within CareerLens AI:
1. Please **do not open a public GitHub issue**.
2. Send an email with vulnerability details and reproduction steps to: `maheshburra2712@gmail.com`.
3. We will acknowledge receipt within 24 hours and provide an estimated fix timeline.
