# Velora Secure Commerce

A local Flask storefront for practicing application security engineering. Milestone 1 implements a searchable catalog with three synthetic stationery products. A reviewer can follow a single search from an HTML form through a bound SQLite query to escaped HTML.

[Architecture and control decisions](docs/architecture.md) · [Verification record](docs/verification.md) · [Working conventions](AGENTS.md)

## Run on macOS

Use Python 3.12 with pip. From the repository root, run:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m flask --app velora init-db
python -m flask --app velora seed-demo
python -m pytest -q
python -m flask --app velora run --host 127.0.0.1 --port 5050
```

If Python 3.12 is installed outside your PATH, substitute the full interpreter path in the first command. Use Control-C to stop the server. Initialization and seeding can be repeated. Your local catalog lives in the Git-ignored instance directory. Tests use temporary databases.

## Review in two minutes

Open [the local catalog](http://127.0.0.1:5050/). Search for **notebook**, open **Field Notebook**, and check the €8.50 price and VL-101 SKU. Follow **Product catalog**, search for **linen**, and use **Show all products** to return to the full list.

Read the index route in `velora/catalog.py` alongside `test_search` and `test_html_contexts` in `tests/test_catalog.py`. The first connects search behavior to SQL parameter binding. The second checks how database values and the query appear in the rendered HTML.

## Repository guide

- `velora/` contains the Flask factory, catalog routes, SQLite connection lifecycle and schema, templates, and CSS.
- `tests/` exercises the application through its Flask HTTP and CLI interfaces.
- `docs/` explains the design, planned roles, evidence and limits.

The first milestone ends at catalog review. Customer accounts, profile and order management, administrative access, containers and security automation are future work.
