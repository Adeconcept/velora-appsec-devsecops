# Abuse cases and decision evidence

|Claim to evaluate|Relevant actor and comparison|Evidence needed for a decision|
|---|---|---|
|A valid account grants visibility into unrelated purchases|Compare seeded customer views and the owner-scoped regression (AS-002)|Record visible references, principal and response status. A shorter response cannot establish disclosure.|
|A form author can choose protected fields or start fulfillment|Compare the customer and operator policies with the rows persisted by the field and transition tests (AS-003/004/010)|Check owner, price, role and shipment state before and after. A redirect alone cannot establish a write.|
|Closing a session leaves private data accessible|Compare a fresh authorized read, logout and a new server request (AS-005)|Distinguish cached browser history from a fresh private response. Record the expiry clock and any intervening activity.|
|An unintended form submission changes state|Compare a valid edit with the missing/foreign-token regression (AS-006)|Require a rejected response and an unchanged value.|
|Input crosses an interpreter boundary|Compare literal search and profile text with bound SQL and the rendered HTML (AS-007/008)|Capture expected rows, markup context and visible text. Search behavior alone cannot prove every query safe.|
|Login capacity is exhausted|Review the verification and allocation budgets separately (AS-009)|Controlled-clock suite measures the cap and recovery. Throughput and multi-worker behavior remain open.|
