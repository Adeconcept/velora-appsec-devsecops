# Milestone 1 verification

**Tested revision** `8e13172` on 2026-11-27. Apple Silicon macOS, native arm64, Python 3.12.14. The interpreter came from a bundled runtime outside PATH. Tests and the development server ran inside a local virtual environment.

| Check | Observation |
|---|---|
| Reproducible setup | Cloned the implementation commit to a fresh directory, created a new venv, installed requirements-dev.txt from PyPI, and ran pip check. Output included “No broken requirements found.” |
| Database setup | Both Flask CLI commands exited successfully in the fresh clone. The repeat-setup test also retained an edited price and exactly three rows. |
| Automated checks | python -m pytest -q reported **14 passed in 0.15s** in the clean clone. Coverage includes literal search, length boundaries, detail lookup, prices, output escaping and database constraints. |
| Live HTTP walkthrough | Used curl against the Flask server on 127.0.0.1:5050. The catalog returned Field Notebook, Pocket Ruler and Studio Tray. Searching notebook returned one detail link. Following /products/1 returned €8.50 and VL-101. Searching linen returned “No products found.” |

## Source review

Reviewed both SELECT statements in velora/catalog.py. Search and detail lookup each use a fixed statement with a bound value. Reviewed the setup commands in velora/db.py. Initialization reads packaged SQL, and the seed insertion binds all four row values. The templates use standard escaped interpolation for text and a quoted attribute for the search term. The rendering test checks the actual response with synthetic angle brackets, ampersands and quotes.

These observations support the current catalog slice of SR-001. The HTTP walkthrough inspected response HTML. Browser appearance, assistive technology behavior, production deployment and broader security assurance were outside this verification. Access-control checks become relevant when private routes are implemented.

## Milestone 2 · Authentication and authorization

**Tested implementation** `0b3fb28`, native arm64 macOS, Python 3.12.14. Before the change, the accepted main branch passed 14 catalog tests in 0.18s. A fresh feature-branch clone with a new venv installed the pinned dependencies and passed pip check.

| Check | Recorded result |
|---|---|
| Upgrade existing data | Initialized and seeded a catalog at revision 4c0803e, changed VL-101 to 925 cents, then checked out 0b3fb28 and reran init-db and seed-demo. After two seed-accounts runs the price was 925, users numbered three, orders numbered two, and SQLite foreign_key_check returned no rows. |
| Complete suite | `python -m pytest -q` reported **33 passed in 1.54s** in the fresh clone. This includes all 14 original tests and 19 new cases. |
| Identity and session checks | Exercised valid and failed login, role-restricted routes, server-side termination, old-cookie replay, expiry, cookie attributes and stored password verification. |
| Object and field checks | Two seeded customers could read their own order totals. Cross-owner details returned 404. Profile updates applied to the current identity. Customer attempts to ship an order returned 403. The admin transition succeeded once and returned 409 on repetition. |
| Form integrity | Missing tokens and tokens from another session returned 400 on login, profile update, shipping and logout. Tests checked the resulting profile, order and session state. |

HTTP tests used Flask's test client. The HTTPS scenario inspected the Secure cookie attribute. Browser enforcement, network TLS and production operation were outside this run. See the [authorization matrix and requirements mapping](access-control.md) for the scope of each claim.
