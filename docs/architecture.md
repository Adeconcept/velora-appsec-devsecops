# Catalog architecture and security decisions

The storefront implements a local slice of AST-001 (customer application) and AST-002 (customer and order database). The earlier threat model links catalog threat TM-004 to requirement SR-001 and planned verification ST-001. Its web penetration test records results from separate PortSwigger labs. This repository supplies implementation evidence for its own catalog. [Threat model and secure SDLC](https://github.com/Adeconcept/Velora-GmbH/tree/project/Application-threat-model-and-secure-SDLC) · [Web penetration test](https://github.com/Adeconcept/Velora-GmbH/tree/project/Web-app-Penetration-testing)

## Request path

1. A visitor submits GET / with an optional q parameter. Flask trims whitespace and returns HTTP 400 if the remaining term exceeds 100 characters.
2. The route binds the term to a fixed SQL statement. SQLite instr searches for the literal substring, so punctuation such as % has its ordinary meaning. SQLite lower handles ASCII case folding, sufficient for the seeded English names. An empty term returns the whole catalog.
3. Flask passes rows to an HTML template. Jinja escapes values when rendering product text and the quoted search field. Validation limits the size of input. Parameter binding and output escaping protect their respective interpreter boundaries.
4. GET /products/<id> binds the integer ID to a separate lookup. An absent product returns 404. Product IDs designate public catalog entries.
5. Flask closes the request's SQLite connection during teardown. A single process and a file database keep setup small on the M1. Only the two local CLI commands write application data.

## Entities and ownership

| Entity | State | Fields and constraints |
|---|---|---|
| Product | Implemented | Integer primary key, unique SKU, required name and description, nonnegative integer euro cents |
| User | Planned | Unique email, password hash, display name, server-assigned customer or administrator role |
| Order | Planned | Primary key, owning user reference, creation time, fulfillment status |
| Order item | Planned | Order and product references, quantity, unit price in cents at purchase |

A visitor can browse, search and open products. The planned customer role can authenticate, edit its own profile, place orders and read its own orders. Each private lookup must check the authenticated principal's ownership on the server. The planned administrator can review orders and change fulfillment status after a server-side role check. Price snapshots keep historical totals stable when catalog prices change.

## Milestone review

The catalog uses no session, account data or signing secret. Loopback development with debugging off is the intended runtime. The evidence record covers the two HTTP routes and the local setup commands. Review accounts and ownership as a separate milestone before adding private data.
