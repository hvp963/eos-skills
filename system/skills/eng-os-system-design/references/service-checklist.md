# Service Checklist

Starter checklist for designing or implementing a new backend service, part of `eng-os-system-design`. The base checklist is canonical in `../../../micro/templates/service-template.md`; work through it before writing code and again before calling the service done.

## Additions to the Base Checklist

- **Contracts:** endpoints must exist in the folder layout expected by the project structure
  (routes/controllers separated from business logic), and each endpoint needs an owner and a
  documented purpose distinct from other endpoints in this service. Before finalizing any
  endpoint contract, invoke the `eng-os-api-design` skill and satisfy its Definition of Done. Do not
  restate that checklist here. This scaffold's job is the service's boundary and folder layout;
  `eng-os-api-design` owns the wire contract itself (request/response schemas, versioning, idempotency,
  pagination, rate limiting, caching).
- **Reliability:** the base template's "retry behavior" and "idempotency addressed" items refer
  specifically to this service's own outbound calls to its upstream dependencies, not the
  wire-level idempotency of this service's own endpoints, which is `eng-os-api-design`'s job. Timeouts
  are defined for every outbound call this service makes.

See `service-checklist-example.md` for a minimal real folder layout and one endpoint file applying this
checklist to a hypothetical service.

## Definition of Done

A service design or implementation is done when every applicable item in
`../../../micro/templates/service-template.md` is addressed, plus the skill-specific additions
above: boundary, contracts, reliability, performance, observability, and failure modes are all
explicit, not implied.

## Scale

- the service's share of the project's Scale Targets is stated (peak RPS, largest tenant, data volume)
- SLOs, timeouts, and pool bounds come from `eng-os-reliability-engineering`
- region/cell placement comes from `eng-os-platform-infrastructure`
