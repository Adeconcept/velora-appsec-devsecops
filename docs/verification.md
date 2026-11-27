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
