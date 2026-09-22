# Evidence-to-Effect Conformance

| Case | Condition | Required result |
| --- | --- | --- |
| EE-001 | Evidence provenance missing | `BLOCKED` |
| EE-002 | Material evidence conflict unresolved | `BLOCKED` |
| EE-003 | Required predicate unresolved or expired | `BLOCKED` |
| EE-004 | Gate declares effect admissible without all required links | `INVALID` |
| EE-005 | Execution has no effect receipt | `BLOCKED` |
| EE-006 | Effect receipt lacks review/remedy route | `BLOCKED` |
| EE-007 | Complete current chain, resolved evidence, and durable receipt | `ADMISSIBLE_FOR_CONSEQUENCE` |

The last result is a chain-completeness finding only. It never gives a repository record power to authorize or impose an effect.
