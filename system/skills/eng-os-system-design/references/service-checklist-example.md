# Worked Example — Scaffolding a New Notifications Service

Hypothetical: the platform needs a new backend service, `notifications-service`, responsible for
sending email/push notifications triggered by events from other services (e.g. "expense
approved" → notify the employee). This applies the checklist from
`../../../micro/templates/service-template.md` plus this skill's additions.

## Checklist Walkthrough

- **Boundary:** responsibility is "deliver a notification for a triggering event"; it does not
  decide business logic about *whether* to notify (that lives in the calling service); it only
  owns delivery, templating, and channel selection (email vs. push). Inputs: `notification.send`
  events. Outputs: delivery attempts to email/push providers, and a `notification.delivered` /
  `notification.failed` event back onto the bus.
- **Contracts:** one real endpoint below shows the folder layout with routes separated from
  business logic, satisfying the "endpoints exist in the expected folder layout" item. The wire
  contract for `POST /internal/notifications` itself is not re-litigated here; it went through
  the `eng-os-api-design` skill's Definition of Done before being finalized.
- **Reliability:** outbound calls to the email/push providers (SendGrid, FCM) have a 5s timeout
  and 3 retries with exponential backoff; a circuit breaker opens after 10 consecutive provider
  failures to avoid hammering a down provider (bulkheading, isolating provider outages from the
  service's own health).
- **Performance:** latency target is "under 2s from event receipt to provider call," not
  end-to-end delivery (which depends on the provider); throughput target is 500 events/minute
  based on current expense-approval volume with headroom.
- **Observability:** metrics for send attempts, delivery success/failure rate per channel,
  provider latency; structured logs include `notification_id` and `trigger_event_id` for tracing
  one notification back to its cause.
- **Failure modes:** provider outage (mitigated by circuit breaker + retry), duplicate delivery if
  an event is redelivered (mitigated by idempotency key = event id, checked before send), queue
  backlog if throughput spikes (blast radius: delayed but not lost notifications, since the queue
  persists).

## Minimal Real Folder Layout

```
notifications-service/
  src/
    routes/
      notifications.route.ts        # HTTP layer only, validates request, calls service layer
    services/
      notification.service.ts       # business logic: template selection, channel routing
    providers/
      email-provider.ts             # SendGrid client, retry/circuit-breaker wrapper
      push-provider.ts               # FCM client, retry/circuit-breaker wrapper
    events/
      notification-consumer.ts       # consumes notification.send events from the bus
    config/
      timeouts.ts                    # timeout/retry/circuit-breaker constants
  test/
    notification.service.test.ts
```

## One Real Endpoint File

```typescript
// src/routes/notifications.route.ts
import { Router, Request, Response } from "express";
import { sendNotification } from "../services/notification.service";

const router = Router();

// POST /internal/notifications
// Owner: notifications-service team. Purpose: accept a pre-validated notification
// request from an internal caller and enqueue it for delivery. Distinct from
// notification-consumer.ts, which handles the async event-bus trigger path.
router.post("/internal/notifications", async (req: Request, res: Response) => {
  const { recipientId, channel, templateId, idempotencyKey } = req.body;

  if (!recipientId || !channel || !templateId || !idempotencyKey) {
    return res.status(400).json({ error: "missing required field" });
  }

  try {
    const result = await sendNotification({ recipientId, channel, templateId, idempotencyKey });
    return res.status(202).json({ status: "queued", notificationId: result.notificationId });
  } catch (err) {
    // Timeouts/circuit-breaker-open errors surface as 503 so callers can distinguish
    // "provider is down, retry later" from a genuine 4xx client error.
    if (err.code === "PROVIDER_UNAVAILABLE") {
      return res.status(503).json({ error: "notification provider unavailable" });
    }
    return res.status(500).json({ error: "internal error" });
  }
});

export default router;
```

Notice the route file does no template selection or provider logic: that's in
`notification.service.ts`, keeping the "routes/controllers separated from business logic"
checklist item real rather than nominal.
