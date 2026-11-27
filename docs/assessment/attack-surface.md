# HTTP surface at the merged baseline

Inventory from Flask's route registry and the handlers. Each GET rule also accepts HEAD. Flask supplies OPTIONS on these rules. The account blueprint hook still runs on matched account requests. HEAD /login has an explicit empty response. Roles below describe normal handler access. [Architecture and data-flow diagram](data-flow.md)

|Route|Method|Identity and roles|Client inputs|Data at boundary|Control|Cases|
|---|---|---|---|---|---|---|
|/|GET|Public, all|q|Search text → catalog SQL and HTML|Trim, 100-character cap, bound literal substring, escaped attribute|007,008,011|
|/products/&lt;product_id&gt;|GET|Public, all|Integer path|ID → product details and price|Integer converter, range guard, bound lookup|007,011|
|/static/&lt;filename&gt;|GET|Public, all|File path|Path → bundled static assets|Framework static directory; current asset catalog.css|012|
|/login|GET|Public, all|Session cookie|Browser → guest session and CSRF form|Session reuse, allocation budget, authenticated redirect|005,009,012|
|/login|POST|Public with form session, all|Email, password, csrf, cookie|Credentials → password hash verification|CSRF, hash-check budget, generic failure, session rotation|005,006,009|
|/logout|POST|Authenticated customer/admin|Cookie, csrf|Bearer → session row|Role gate, CSRF, row deletion and cookie expiry|001,005,006|
|/profile|GET / POST|Authenticated customer/admin|Cookie; POST csrf and display_name|Identity → own email and name|Session-derived user ID, name-only update and length bound, escaping|001,004,006,008|
|/orders|GET|Authenticated customer|Cookie|Identity → order list|Owner ID bound from session|001,002|
|/orders/&lt;order_id&gt;|GET|Authenticated customer|Cookie, numeric path|Selector → private order and lines|Owner and ID in one query before line access|002,011|
|/admin/orders|GET|Authenticated admin|Cookie|Role → cross-customer fulfillment queue|Current database role, selected operational fields|001,003|
|/admin/orders/&lt;order_id&gt;/ship|POST|Authenticated admin|Cookie, path, csrf|Role → order status mutation|Role gate, CSRF, processing-only conditional UPDATE|003,004,006,010|

All account responses receive Cache-Control: no-store through the blueprint hook. Authentication requires an unexpired session joined to a user. Public catalog routes do not use the session. Reproduce the inventory with `python -m flask --app velora routes --all-methods`.
