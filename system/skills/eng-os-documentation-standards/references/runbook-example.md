# Runbook Example

Source: `meso/documentation.md` §2.4 (Operational Documentation)

A runbook gives an operator enough information to act during an incident or routine operation
without hunting for context. It must include:
- what the system does (one paragraph, no assumptions about prior knowledge)
- how to confirm it is healthy
- common failure symptoms and their likely causes
- step-by-step recovery procedures for each known failure mode
- escalation path: who to contact and when

```
// runbook structure
# Runbook: Orders Pipeline

## System Summary
Consumes order events from Kafka, enriches with customer profile, writes to orders warehouse table.
Expected throughput: 2,000 events/minute.

## Health Check
- Grafana: orders-pipeline dashboard → throughput > 1,500 events/min, error rate < 0.1%
- Check consumer lag: `kafka-consumer-groups --describe --group orders-pipeline`

## Failure: Consumer Lag Growing
Likely cause: downstream warehouse write latency spike.
Steps:
  1. Check warehouse write latency on Grafana orders-pipeline dashboard
  2. If latency > 2s p95, check warehouse cluster health
  3. If healthy, reduce batch size in config: BATCH_SIZE=50 (default: 100)
  4. Restart pipeline service

## Escalation
SLA breach (lag > 10 min): page #data-oncall
```
