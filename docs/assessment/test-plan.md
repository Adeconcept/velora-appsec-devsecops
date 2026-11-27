# Verification plan · analyst cases

Cases cover selected controls on the merged baseline. The manual disposition remains NOT TESTED until the analyst returns observations. The named pytest functions have separate automated evidence. Use PASS for a verified expectation, FAIL for an evidenced violation, INCONCLUSIVE for insufficient or conflicting evidence, NOT TESTED for pending work, and NOT APPLICABLE when the precondition is outside scope. Record subchecks separately where a case has partial coverage. [Baseline transcript](../../evidence/automated/baseline.txt) · [ASVS mapping](asvs-traceability.csv) · [WSTG v4.2 methods](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/)

## AS-001 · Anonymous access

- **Target and preconditions.** Private routes / guest. Signed-out context.
- **Control and method.** Default-deny role gate. Observe a fresh profile read; consult logged-out method matrix.
- **Expected.** 401 and no account data.
- **Trace.** ASVS 8.2.1 8.3.1. WSTG 4.5 Authorization. Source under `velora/`: access.check_access. Baseline: `test_logged_out_access`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-001-E01.

## AS-002 · Customer ownership

- **Target and preconditions.** GET /orders and detail / customer. Both seeded owners.
- **Control and method.** Session owner in list and detail SQL. Compare legitimate owner views; inspect the paired cross-owner regression.
- **Expected.** Only own rows; regression returns 404 for unrelated and absent rows.
- **Trace.** ASVS 8.2.2 8.3.1. WSTG 4.5 Authorization. Source under `velora/`: accounts.orders, order. Baseline: `test_customer_boundary`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-002-E01.

## AS-003 · Admin authorization

- **Target and preconditions.** Admin queue and ship / customer, admin. Separate authenticated contexts.
- **Control and method.** Database role policy. Observe operator queue and customer navigation; inspect direct-denial regression.
- **Expected.** Operator allowed; customer requests denied 403 with order unchanged.
- **Trace.** ASVS 8.2.1 8.3.1. WSTG 4.5 Authorization. Source under `velora/`: access.check_access; accounts.fulfillment, ship. Baseline: `test_admin_scope_and_transition; test_live_role_demotion; test_customer_boundary`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-003-E01.

## AS-004 · Field permissions

- **Target and preconditions.** POST /profile and ship / customer, admin. Record original role, email, order and price.
- **Control and method.** Explicit update columns. Edit own name; compare protected-field assertions before and after.
- **Expected.** Only name or permitted order status changes.
- **Trace.** ASVS 8.2.3. WSTG 4.5 Authorization. Source under `velora/`: accounts.profile, ship. Baseline: `test_customer_boundary; test_admin_scope_and_transition`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-004-E01.

## AS-005 · Session lifecycle

- **Target and preconditions.** Login, profile, logout / customer. Fresh browser session and clock.
- **Control and method.** Password check, token rotation, expiry and revocation. Observe cookie replacement and logout; compare idle and stale-token test assertions.
- **Expected.** Successful login rotates session; invalid credentials fail; stale sessions rejected.
- **Trace.** ASVS 7.2.1 7.2.4 7.3.1 7.3.2 7.4.1. WSTG 4.4 Authentication; 4.6 Session management. Source under `velora/`: access.login, start_session, logout, check_access. Baseline: `test_failed_login; test_session_rotation_and_revocation; test_expiration`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-005-E01.

## AS-006 · CSRF

- **Target and preconditions.** All account POSTs / permitted role. Valid session and forms.
- **Control and method.** Per-session comparison. Observe ordinary forms; inspect missing and foreign-token regression for all writes.
- **Expected.** Valid forms work; invalid tokens return 400 and leave state unchanged.
- **Trace.** ASVS 3.5.1. WSTG 4.6 Session management. Source under `velora/`: access.check_access; templates/csrf.html. Baseline: `test_csrf_for_all_writes`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-006-E01.

## AS-007 · SQL parameterization

- **Target and preconditions.** GET / / all. Seeded English catalog.
- **Control and method.** Bound parameters and fixed SQL. Compare notebook, percent sign and an absent name; inspect query construction.
- **Expected.** Notebook matches; literal % and absent name have zero matches.
- **Trace.** ASVS 1.2.4. WSTG 4.7 Input validation. Source under `velora/`: catalog.index; db.connection. Baseline: `test_search`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-007-E01.

## AS-008 · Contextual escaping

- **Target and preconditions.** GET / and POST/GET /profile / customer. Capture original name.
- **Control and method.** Jinja text and quoted attributes. Use inert punctuation; compare displayed value with encoded HTML.
- **Expected.** Characters remain literal in the same field; no new markup.
- **Trace.** ASVS 1.2.1. WSTG 4.7 Input validation. Source under `velora/`: catalog.index; accounts.profile; templates/catalog.html, profile.html. Baseline: `test_html_contexts; test_customer_boundary`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-008-E01.

## AS-009 · Login abuse controls

- **Target and preconditions.** GET/POST /login / guest. Fresh process or known window.
- **Control and method.** Independent admission budgets. Observe one failed sign-in and recovery to valid login; use clock-controlled tests for thresholds.
- **Expected.** Generic failure; budgets enforce 10 checks and 20 allocations per rolling minute, then recover.
- **Trace.** ASVS 6.1.1 6.3.1. WSTG 4.4 Authentication. Source under `velora/`: access.check_access, login; throttle.MinuteBudget.reserve. Baseline: `test_login_attempt_budget; test_anonymous_allocation_budget`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-009-E01.

## AS-010 · State transition

- **Target and preconditions.** POST /admin/orders/{id}/ship / admin. Processing fixture with owner view.
- **Control and method.** Conditional UPDATE on current status. Observe one shipment and owner view; consult duplicate and concurrent assertions.
- **Expected.** One transition persists; repeat receives 409.
- **Trace.** ASVS 2.3.1. WSTG 4.10 Business logic. Source under `velora/`: accounts.ship. Baseline: `test_admin_scope_and_transition; test_two_concurrent_ship_requests`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-010-E01.

## AS-011 · Errors and validation

- **Target and preconditions.** Catalog and order detail / guest, customer. Debug off.
- **Control and method.** Query limits and 404 handling. Compare an absent product and invalid search length; inspect returned body.
- **Expected.** 404 or 400 as applicable; no traceback, query or private data.
- **Trace.** ASVS 2.2.1 16.5.1. WSTG 4.8 Error handling. Source under `velora/`: catalog.detail, index; accounts.OrderIDConverter, order. Baseline: `test_detail; test_search_limit; test_unsupported_order_identifiers`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-011-E01.

## AS-012 · Configuration

- **Target and preconditions.** Account headers and public static CSS / all. Loopback HTTP, debug off.
- **Control and method.** Cookie flags and cache policy. Observe headers and actual listener; compare HTTPS-mode header unit test.
- **Expected.** HttpOnly and SameSite=Strict; account response no-store; local Secure exception documented.
- **Trace.** ASVS 3.3.2 3.3.4. WSTG 4.2 Configuration; 4.6 Session management. Source under `velora/`: access.private_headers; __init__.create_app. Baseline: `test_https_cookie_configuration; test_session_rotation_and_revocation`.
- **Observed / disposition.** NOT TESTED / NOT TESTED. Planned analyst evidence: AS-012-E01.
