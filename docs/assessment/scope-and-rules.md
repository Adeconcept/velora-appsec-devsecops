# Engagement scope · checkpoint 1

**Decision sought:** Does the current local storefront enforce its documented identity, order and fulfillment boundaries? The unit of assessment is the application at `b01e77e5e0af69fb2fe58a38cd14dc22ac7e8d5a`, the verified merge of PR #1 into main. The assessment branch starts at that commit.

On 27 November 2026, the existing suite returned **38 passed in 2.69s** on Darwin arm64, Python 3.12.14. A verbose second run records the individual cases. Both runs used Flask test clients and temporary SQLite files. The CLI route inventory contained ten rules including static files. [Run transcript](../../evidence/automated/baseline.txt)

The practitioner owns the manual assessment on a disposable, synthetic, loopback-only instance. Observe catalog, account, session, order and fulfillment traffic. Preserve existing databases. Record redacted excerpts outside the raw proxy project. Stop on unexpected data or state changes and retain the relevant observation. Production infrastructure, payments, cloud, scanner runs and deployment assurance are outside the engagement.

Checkpoint 1 supplies the inventory, source review, threat analysis, planned cases and worksheet. Each manual case remains NOT TESTED. Evidence adjudication, finding severity, remediation decisions and final reports follow the analyst handoff.
