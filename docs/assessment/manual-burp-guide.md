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

## Six manual comparisons

Record the tested SHA, OS, Python, Burp and browser versions, time zone, and synthetic account once per run. Use an isolated session for each account. Record the **first HTTP status before following a redirect** and use a fresh GET for the state check. The expectations below come from the reviewed implementation. All six manual cases start as **NOT TESTED**.

1. **AS-002 · Order ownership.** In Avery's session, capture GET of the order detail linked from My orders (VC-1001, two notebooks, €17.00). In Morgan's session, record the legitimate detail URL for VC-1002 (studio tray, €24.00). Both owner reads should return 200. For the comparison, keep Avery's session and change only the order selector in Avery's GET to Morgan's observed selector. Expect 404 with no Morgan reference, items or total. Refresh each owner's list and detail in its own session and verify the original ownership and amounts. Save the legitimate pair under AS-002-E01 and the denied response plus state check under AS-002-E02.
2. **AS-003 · Fulfillment permission.** As Ops, GET /admin/orders and record VC-1001's processing status and the action URL on its shipment form. Keep this order processing for the test. As Avery, GET the same queue and submit a POST to that shipment URL with Avery's own valid session and form token. Expect 403 for both customer requests. A 400 alone does not establish role enforcement. Refresh Ops's queue and Avery's order detail; both should still show processing. Use AS-003-E01 for the authorized queue and AS-003-E02 for both denials and the fresh reads.
3. **AS-004 · Protected form fields.** As Avery, save an ordinary display name with POST /profile. Expect 303 and verify the new value with GET /profile. Repeat the permitted edit with a distinct name and additional role and ownership claims (role=admin and owner_id set to Morgan's fixture ID). Keep Avery's session and valid CSRF token. Expect 303 because the permitted name change succeeds. Confirm the new name persists for Avery, Morgan's profile is unchanged, Avery still receives 403 for the admin queue, and each original order remains visible to its owner. Restore Avery's original name. Save AS-004-E01 for the ordinary edit and AS-004-E02 for the second edit and postconditions.
4. **AS-005 · Logout revocation.** As Avery, retain a successful GET /profile in the temporary proxy project. Sign out normally with POST /logout and record the expected 303 and cookie expiration. Repeat the retained profile read with its original session context, before signing back in. Expect 401 and no profile data. A fresh browser profile read should also require authentication. Record the retained-request response separately from the new browser request: only the former checks server-side revocation of the old session. Use AS-005-E01 for the authorized read and logout and AS-005-E02 for the post-logout reads. Redact every cookie value.
5. **AS-006 · Form integrity.** Sign back in as Avery. With a valid token, save a known baseline name on POST /profile and confirm it persists. Prepare another edit with a different candidate name. In two separate requests keep the session, name and route constant: omit the csrf field, then supply the literal invalid value “invalid”. Expect 400 each time. After **each** response, GET /profile and verify the baseline name persists. Restore the original name. Save AS-006-E01 for the valid control, AS-006-E02 for missing, AS-006-E03 for invalid.
6. **AS-008 · HTML output context.** As Avery, search normally with GET /?q=notebook and record an ordinary display-name save. Then use the inert text `<em>Velora</em> & "Ink"` as the search term and as Avery's display name using the supported forms. Expect 200 for search, 303 for save and 200 on profile reload. Compare the raw HTML with the browser field value: delimiters should be escaped in the quoted attribute and the complete original text should be visible as the value. Inspect the DOM for any marker-created element. Repeat the profile GET to confirm persistence, then restore the original name. Save AS-008-E01 for the ordinary inputs and AS-008-E02 for encoded source, field value and reload. This checks the sampled HTML contexts only.

## Analyst return sheet

E01 records the baseline in each case. Use the comparison IDs below for the associated contrasts. Enter filenames only after sanitizing the artifacts. Leave unobserved variants NOT TESTED and split mixed outcomes across rows.

|Comparison ID|Expected outcome|Actual HTTP status|Relevant response excerpt|Persisted state / fresh read|Evidence filename(s)|Interpretation / disposition|
|---|---|---|---|---|---|---|
|AS-002-E02|Avery receives 404 for Morgan's order; own details intact||||||
|AS-003-E02|Customer queue and shipment return 403; processing persists||||||
|AS-004-E02|303; only Avery's display name changes||||||
|AS-005-E02|Old session and fresh signed-out read return 401||||||
|AS-006-E02|Missing token returns 400; baseline name persists||||||
|AS-006-E03|Invalid token returns 400; baseline name persists||||||
|AS-008-E02|Literal value survives rendering and profile reload||||||

**Evidence boundaries.** A passing automated test can corroborate a manual observation. It cannot populate an empty manual result. The order schema's lack of operator and transition time is a source-review limitation tracked in the [review draft](secure-code-review.md). It has no manual finding or severity assigned. Keep the remaining assessment cases and unobserved variants pending in the [full test plan](test-plan.md).

Stop Flask with Ctrl-C and close the temporary Burp project. For a clean reset, retain sanitized evidence outside the checkout and repeat setup in a **new** temporary directory. Reseeding an existing database preserves shipped orders. Return the completed rows and sanitized excerpts. Include any skipped case and why.
