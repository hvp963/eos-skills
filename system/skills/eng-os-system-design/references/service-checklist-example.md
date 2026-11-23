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
  and retry per `eng-os-coding-standards-common` Standard 5; a circuit breaker per
  `eng-os-reliability-engineering` opens when the provider failure rate passes 50% over a 30s
  window, so a down provider is not hammered (bulkheading, isolating provider outages from the
  service's own health).
- **Performance:** latency target is "under 2s from event receipt to provider call," not
  end-to-end delivery (which depends on the provider); throughput target is 500 events/minute
  based on current expense-approval volume with headroom.
- **Observability:** metrics for send attempts, delivery success/failure rate per channel,
  provider latency; structured logs include `notification_id` and `trigger_event_id` for tracing
  one notification back to its cause.
- **Failure modes:** provider outage (mitigated by circuit breaker + retry), duplicate delivery if
  an event is redelivered (mitigated by an atomic insert of the idempotency key, the event id, into
  `deliveries` under a unique constraint before send: `INSERT ... ON CONFLICT DO NOTHING
  RETURNING id`, where no row returned means a duplicate and nothing is sent; a check-then-send
  would let two redeliveries both pass the check), queue
  backlog if throughput spikes (blast radius: delayed but not lost notifications, since the queue
  persists).

## Minimal Real Folder Layout

One capability, `notifications`, with all five layer folders (`eng-os-coding-standards-common`
Standard 13). The HTTP route and the event consumer are both controllers; the provider clients
and the delivery log are repositories.

```
notifications-service/
  src/
    app.ts                                        # composition root: builds repositories, injects them
    config/env.ts                                 # timeouts, retry counts, breaker thresholds
    capabilities/notifications/
      controllers/notifications.controller.ts     # POST /internal/notifications: shape validation, one service call
      controllers/notification-send.consumer.ts   # notification.send events from the bus
      services/notifications.service.ts           # template selection, channel routing, idempotency
      repositories/email-provider.repository.ts   # SendGrid client behind the breaker
      repositories/push-provider.repository.ts    # FCM client behind the breaker
      repositories/deliveries.repository.ts       # deliveries table: the idempotency key's unique constraint
      models/notification.model.ts
      views/notification.view.ts                  # the 202 response shape
  tests/capabilities/notifications/               # mirrors src/, one test file per source file
```

## One Real Endpoint File

```typescript
// src/capabilities/notifications/controllers/notifications.controller.ts
import { Router, Request, Response, NextFunction } from "express";
import { z } from "zod";
import type { NotificationsService } from "../services/notifications.service";
import { toQueuedView } from "../views/notification.view";

// shape validation at the controller; a failure is a 400 in the one error envelope
const SendNotificationSchema = z.object({
  recipient_id: z.string().uuid(),
  channel: z.enum(["email", "push"]),
  template_id: z.string().min(1),
  idempotency_key: z.string().min(1),
});

// POST /internal/notifications
// Owner: notifications-service team. Accepts a notification request from an internal caller
// and enqueues it for delivery; notification-send.consumer.ts handles the event-bus path.
export function makeNotificationsController(notificationsService: NotificationsService) {
  const router = Router();
  router.post("/internal/notifications", async (req: Request, res: Response, next: NextFunction) => {
    try {
      const input = SendNotificationSchema.parse(req.body);           // ZodError -> 400
      const result = await notificationsService.send(input);
      res.status(202).json(toQueuedView(result));
    } catch (err) {
      // the one error-handling middleware maps typed errors to the envelope:
      // ZodError -> 400 validation_error; ProviderUnavailableError -> 503 unavailable
      // with Retry-After; anything else -> 500 internal_error
      next(err);
    }
  });
  return router;
}
```

The controller does no template selection, provider calls, or status mapping: those are in the
service, the repositories, and the one error-handling middleware. Its only branch is the typed
error the middleware maps, `err instanceof ProviderUnavailableError`, never a string property on
an untyped catch variable.
