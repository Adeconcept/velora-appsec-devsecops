# Working on Velora Secure Commerce

Build a lightweight Flask, SQLite and Jinja2 portfolio application that makes each security decision traceable to code and evidence. Treat Adeconcept/Velora-GmbH as read-only reference material.

- Work one reviewed milestone at a time. Milestone 1 is accepted. Milestone 2 covers password sessions, profiles, owned orders and fulfillment. Open a PR for review before merging. Docker, GitHub Actions, Snyk and ZAP belong to later work.
- Use synthetic data only. Keep credentials, databases, virtual environments and machine-specific settings out of Git. Use environment-provided secrets when a feature requires them.
- Keep the local server on loopback. Isolate and label any future deliberately vulnerable demonstrations and keep them off public deployments.
- Bind SQL values, retain HTML template autoescaping and add tests at the HTTP or CLI boundary for new behavior. Use temporary databases for tests.
- Run the README setup and test commands after changes. Record the interpreter, revision, command, outcome and limitations. Claim verification only for observed behavior. Keep recommendations and planned controls explicitly identified.
- Explain changes in terms a learner can demonstrate and defend. Preserve the simple native development path on an 8 GB Apple Silicon Mac.
