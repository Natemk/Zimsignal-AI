# ZimSignal AI

ZimSignal is an evidence-grounded agricultural intelligence service. Its FastAPI
application exposes chat, tenant-isolated workspace search, and health endpoints.
LangGraph routes chat requests to specialist nodes; retrieval uses source-aware
documents stored in PostgreSQL with pgvector.

## Architecture

- `agents/`: supervisor and domain specialist nodes.
- `api/`: FastAPI entry point, authentication, routes, and request dependencies.
- `governance/`: profile-change audit records and alert dispatching.
- `ingestion/`: Firecrawl collection, document processing, and pgvector indexing.
- `orchestration/`: graph state, graph assembly, and deterministic routing.
- `agents/prompts/`: prompt templates.
- `tools/`: public-data clients, MCP adapters, workspace connector, and tool registry.
- `tests/`: unit and integration tests.
- `evals/`: evaluation datasets and suites.

Older `engine.*`, `tools.definitions.*`, `orchestration.supervisor`, and
`retrieval.rag_chain` import paths remain as compatibility re-exports while callers
migrate to the new package paths.

## Local setup

1. Copy `.env.example` to `.env` and set any external API keys you use.
2. Install the pinned dependencies: `python -m pip install -e ".[dev]"`.
3. Start PostgreSQL/pgvector and Redis: `docker compose up -d`.
4. Set `OIDC_ISSUER`, `OIDC_AUDIENCE`, `OIDC_JWKS_URL`, and the public
	`VITE_AUTH0_DOMAIN`, `VITE_AUTH0_CLIENT_ID`, and `VITE_AUTH0_AUDIENCE`
	values in the project-root `.env` file.
5. Run `npm run dev` to start the API and React app with the project virtual
	environment. Open `http://localhost:5173` for chat or
	`http://localhost:8000/docs` for the API reference.

Run unit tests with `python -m pytest tests/unit`. Integration tests may need a
running database and valid external service credentials.
