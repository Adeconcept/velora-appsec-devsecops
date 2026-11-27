# Milestone 2 · Who can do what?

| HTTP resource | Signed out | Customer | Administrator |
|---|---|---|---|
| GET catalog and product | Browse | Browse | Browse |
| GET /login, POST /login | Obtain a form, authenticate within the local budgets below | Return to own profile | Return to own profile |
| GET /profile, POST /profile | 401 | Read own email and name, edit own name | Same, for own account |
| GET /orders | 401 | List own references, dates and statuses | 403 |
| GET /orders/&lt;id&gt; | 401 | Read own order and lines. Any other ID returns 404 | 403 |
| GET /admin/orders | 401 | 403 | List fulfillment references, dates and statuses across accounts |
| POST /admin/orders/&lt;id&gt;/ship | 401 | 403 | Move one processing order to shipped. Other submitted fields are ignored. A repeat returns 409 |
| POST /logout | 401 | Revoke current session | Revoke current session |

Every permitted POST requires a CSRF token tied to the current session, including the anonymous login form. Missing or unrelated tokens return 400. Each endpoint on the account blueprint needs an explicit entry in the role policy. A missing entry denies access.

The server reads the current role on each private request. After a committed administrator demotion, the next request in the existing session follows customer permissions. Expired and revoked sessions have signed-out permissions. Unsupported order identifiers return 404.

## Why checking ownership matters

Authentication tells Flask who is making a request. A signed-in customer still has no right to another customer's order. Looking up a private order using only its ID would allow an authenticated user who learns another ID to read purchases and amounts. A dropdown, hidden link or unpredictable reference cannot enforce that boundary.

The detail query binds the requested order ID and the current account ID together. Flask obtains the account ID from the server-side session. A missing match ends the request before any line items are read. Both the list and the detail route apply ownership checks. The profile route uses the session owner directly and accepts one editable field. The admin action reads the role from SQLite and performs a conditional update of one status field. The owner, amount and order lines never come from that form.

In the two-customer test, each identity reads its own line total and receives the same 404 for an unrelated order and a missing order. A second test records that a permitted fulfillment change becomes visible to the owner. These are tests of the implemented policy. The earlier penetration-test findings belong to the separate training labs.

## Passwords, sessions and request integrity

- The local seed prompts for each password, hashes it with Werkzeug's salted scrypt implementation and stores only the encoded hash. Login uses the library verifier and a generic failure response. An unknown email still incurs a password-hash check.
- A browser receives a random 32-byte opaque token. SQLite holds its SHA-256 digest, a separate random CSRF token, expiry and the user reference. Hashing a high-entropy lookup token is inexpensive. A human password needs the more expensive salted password hash. Each private request reads the current account role from the database.
- Successful login replaces the anonymous session and its CSRF token. Logout deletes the database row. Sessions expire after 15 minutes of account inactivity or eight hours from creation. Public catalog views do not refresh the idle window. Expired rows are pruned on session creation.
- Each account form submits a synchronizer token. The server checks it with a constant-time comparison before accepting the POST. Private responses request no storage. Cookies are host-only, HttpOnly, and SameSite=Strict. Local HTTP uses a cookie without Secure. Set VELORA_HTTPS=1 when testing with an actual HTTPS listener. This flag changes the cookie attribute and does not configure TLS.

## Local authentication abuse controls

Every verified password attempt incurs a memory-hard scrypt operation, including attempts for unknown users. Fresh login forms also allocate SQLite rows. Session expiry bounds the lifetime of a row but cannot limit how fast rows are created.

The single-process loopback app therefore admits **10 password checks and 20 fresh anonymous sessions per rolling 60 seconds**, in independent, lock-protected budgets. Successful and failed password checks both count. Refreshing a form with a valid session reuses its CSRF token. An exhausted budget returns 429 with Retry-After before the corresponding hash or allocation. These are local demo defaults. A shared budget gives this one-process app bounded memory without retaining IP addresses or account identifiers.

Any local client can consume the shared allowance and temporarily delay another login. Restarting the process resets the counters. Ordinary requests and session lookups can still consume resources. For a shared service, measure legitimate traffic, combine per-account and per-source limits with an aggregate capacity limit, coordinate counters across workers, and monitor denials. Select source identities only after configuring the proxy trust boundary. MFA remains outstanding under SR-004.

## Fulfillment concurrency

The status predicate and the write execute as one SQLite UPDATE. Two sessions requesting shipment of the same processing order compete for the same transition. The successful request returns 303. A later writer sees the existing shipped row and returns 409. The test releases two Flask clients together against one on-disk temporary database, using independent request connections. Thread scheduling and SQLite determine when each write runs. This checks the observable outcome for two local requests. Sustained lock contention, multi-host operation and external shipping side effects require separate evaluation.

## Production configuration requirements (future work)

The supported runtime is loopback HTTP with debugging off. A production review would require a production WSGI server, disabled debugger and reloader, bounded request sizes and worker timeouts, and restricted access to the database file. Terminate HTTPS with a valid certificate, enforce HTTPS and set VELORA_HTTPS=1. Verify actual browser transport and cookie behavior through the deployed path. The existing cookie test inspects a response header.

Configure Flask TRUSTED_HOSTS with the service's explicit hostnames. If a reverse proxy is introduced, restrict direct access to the backend, have the trusted proxy replace client-supplied forwarding headers and configure ProxyFix only for the headers and hop counts that match that topology. The local app needs no proxy middleware. [Flask security considerations](https://flask.palletsprojects.com/en/stable/web-security/) · [Flask reverse proxy guidance](https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/)

## Traceability and limits

| Source | Local implementation and evidence |
|---|---|
| ASVS v5.0.0 8.2.2, 8.2.3, 8.3.1 · Velora TM-006 / SR-003 / ST-003 | Server-side role gate, owner-scoped SQL, field allowlisting. Customer boundary and admin transition tests exercise permitted and denied operations. |
| ASVS v5.0.0 7.2.1, 7.2.4 · Velora TM-001 / SR-007 / ST-007 | Server validates and rotates tokens. Tests cover expiry, login rotation, logout replay and cookie settings. Secure on loopback HTTP is an explicit gap against the portfolio target. |
| ASVS v5.0.0 3.3.2, 3.3.4, 3.5.1 | SameSite and HttpOnly attributes and session-bound form tokens. Tests reject missing and foreign tokens on all four write operations. |
| Velora TM-004 / SR-001 and TM-007 / SR-002 | Bound SQL parameters and Jinja HTML escaping continue into profile and order views. The profile test renders a name containing an ampersand. |
| Velora TM-008 / SR-004 | This milestone implements password authentication. The modeled MFA requirement remains open. |

These mappings cover selected controls. Production assurance would require additional work, including TLS verification, distributed abuse protection and MFA. [ASVS authorization](https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x17-V8-Authorization.md) · [Session management](https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x16-V7-Session-Management.md) · [Web frontend security](https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x12-V3-Web-Frontend-Security.md) · [Velora security requirements](https://github.com/Adeconcept/Velora-GmbH/blob/project/Application-threat-model-and-secure-SDLC/Registers/Security-requirements.csv)
