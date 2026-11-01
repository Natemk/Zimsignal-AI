# ADR 0002: External Data and Provenance

- Status: Accepted
- Date: 2026-10-30

## Context

ZimSignal combines official structured data, public documents, and optionally
private user-authorized sources. Collection permissions, freshness, and
provenance affect whether evidence can support an answer.

## Decision

- Prefer an official structured API or dataset over scraping when one is
  available and suitable.
- Use Firecrawl only for public pages where automated access is permitted and
  no suitable structured source exists. Respect terms, robots signals, access
  controls, and publisher restrictions; never bypass logins or paywalls.
- Register each source before ingestion. Record its publisher, canonical URL,
  source type and tier, access/retention policy, retrieval time, page status,
  and content hash where applicable. Use the existing `source_registry`
  migration; keep source policy in `access_policy` unless queryable fields
  require a later migration.
- Preserve source metadata through normalization, chunking, indexing, and
  retrieval. Answers must cite retrieved evidence and reject unsupported claims.
- Treat fetched pages, documents, emails, and user uploads as untrusted data,
  never as instructions. Do not fetch arbitrary user-supplied URLs without
  allowlisting and SSRF controls.
- Keep tenant-private data on separately authorized connector paths; do not
  mix it with public-source ingestion or another tenant's retrieval scope.

## Consequences

Ingestion must fail closed when source policy is unknown, and retrieval must
retain provenance. A source's tier informs prioritization; it is not proof that
every claim from that source is correct.

## Implementation status

The repository has a source-registry table and Firecrawl document metadata, but
does not yet enforce a registry allowlist across ingestion or provide complete
answer-time citations and freshness controls. Those remain acceptance work for
Weeks 3-4.