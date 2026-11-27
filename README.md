# Velora Secure Commerce

A local Flask storefront for practicing application security engineering. Milestone 2 adds password login, editable profiles, customer-owned order history and an administrator fulfillment queue to the accepted product catalog.

[Authorization matrix and design](docs/access-control.md) · [Catalog architecture](docs/architecture.md) · [Verification record](docs/verification.md) · [Working conventions](AGENTS.md)

## Run on macOS

Use Python 3.12 with pip. From the repository root, run:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m flask --app velora init-db
python -m flask --app velora seed-demo
python -m flask --app velora seed-accounts
python -m pytest -q
python -m flask --app velora run --host 127.0.0.1 --port 5050
```

If Python 3.12 is installed outside your PATH, substitute the full interpreter path in the first command. Use Control-C to stop the server. Initialization and seeding can be repeated. Your local catalog lives in the Git-ignored instance directory. Tests use temporary databases.

## Review the account flows

On an existing Milestone 1 checkout, run the three Flask setup commands above in order and restart the local server. The schema update adds tables. Product rows and prices are preserved. The account seed prompts for separate local demo passwords (15–128 characters) with hidden input. Use synthetic credentials and keep them in your local password manager. A repeat seed preserves existing password hashes, profile edits and fulfillment status.

1. Select **My account** and sign in as `avery@example.test`. Change the display name and open **My orders**. Order VC-1001 contains two notebooks.
2. Return through **My account**, sign out, and sign in as `morgan@example.test`. Morgan sees VC-1002. The automated suite checks that each customer's detail page is private.
3. Sign in as `ops@example.test`, open **Manage fulfillment**, and mark VC-1001 shipped. Sign back in as Avery to see the updated status.

## Review the catalog

Open [the local catalog](http://127.0.0.1:5050/). Search for **notebook**, open **Field Notebook**, and check the €8.50 price and VL-101 SKU. Follow **Product catalog**, search for **linen**, and use **Show all products** to return to the full list.

Read the index route in `velora/catalog.py` alongside `test_search` and `test_html_contexts` in `tests/test_catalog.py`. The first connects search behavior to SQL parameter binding. The second checks how database values and the query appear in the rendered HTML.

## Repository guide

- `velora/` contains the Flask factory, catalog routes, SQLite connection lifecycle and schema, templates, and CSS.
- `tests/` exercises the application through its Flask HTTP and CLI interfaces.
- `docs/` explains the design, planned roles, evidence and limits.

The repository publishes source and local verification evidence. Run the application on loopback. Deployment and the DevSecOps pipeline are outside this milestone.
