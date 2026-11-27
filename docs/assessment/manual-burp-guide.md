# Analyst worksheet · local storefront

Run this on a disposable checkout. The analyst owns all manual results. Use the [test plan](test-plan.md) for expected behavior and the [evidence conventions](../../evidence/README.md) before exporting anything.

## Bring up a fresh instance

Keep Firefox, Burp and Flask inside the **same Kali VM**. Kali's 127.0.0.1 belongs to Kali. A Flask process bound to macOS loopback cannot be reached at that address from Kali. Use one Flask process without a reloader so the local rate budgets have a stable lifetime.

```sh
assessment_dir=$(mktemp -d)
git clone https://github.com/Adeconcept/velora-appsec-devsecops.git "$assessment_dir/storefront"
cd "$assessment_dir/storefront"
git switch --detach b01e77e5e0af69fb2fe58a38cd14dc22ac7e8d5a
python3 --version
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip check
python -m pytest -q
python -m flask --app velora init-db
python -m flask --app velora seed-demo
python -m flask --app velora seed-accounts
VELORA_HTTPS=0 python -m flask --app velora --no-debug run --no-reload --host 127.0.0.1 --port 5050
```

The verified interpreter is Python 3.12.14 on macOS arm64. Kali compatibility is pending your setup check. Record the interpreter and test result. If venv creation, dependency installation or the baseline suite fails, keep that error and use a fresh Mac checkout with Python 3.12 and Burp plus its browser on the Mac; keep both listeners on Mac loopback. Keep the worksheet open separately since the tested baseline predates these documents.

Choose distinct synthetic passwords at the hidden prompts for avery@example.test, morgan@example.test and ops@example.test. Use separate browser profiles or isolated sessions labeled Avery, Morgan and Ops. Only these synthetic accounts belong in this assessment.

Set Burp's local proxy listener to 127.0.0.1:8080. Use Burp's browser or a dedicated Firefox profile using that HTTP proxy; if Firefox bypasses localhost, use Burp's browser. Limit scope to http://127.0.0.1:5050. Open the catalog and confirm an entry for GET / in HTTP history before recording anything. No TLS certificate installation is needed for this HTTP instance.

## Capture sequence

Use regular application traffic for the browser observations. The existing regression suite supplies the negative-control comparisons below. Record automated corroboration separately. Leave any manual variant you did not observe as NOT TESTED.

1. **Authorization (AS-001–004).** In a signed-out context open /profile. Sign in as Avery, open My orders and the notebook detail. Repeat in Morgan's own context for the tray order. Capture each legitimate reference, displayed amount, role and status. Open the fulfillment queue as Ops and note the available fields. Save Avery’s name once, return to the profile and verify the other identity retains its own name. Use the ownership, field-permission and role tests below as supporting evidence for the denied variants.
2. **Authentication and sessions (AS-005,009,012).** Track whether the cookie changes after sign-in using labels A and B. Record the flags and no-store header, without copying the values. Sign out and navigate afresh to /profile. In a fresh signed-in session leave all account pages inactive for at least 15 minutes, then request My orders. Record elapsed time and the fresh HTTP status. For a low-cost abuse check, make one incorrect synthetic login followed by one legitimate login; record the generic failure and subsequent result. Use the deterministic budget tests for threshold and recovery evidence. If you do not wait eight hours, record absolute expiry as automated-only.
3. **Input and error handling (AS-007,008,011).** Search separately for notebook, %, and a missing product name. Record the matching rows. Use an inert marker such as `Paper & "Ink"` in search and your own display name. Compare the raw HTML attribute with the visible value on the page. Restore the original display name. Observe the response for an absent product and check for diagnostic details. Note that literal behavior and escaping support specific input contexts only.
4. **Request integrity and fulfillment (AS-006,010).** Capture one legitimate edit and note where the hidden form token is carried; redact it. Confirm VC-1001 is processing in both Ops and Avery’s views. Use Ops to mark it shipped once, then refresh Avery’s detail. Capture the POST response before the redirect, the resulting state and the absence of a second action in the queue. Use the existing CSRF, repeated-transition and concurrency tests for the denied cases. A missing button is UI evidence only.

For the paired allow/deny comparisons on this exact baseline, run in a second terminal from the same checkout:

```sh
. .venv/bin/activate
python -m pytest -v tests/test_accounts.py -k 'customer_boundary or admin_scope or csrf_for_all or rotation_and_revocation or expiration or attempt_budget or allocation_budget or concurrent_ship'
python -m pytest -v tests/test_catalog.py -k 'search or html_contexts'
```

## Analyst return sheet

Use E01 for the first sanitized manual observation in a case, E02 for its comparison. Add rows for partial or conflicting observations.

|Case|Role / method / route|Expected behavior|Observed status and relevant data or state|Evidence ID or file|Interpretation|
|---|---|---|---|---|---|
|AS-001|Guest / profile|401||||
|AS-002|Avery and Morgan / order reads|Own order visible||||
|AS-003|Ops / queue|Queue visible within role policy||||
|AS-004|Customer / profile edit|Only own name changes||||
|AS-005|Customer / session lifecycle|Rotation and loss of access on termination||||
|AS-006|Permitted actor / forms|Session-bound tokens required||||
|AS-007|Guest / search|Literal matching||||
|AS-008|Customer / search and profile|Punctuation remains text||||
|AS-009|Guest / login|Generic failure and recovery within budget||||
|AS-010|Ops / ship|One persisted transition||||
|AS-011|Guest / product lookup|404 without internals||||
|AS-012|Guest and customer / headers|Documented cookie and cache settings||||

Stop Flask with Ctrl-C and close the temporary Burp project. For a clean reset, retain sanitized evidence outside the checkout and repeat setup in a **new** temporary directory. Reseeding an existing database preserves shipped orders. Return the completed rows and sanitized excerpts. Include any skipped case and why.
