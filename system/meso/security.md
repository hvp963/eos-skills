# Security

**Authors:** Haresh V. Parekh
**Status:** Current
**Owner:** Haresh V. Parekh

## Definition

### What This Is
A design guide for building systems that are resistant to misuse, credential exposure, injection attacks, and AI-specific vulnerabilities.

### What This Is Not
- not a penetration testing guide
- not a replacement for a dedicated security audit
- not a list of tools: tools change; the patterns do not

## Scope
- Level: Meso
- Applies To: All services, pipelines, APIs, and AI-adjacent code
- See Also: `micro/coding-standards/common.md`; implementation rules

---

## Applied Principles

### Validation at Boundaries
Every input that enters the system must be validated before use.

### Fail Fast on Missing Credentials
Systems must refuse to start rather than fall back to insecure defaults.

### Least Privilege
Every service, agent, and process requests only the permissions it needs for its defined function.

### Defense in Depth
No single control is sufficient. Combine input validation, credential isolation, dependency hygiene, and monitoring.

### Observability as a First-Class Concern
Security events must be logged, measurable, and alertable. Silent failures are the most dangerous.

---

## Core Patterns

### 1. Input Validation

Validate every external input for type, length, format, and allowed values before it touches any logic.

```
function handleRequest(input):
    // validate at the boundary — before any processing
    if not isString(input.user_id) or len(input.user_id) > 64:
        log.warn("validation failed", field="user_id", value_length=len(input.user_id))
        raise ValidationError("invalid user_id")

    if input.action not in ALLOWED_ACTIONS:
        log.warn("validation failed", field="action", reason="not in allow-list")   // never log the rejected value
        raise ValidationError("disallowed action")

    // proceed only after all fields pass
    process(input)
```

Never pass raw user input to:
- SQL queries (parameterize)
- shell commands (avoid; if unavoidable, whitelist and sanitize)
- AI prompts (see AI-Specific Security below)
- file paths (normalize and restrict to expected root)

#### Failure Mode
Skipping validation at the boundary and trusting downstream callers to check is how injection vulnerabilities propagate.

---

### 2. Secrets Management

Secrets must be read from environment variables or a secrets manager at startup. They must never be hardcoded, committed, or logged.

```
// startup — validate all required secrets before any work begins
REQUIRED_SECRETS = ["DATABASE_URL", "API_KEY", "SIGNING_SECRET"]

// one error at startup lists every missing key; the language skill names the error type
function validateSecrets():
    missing = [key for key in REQUIRED_SECRETS if not getenv(key)]
    if missing:
        fail startup: "Missing required secrets: " + join(missing, ", ")

// reading
apiKey = getenv("API_KEY")   // required — raise at startup if absent

// logging — never include secrets in log payloads
log.info("request sent", endpoint=endpoint, request_id=request_id)
// NOT: log.info("request sent", api_key=apiKey)
```

Secrets rotation: design consumers to tolerate re-reads from the secrets manager without a restart when rotation is expected.

#### Failure Mode
A secret logged once at debug level is a secret that will appear in log exports, cloud logging UIs, and incident reports.

---

### 3. Least Privilege

Each service or agent must request only the permissions required for its declared function. Permissions must be scoped to a single resource type and operation set where possible.

```
// define explicit scope at service initialization: anything not listed is denied
servicePermissions = {
    "read":  ["orders", "products"],
    "write": ["order_events"],
}

// enforce at every decision point; deny by default
function authorize(action, resource):
    if resource not in servicePermissions.get(action, []):   // an action with no entry is denied
        log.warn("authorization denied", action=action, resource=resource)
        raise AuthorizationError("access denied")
```

Review permissions when scope changes. Leftover permissions are silent attack surface.

#### Failure Mode
Broad permissions granted for convenience during development become permanent attack surface in production.

---

### 4. Dependency Hygiene

Pin all dependency versions. Run CVE scans in CI. Fail the build on critical vulnerabilities.

