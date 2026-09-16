# Postmortem: Checkout API outage, 14 August 2026

**Severity:** SEV-1
**Duration:** 47 minutes (09:12 to 09:59 BST)
**Customer impact:** Roughly 6,400 customers saw "Something went wrong" on the payment step. An estimated 1,100 quotes were abandoned.
**Owners:** Payments team (primary), Platform team (supporting)

## Summary

A routine deploy of `checkout-api` v2.31.0 introduced a change to how we read the `PAYMENT_PROVIDER_TIMEOUT_MS` environment variable. The new code parsed the value as an integer but the production value had a trailing `ms` suffix (`"8000ms"`), left over from an older config format. Parsing returned `NaN`, which the HTTP client treated as "no timeout". When the payment provider slowed down at 09:12, every checkout request hung indefinitely, the Node worker pool filled, and the service stopped answering health checks. Kubernetes restarted pods in a loop, which made the outage look like an infrastructure problem for the first 20 minutes.

## Timeline (BST)

| Time | Event |
| --- | --- |
| 08:41 | `checkout-api` v2.31.0 deployed to production via Semaphore. Canary passed (provider was fast at the time). |
| 09:12 | Payment provider latency rises from ~300 ms to ~9 s. Checkout p99 climbs past 30 s. |
| 09:14 | PagerDuty alert `checkout-api-error-rate` fires. On-call engineer acknowledges. |
| 09:16 | Pods begin failing readiness checks; Kubernetes restarts them. Restart loop begins. |
| 09:20 | On-call opens incident channel, pages Platform team suspecting a cluster issue. |
| 09:33 | Platform confirms cluster and network are healthy. Focus shifts to the deploy. |
| 09:41 | Engineer notices `timeout: NaN` in a debug log line. Links it to the config parsing change. |
| 09:47 | Rollback to v2.30.4 started. |
| 09:52 | Rollback complete. Error rate falls. |
| 09:59 | Provider latency recovers. Incident declared resolved. |

## Root cause

The change in v2.31.0 replaced a hand-written config reader with a shared `readIntEnv()` helper. The old reader stripped a `ms` suffix before parsing; the helper does not. `parseInt("8000ms")` actually returns `8000` in JavaScript, but the helper used `Number("8000ms")`, which returns `NaN`. The HTTP client library treats a `NaN` timeout as "disabled".

Neither the unit tests nor the canary caught this because:

- Tests set the variable to `"8000"` with no suffix.
- The canary ran while the provider was fast, so requests completed well under any timeout.

## Contributing factors

- **Stale config format.** The `ms` suffix had been unsupported for two years but was never cleaned up in production because the old reader tolerated it silently.
- **No validation at startup.** The service accepted a `NaN` timeout without logging a warning or refusing to boot.
- **Misleading symptoms.** The restart loop pointed responders at Kubernetes first, costing about 20 minutes.
- **Health check shares the worker pool.** When every worker was hung on a payment call, the health endpoint could not respond either.

## What went well

- The alert fired within two minutes of impact.
- Rollback took five minutes once the cause was identified.
- The incident channel had a clear scribe from 09:20, which made this document quick to write.

## Action items

| # | Action | Owner | Due |
| --- | --- | --- | --- |
| 1 | Make `readIntEnv()` throw on `NaN` and log the offending variable name. | Platform | 21 Aug |
| 2 | Audit all production environment variables for legacy suffixes; remove `ms` from `PAYMENT_PROVIDER_TIMEOUT_MS`. | Payments | 21 Aug |
| 3 | Add a startup validation step that refuses to boot when any timeout is missing or non-finite. | Payments | 28 Aug |
| 4 | Move the health endpoint to a dedicated, non-blocking handler. | Payments | 4 Sep |
| 5 | Add a canary stage that injects 5 s of provider latency before promoting. | Platform | 11 Sep |
| 6 | Add a runbook note: "restart loop after deploy: check the deploy before the cluster". | Payments | 21 Aug |

## Lessons

1. A helper that is "the same as the old code" is a behaviour change until proven otherwise. Diff the behaviour, not just the intent.
2. Fail loudly at startup. A service that boots with an invalid config is worse than one that refuses to boot.
3. Symptoms lie. When a problem starts shortly after a deploy, suspect the deploy first, however infrastructural it looks.
