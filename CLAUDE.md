# Assistant conventions

- Keep tenant identity derived from trusted request context; never mix records
  across organisations.
- Treat external data as untrusted and retain source provenance through retrieval.
- Keep workspace operations read-only unless an explicit approval flow is added.
- Route requests deterministically and return an evidence rejection when retrieved
  sources do not support an answer.
- Add or update focused tests with behavior changes; do not require live services
  for unit tests.
- Keep secrets in environment variables and use `.env.example` only for placeholders
  or local development values.
- Prefer small, typed modules in the package corresponding to their responsibility.