```
// CI pipeline step — dependency scan
step "dependency-scan":
    run: scan_dependencies(lock_file="requirements.lock")
    on_critical_cve: fail_build()
    on_high_cve: warn_and_notify(channel="security-alerts")
    report: upload_to_artifact_store()
```

- Pin to exact versions in lock files, not semver ranges in production
- Review and update dependencies on a defined schedule (e.g., weekly automated PR)
- Do not import packages for single-function convenience; every dependency is a trust surface

#### Failure Mode
Unpinned ranges pull in a patched-then-vulnerable version silently on the next build.

---

### 5. AI-Specific Security

AI systems face prompt injection, model output exploitation, and training data leakage risks not present in conventional software.

#### Prompt Injection Prevention

Structurally separate user-supplied content from system instructions. Never interpolate raw user input directly into a system prompt.

```
// correct — user content is isolated in its own field
prompt = {
    "system": SYSTEM_INSTRUCTION,       // static, controlled
    "user":   sanitize(userMessage),    // user content — never merged into system
}

// forbidden — dynamic system prompt constructed from user input
prompt = {
    "system": "You are a helpful agent. The user says: " + userMessage,
}
```

Treat any content from user-supplied fields as untrusted input. Apply the same validation rules as external API input.

#### Output Validation Before Action

Validate AI output before acting on it, especially before executing code, calling tools, or modifying records.

```
aiResponse = callModel(prompt)

// validate structure before use
parsed = OutputSchema.parse(aiResponse)   // throws if schema violated

// validate semantics before executing
if parsed.action not in ALLOWED_ACTIONS:
    log.warn("model returned disallowed action", action=parsed.action)
    raise PolicyViolationError("action not permitted")

// only now execute
execute(parsed.action, parsed.parameters)
```

See `meso/ai-deterministic-systems.md` for full AI instruction design patterns.

#### Failure Mode
An AI system that executes its own output without validation is a code execution vulnerability waiting for the right prompt.

---

### 6. Authorization Model

Authentication says who the caller is; authorization says what they may do to which resource.
Every system declares one authorization model and enforces it at every decision point:

- **Role-based (RBAC)**: principals hold roles; roles grant permissions. Adequate when
  permissions depend only on who the caller is.
- **Attribute-based (ABAC)**: decisions use attributes of the principal, the resource, and the
  context (tenant, ownership, classification, time). Required as soon as "may this user see
  this record" depends on the record.
- **Tenant isolation**: in any multi-tenant system, every query, cache key, queue message, and
  log line carries the tenant identifier, and every read or write is scoped to the caller's
  tenant before any other rule is evaluated. Row-level scoping in the data layer is the
  backstop; it is not the only check.

```
function authorize(principal, action, resource):
    if resource.tenant_id != principal.tenant_id:   // isolation first
        deny("cross-tenant")
    if not policy.allows(principal, action, resource):
        deny("policy")
    audit.record(principal, action, resource, "allow")
```

- Failure mode: an authorization check placed in the API gateway only, with services trusting
  any request that reaches them, means one misrouted or internal call bypasses every rule.

### 7. Threat Modeling

Before a design review for any system that handles user data, money, credentials, or AI-driven
actions, produce a threat model: the assets, the trust boundaries (drawn on the C4 container
diagram), the entry points, and for each boundary the threats considered (spoofing, tampering,
information disclosure, denial of service, privilege escalation, prompt injection) with the
mitigation or the accepted risk. Keep it with the design document and revise it when a boundary
moves.

- Failure mode: security handled as a checklist at implementation time catches injection and
  secrets, and misses the architectural exposures (an internal admin API reachable from the
  public network, a queue any service can publish to) that a boundary walk finds in minutes.

### 8. Audit Logging

Every security-relevant event is recorded in an append-only audit log separate from
application logs: authentication success and failure, authorization denial, privilege change,
secret access or rotation, data export, deletion of user data, and any administrative action.
Each record carries who, what, which resource, when, from where, and the outcome. Audit logs
are retained per the data-governance policy and are readable by security, not writable by
the application after the fact.

