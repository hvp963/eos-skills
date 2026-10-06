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

## RIGHT — redact secrets before logging, validate at the boundary

```
LOGIN_REDACT_FIELDS = ["password", "token", "authorization"]

function handleLogin(request):
    // validate at the boundary before anything else touches the input
    if not isString(request.body.email) or len(request.body.email) > 254:
        log.warn("validation failed", field="email")
        raise ValidationError("invalid email")
    if not isString(request.body.password) or len(request.body.password) < 1:
        log.warn("validation failed", field="password")
        raise ValidationError("invalid password")

    // log only after redacting known-sensitive fields, never the raw body
    log.info("login request received",
        email=request.body.email,
        redacted_fields=LOGIN_REDACT_FIELDS)
    // no "password" key appears anywhere in the emitted record, not even hashed:
    // there is no legitimate reason for a password to reach a log sink

    user = db.findByEmail(request.body.email)
    if user is null or not verifyHash(user.password_hash, request.body.password):
        log.warn("login failed", email=request.body.email)   // still no password/hash logged
        return Response(status=401, body={"error": {"code": "invalid_credentials"}})

    log.info("login succeeded", user_id=user.id)
    return issueSession(user)
```

Applying the rules from `SKILL.md`: input is validated (type/length) before use, the response
error uses an explicit machine-readable code rather than leaking whether the email or the password
was wrong, and `password`/`token`/`authorization` are excluded from every log call by policy, not
by remembering to omit them ad hoc at each call site.
