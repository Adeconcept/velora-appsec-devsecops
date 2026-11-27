# Milestone 2 · Who can do what?

| HTTP resource | Signed out | Customer | Administrator |
|---|---|---|---|
| GET catalog and product | Browse | Browse | Browse |
| GET /login, POST /login | Obtain a form, authenticate | Return to own profile | Return to own profile |
| GET /profile, POST /profile | 401 | Read own email and name, edit own name | Same, for own account |
| GET /orders | 401 | List own references, dates and statuses | 403 |
| GET /orders/&lt;id&gt; | 401 | Read own order and lines. Any other ID returns 404 | 403 |
| GET /admin/orders | 401 | 403 | List fulfillment references, dates and statuses across accounts |
| POST /admin/orders/&lt;id&gt;/ship | 401 | 403 | Move one processing order to shipped. Repeating returns 409 |
| POST /logout | 401 | Revoke current session | Revoke current session |

Every permitted POST requires a CSRF token tied to the current session, including the anonymous login form. Missing or unrelated tokens return 400. Each endpoint on the account blueprint needs an explicit entry in the role policy. A missing entry denies access.

## Why checking ownership matters

Authentication tells Flask who is making a request. A signed-in customer still has no right to another customer's order. Looking up a private order using only its ID would allow an authenticated user who learns another ID to read purchases and amounts. A dropdown, hidden link or unpredictable reference cannot enforce that boundary.

The detail query binds the requested order ID and the current account ID together. Flask obtains the account ID from the server-side session. A missing match ends the request before any line items are read. Both the list and the detail route apply ownership checks. The profile route uses the session owner directly and accepts one editable field. The admin action reads the role from SQLite and performs a conditional update of one status field. The owner, amount and order lines never come from that form.

In the two-customer test, each identity reads its own line total and receives the same 404 for an unrelated order and a missing order. A second test records that a permitted fulfillment change becomes visible to the owner. These are tests of the implemented policy. The earlier penetration-test findings belong to the separate training labs.

## Passwords, sessions and request integrity

- The local seed prompts for each password, hashes it with Werkzeug's salted scrypt implementation and stores only the encoded hash. Login uses the library verifier and a generic failure response. An unknown email still incurs a password-hash check.
- A browser receives a random 32-byte opaque token. SQLite holds its SHA-256 digest, a separate random CSRF token, expiry and the user reference. Hashing a high-entropy lookup token is inexpensive. A human password needs the more expensive salted password hash. Each private request reads the current account role from the database.
- Successful login replaces the anonymous session and its CSRF token. Logout deletes the database row. Sessions expire after 15 minutes of account inactivity or eight hours from creation. Public catalog views do not refresh the idle window. Expired rows are pruned on session creation.
- Each account form submits a synchronizer token. The server checks it with a constant-time comparison before accepting the POST. Private responses request no storage. Cookies are host-only, HttpOnly, and SameSite=Strict. Local HTTP uses a cookie without Secure. Set VELORA_HTTPS=1 when testing with an actual HTTPS listener. This flag changes the cookie attribute and does not configure TLS.

## Traceability and limits

| Source | Local implementation and evidence |
|---|---|
| ASVS v5.0.0 8.2.2, 8.2.3, 8.3.1 · Velora TM-006 / SR-003 / ST-003 | Server-side role gate, owner-scoped SQL, field allowlisting. Customer boundary and admin transition tests exercise permitted and denied operations. |
| ASVS v5.0.0 7.2.1, 7.2.4 · Velora TM-001 / SR-007 / ST-007 | Server validates and rotates tokens. Tests cover expiry, login rotation, logout replay and cookie settings. Secure on loopback HTTP is an explicit gap against the portfolio target. |
| ASVS v5.0.0 3.3.2, 3.3.4, 3.5.1 | SameSite and HttpOnly attributes and session-bound form tokens. Tests reject missing and foreign tokens on all four write operations. |
| Velora TM-004 / SR-001 and TM-007 / SR-002 | Bound SQL parameters and Jinja HTML escaping continue into profile and order views. The profile test renders a name containing an ampersand. |
| Velora TM-008 / SR-004 | This milestone implements password authentication. The modeled MFA requirement remains open. |

These mappings cover selected controls. Production assurance would require additional work, including TLS verification, authentication abuse controls and MFA. [ASVS authorization](https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x17-V8-Authorization.md) · [Session management](https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x16-V7-Session-Management.md) · [Web frontend security](https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x12-V3-Web-Frontend-Security.md) · [Velora security requirements](https://github.com/Adeconcept/Velora-GmbH/blob/project/Application-threat-model-and-secure-SDLC/Registers/Security-requirements.csv)
