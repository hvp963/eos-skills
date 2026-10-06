---
name: eng-os-security-practices
description: "Use when handling input validation, secrets management, authentication/least-privilege, or dependency hygiene. Invoke on any code touching user input, credentials, or external packages."
sources:
  - meso/security.md
globs: ["**/*"]
always_apply: false
verified_platforms: [claude-code]
---

# Security Practices

Apply these rules to any code that accepts external input, handles credentials, manages permissions, pulls dependencies, or drives AI model calls.

## Principles

- **Validation at boundaries.** Every input that enters the system must be validated before use.
- **Fail fast on missing credentials.** Refuse to start rather than fall back to insecure defaults.
- **Least privilege.** Every service, agent, and process requests only the permissions it needs.
- **Defense in depth.** No single control is sufficient; combine validation, credential isolation, dependency hygiene, and monitoring.
- **Observability as a first-class concern.** Security events must be logged, measurable, and alertable; silent failures are the most dangerous.

## Core Patterns

### 1. Input Validation
Validate every external input for type, length, format, and allowed values before it touches any logic. Never pass raw user input to: SQL queries (parameterize), shell commands (avoid; whitelist/sanitize if unavoidable), AI prompts (see AI-Specific Security), or file paths (normalize and restrict to expected root).
- Failure mode: skipping boundary validation and trusting downstream callers is how injection vulnerabilities propagate.

### 2. Secrets Management
Read secrets from environment variables or a secrets manager at startup. Validate all required secrets are present before any work begins: raise a `StartupError` listing missing keys, don't fall back to a default. Never hardcode, commit, or log secrets (not even at debug level; debug logs end up in log exports and incident reports). Design consumers to tolerate re-reads on rotation without a restart when rotation is expected.

### 3. Least Privilege
Scope each service/agent to explicit allow-lists of resource + operation (`read: [...]`, `write: [...]`, `denied: [...]`), enforced at every authorization decision point, not just at provisioning time. Review permissions whenever scope changes; leftover permissions are silent attack surface.
- Failure mode: broad permissions granted for development convenience become permanent production attack surface.

### 4. Dependency Hygiene
Pin exact dependency versions in lock files (not semver ranges) in production. Run CVE scans in CI; fail the build on critical CVEs, warn-and-notify on high. Review/update dependencies on a defined schedule. Don't import a package for single-function convenience: every dependency is a trust surface.
- Failure mode: unpinned ranges silently pull in a patched-then-vulnerable version on the next build.

### 5. AI-Specific Security
AI systems face prompt injection, output exploitation, and training-data leakage risks absent from conventional software.

**Prompt injection prevention:** structurally separate user-supplied content from system instructions; never interpolate raw user input into a system prompt string.
```
// correct
prompt = { "system": SYSTEM_INSTRUCTION, "user": sanitize(userMessage) }
// forbidden
prompt = { "system": "You are a helpful agent. The user says: " + userMessage }
```
Treat any user-supplied field as untrusted input, with the same validation rigor as external API input.

**Output validation before action:** validate AI output against a schema, then check semantic allow-lists, before executing code, calling tools, or modifying records.
```
parsed = OutputSchema.parse(aiResponse)   // throws if schema violated
if parsed.action not in ALLOWED_ACTIONS:
    raise PolicyViolationError("action not permitted")
execute(parsed.action, parsed.parameters)
```
- Failure mode: an AI system that executes its own output without validation is a code execution vulnerability waiting for the right prompt.

See `meso/ai-deterministic-systems.md` for full AI instruction design patterns.

See `references/example.md` for a worked before/after login-route example: raw-body logging
with no boundary validation vs. redacted logging with input validation.

### 6. Authorization Model
Declare one model and enforce it at every decision point: RBAC when permissions depend only on who the caller is; ABAC as soon as "may this user see this record" depends on the record. In any multi-tenant system, every query, cache key, queue message, and log line carries the tenant id, and every access is scoped to the caller's tenant before any other rule runs; row-level scoping in the data layer is the backstop, not the only check.
```
function authorize(principal, action, resource):
    if resource.tenant_id != principal.tenant_id: deny("cross-tenant")   // isolation first
    if not policy.allows(principal, action, resource): deny("policy")
    audit.record(principal, action, resource, "allow")
```
- Failure mode: authorization only at the gateway, so one internal or misrouted call bypasses every rule.

### 7. Threat Modeling
Before the design review of any system handling user data, money, credentials, or AI-driven actions: list assets, draw trust boundaries on the C4 container diagram, enumerate entry points, and for each boundary record the threats considered (spoofing, tampering, disclosure, denial of service, privilege escalation, prompt injection) with the mitigation or the accepted risk. Keep it with the design document; revise when a boundary moves.
- Failure mode: a checklist at implementation time catches injection and misses the admin API reachable from the public network.

### 8. Audit Logging
Security-relevant events (auth success and failure, authorization denial, privilege change, secret access or rotation, data export, user-data deletion, admin actions) go to an append-only audit log separate from application logs, with actor, action, resource, time, origin, and outcome. Retained per `eng-os-privacy-and-governance`; readable by security, not writable by the application after the fact.
- Failure mode: reconstructing "who changed this" from debug logs that rotated out a week ago.

## Failure Modes

- raw user input passed to queries or prompts without validation creates injection risk
- debug-level logging that includes secrets or tokens creates persistent credential exposure
- broad IAM permissions granted during development never get narrowed before production
- unpinned dependencies silently pull in vulnerable versions on the next build
- AI prompts that merge user content with system instructions allow prompt injection
- authorization enforced only at the gateway, bypassed by any internal or misrouted call
- no threat model, so architectural exposures are found by attackers instead of the design review

## Definition of Done

- [ ] All external inputs are validated for type, length, and allowed values at the entry point
- [ ] All secrets are read from environment/secrets manager at startup; none are hardcoded
- [ ] Missing required secrets trigger startup failure, not a fallback default
- [ ] Secrets are explicitly excluded from all log payloads
- [ ] Service/agent permissions are explicitly scoped and documented
- [ ] Dependency versions are pinned; CVE scanning runs in CI and fails the build on critical findings
- [ ] AI systems structurally separate user content from system instructions
- [ ] AI output is validated against a schema and an action allow-list before it is acted on
- [ ] An authorization model (RBAC, ABAC, or both) is declared and enforced at every decision point; multi-tenant access is scoped to the caller's tenant first
- [ ] A threat model exists for any system handling user data, money, credentials, or AI-driven actions, attached to the design document
- [ ] Security-relevant events go to an append-only audit log with actor, action, resource, time, origin, and outcome
