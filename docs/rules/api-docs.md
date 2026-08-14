# API Documentation Rules

Every backend API is documented under `docs/api/`. The code is not the
documentation.

## Placement

`docs/api/` mirrors the backend route layout. One file per resource, named
after it. There is one client, the web app, and there is no API versioning — no
version directories, no version prefixes in paths.

`docs/api/README.md` is the index: it lists every documented resource and links
to it.

## Per-endpoint content

For each endpoint in the file:

- Method and path
- What it does, in one line
- Auth requirement
- Path, query, and body parameters with their types and whether required
- Success response: status code and body shape
- Error responses: status code and when it happens

## Constraints

- Written in English.
- Document the contract, not the implementation.
- The doc changes in the same commit as the endpoint. An endpoint without a doc
  entry is incomplete; a doc entry without an endpoint is a bug.