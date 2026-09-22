# Authority Carrier Conformance

| Case | Condition | Required result |
| --- | --- | --- |
| AC-001 | Office status unknown | `BLOCK` |
| AC-002 | Appointment required but no record path | `BLOCK` |
| AC-003 | Delegation exceeds identified delegator scope | `BLOCK` |
| AC-004 | Delegation revoked or expired at effect time | `BLOCK` |
| AC-005 | Jurisdiction boundary is missing | `BLOCK` |
| AC-006 | Multiple authorities asserted but roles not separated | `BLOCK` |
| AC-007 | Current office, scope, delegation, and jurisdiction all linked | `ELIGIBLE_FOR_NEXT_GATE` |

`ELIGIBLE_FOR_NEXT_GATE` is not permission to act. It means only that the authority-carrier layer is complete enough to proceed to procedure, evidence, and consequence review.