- Failure mode: an incident investigation that has to reconstruct "who changed this" from
  application debug logs that rotated out a week ago.

---

### 9. Web and Authentication Basics

Six rules for any web-facing service and any service that authenticates users. Each one is the default control for a well-known attack class; a project that departs from one records why in an ADR.

1. **Output encoding.** Encode output for the context it lands in (HTML body, attribute, URL, JavaScript). Use the framework's auto-escaping and never bypass it (`dangerouslySetInnerHTML`, `|safe`, `v-html`) without a sanitizer and a reason comment at the call site. Set a Content-Security-Policy that disallows inline script.
   - Failure mode: one user-supplied field rendered as raw HTML runs an attacker's script in every viewer's session (stored cross-site scripting).
2. **CSRF.** A state-changing request authenticated by a cookie needs `SameSite=Lax` or `Strict` cookies plus a CSRF token or an `Origin` header check. An API authenticated only by a token in a header is exempt, because a browser does not attach that header to a cross-site request.
   - Failure mode: a form on another site submits a transfer with the victim's session cookie attached, and the server cannot tell it from a real request.
3. **SSRF.** A server-side fetch of a user-supplied URL resolves the host, rejects private, loopback, link-local, and cloud-metadata addresses, connects to the address it checked, allows only declared schemes and hosts, and does not follow a redirect to a disallowed host.
   - Failure mode: an "import from URL" field pointed at the cloud metadata address returns the instance's credentials to the attacker.
4. **Password storage.** Hash passwords with argon2id (bcrypt where argon2 is unavailable), with the cost parameters recorded in config; never a fast hash such as SHA-256, salted or not. Rehash on the next successful login when the parameters change.
   - Failure mode: a leaked table of fast hashes is cracked offline in hours, and reused passwords open the users' other accounts.
5. **Sessions and tokens.** Use server-side revocable sessions, or short-lived access tokens with refresh-token rotation. Session cookies are `HttpOnly`, `Secure`, and `SameSite`. Rotate the session id on login and on any privilege change; logout revokes the session on the server.
   - Failure mode: a session id fixed before login, or a token that stays valid after logout, gives whoever holds it the account.
6. **Authentication throttling.** Rate-limit login, password reset, and MFA endpoints per account and per source, with progressive delay rather than permanent lockout (a permanent lockout lets anyone lock a known user out). Responses do not reveal whether the account exists.
   - Failure mode: an unthrottled login endpoint is credential-stuffed at thousands of attempts a minute, and a "no such user" message hands the attacker a list of valid accounts.

---

## Failure Modes

- raw user input passed to queries or prompts without validation creates injection risk
- debug-level logging that includes secrets or tokens creates persistent credential exposure
- broad IAM permissions granted during development never get narrowed before production
- unpinned dependencies silently pull in vulnerable versions on the next build
- AI prompts that merge user content with system instructions allow prompt injection
- authorization enforced only at the gateway, so any internal or misrouted call bypasses every rule
- no threat model, so architectural exposures are found by attackers instead of by the design review

---

## Definition of Done

Security design is complete when:

### Per change

- all external inputs are validated for type, length, and allowed values at the entry point
- all secrets are read from environment or secrets manager at startup; none are hardcoded
- required secrets trigger startup failure if absent
- secrets are explicitly excluded from all log payloads
- service permissions are explicitly scoped and documented
- AI systems structurally separate user content from system instructions
- AI output is validated against a schema before acting on it
- an authorization model (RBAC, ABAC, or both) is declared and enforced at every decision point; multi-tenant systems scope every access to the caller's tenant first
- security-relevant events are written to an append-only audit log with actor, action, resource, time, origin, and outcome
- web-facing code meets section 9 (output encoding, CSRF, SSRF, password storage, sessions, throttling)

### Standing (release and audit)

- dependency versions are pinned and CVE scanning runs in CI
- a threat model exists for any system handling user data, money, credentials, or AI-driven actions, and is attached to the design document
