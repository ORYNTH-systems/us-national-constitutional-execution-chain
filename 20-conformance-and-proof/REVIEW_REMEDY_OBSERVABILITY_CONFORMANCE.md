# Review, Remedy, and Observability Conformance

| Case | Condition | Required result |
| --- | --- | --- |
| RR-001 | Judicial claim has no identified case, court, or scope | `BLOCKED` |
| RR-002 | Judicial action is stayed, vacated, or pending but treated as final | `BLOCKED` |
| RR-003 | Effect has no challenge or remedy route | `BLOCKED` |
| RR-004 | Correction erases the original effect receipt | `INVALID` |
| RR-005 | Restricted information has no attributable restriction basis | `BLOCKED` |
| RR-006 | Public trace omits responsible principal or effect | `INCOMPLETE` |
| RR-007 | Effect, review, correction, and public-safe trace remain linked | `ELIGIBLE_FOR_CLOSURE` |

`ELIGIBLE_FOR_CLOSURE` preserves provenance and does not end any lawful appeal, challenge, or review route.
