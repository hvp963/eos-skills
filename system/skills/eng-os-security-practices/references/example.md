# Worked Example: Login Route — Redacting Secrets in Logs vs. Not

## WRONG — logs the raw request body, no boundary validation

```
function handleLogin(request):
    log.info("login request received", body=request.body)
    // body = { "email": "j.rivera@example.com", "password": "hunter2", "remember_me": "true" }
    // the plaintext password is now in every log aggregator, log export, and incident report
    // that touches this service, permanently, with no way to retract it after the fact

    user = db.findByEmail(request.body.email)   // no validation: request.body.email could be
                                                  // anything, including non-string/oversized input
    if user.password_hash == hash(request.body.password):
        return issueSession(user)
    return Response(status=401)
```

## RIGHT — redact by policy, validate at the boundary, send auth events to the audit log

```
// one logger configuration line: the logger drops these keys from every record, at every call site
// (pino `redact` paths, or a structlog processor that removes them)
LOGIN_REDACT_FIELDS = ["password", "token", "authorization"]
log = Logger(redact=LOGIN_REDACT_FIELDS)

function handleLogin(request):
    // validate at the boundary before anything else touches the input; log the field, never the value
    if not isString(request.body.email) or len(request.body.email) > 254:
        log.warn("validation failed", field="email")
        raise ValidationError("invalid email")
    if not isString(request.body.password) or len(request.body.password) < 1:
        log.warn("validation failed", field="password")
        raise ValidationError("invalid password")

    log.info("login request received", redacted_fields=LOGIN_REDACT_FIELDS)   // no email: it is personal data

    user = db.findByEmail(request.body.email)
    if user is null or not verifyHash(user.password_hash, request.body.password):
        // the actor is the user id when resolved, otherwise a keyed hash of the submitted identifier:
        // a plain hash of an email is reversible by hashing known addresses, an HMAC with a secret is not
        actor = user.id if user is not null else hmac(AUDIT_HASH_KEY, request.body.email)
        audit.record(actor, action="auth.login", resource="session", outcome="failure",
                     origin=request.ip, time=now())
        log.warn("login failed")                                   // no email, password, or hash
        return Response(status=401, body={"error": {
            "type": "unauthenticated", "code": "invalid_credentials",
            "message": AUTH_MESSAGES.INVALID_CREDENTIALS.text, "message_code": AUTH_MESSAGES.INVALID_CREDENTIALS.code,
            "api_version": API_VERSION, "request_id": request.id}})   // envelope: eng-os-api-design, Error Contract

    audit.record(user.id, action="auth.login", resource="session", outcome="success",
                 origin=request.ip, time=now())
    log.info("login succeeded", user_id=user.id)
    return issueSession(user)
```

Applying the rules from `SKILL.md`:
- Input is validated (type and length) before use, and a validation failure logs the field name, not the value.
- The application log never carries the email: the request and failure lines carry none, and the success line carries only the resolved `user_id`.
- Login success and failure are security events, so they go to the append-only audit log (§8) with actor, action, resource, outcome, origin, and time. The actor on a failed login for an unknown account is an HMAC of the submitted identifier, so the audit log can correlate repeated attempts without holding the address.
- `password`, `token`, and `authorization` are removed by the logger's configuration, so a call site cannot leak them by forgetting.
- The 401 response uses one machine-readable code and does not reveal whether the email or the password was wrong.
