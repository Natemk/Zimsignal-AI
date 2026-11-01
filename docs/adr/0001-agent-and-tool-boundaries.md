# ADR 0001: Agent and Tool Boundaries

- Status: Accepted
- Date: 2026-10-30

## Context

ZimSignal needs conversational research and workflow automation without giving a
language model authority over identity, tenant isolation, or consequential writes.
The project is being implemented in milestones, so the architecture decision
must distinguish the target design from code that is not yet integrated.

## Decision

- Use one supervisor as the conversational entry point. Give it narrow, typed
  tools for deterministic operations such as public API queries and retrieval.
- Keep validation, authorization, tenant filtering, idempotency, and business
  rules in ordinary application code; prompts are not security controls.
- Add a specialist agent only when a documented need for context isolation,
  distinct tool permissions, parallel work, or a sequential workflow justifies
  its extra state and failure modes. Otherwise, use a tool or function.
- Use LangGraph for routing, execution state, checkpoints, and approval pauses.
  Keep per-invocation identity and entitlements in immutable runtime context,
  derived from trusted authentication or a verified channel-link record.
- Do not expose hidden reasoning in streaming or logs; expose concise status and
  evidence instead.

## Consequences

The supervisor remains responsible for synthesis and routing. Tool contracts
are independently testable, and specialist boundaries must be justified by an
ADR or an update to this one. Durable checkpointers and approval persistence are
required before production use.

## Implementation status

The repository currently has a deterministic LangGraph router and specialist
nodes. The Week 5 target of a `create_agent` supervisor with typed tools is not
yet implemented; this ADR records the intended boundary, not a claim that the
acceptance gate has passed.