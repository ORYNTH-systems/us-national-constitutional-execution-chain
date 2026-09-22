# Emergency Authority Integrity Model

This domain records an asserted emergency authority as a time-bounded, source-linked, reviewable action. It does not declare an emergency, create power, determine necessity, or suspend any constitutional or legal constraint.

## Required trace

An activation record identifies the claimed constitutional or statutory source, triggering predicate, accountable office, jurisdiction, defined scope, ordinary constraint affected, start, end or sunset condition, review route, and any renewal source. An emergency-derived effect also links to a consequence gate and effect receipt.

## Fail-closed conditions

- No source-linked predicate: block the claimed emergency effect.
- Effect outside the recorded scope, jurisdiction, or time window: block it.
- Renewal without its own source and record: do not infer continuation.
- End, sunset, or invalidation: require a restoration or cessation receipt for every affected effect.

Emergency records preserve the distinction between an asserted authority and a valid legal conclusion by the responsible institutions.