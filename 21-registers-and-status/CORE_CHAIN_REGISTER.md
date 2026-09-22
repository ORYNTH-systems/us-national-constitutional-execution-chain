# Core Chain Register

This register indexes the six foundational record families. It is intentionally empty at Batch 01: no constitutional text, office, legislative, statute, delegation, or jurisdiction claim is admitted merely by creating a schema.

| Record family | Identifier prefix | Domain | Entry condition |
| --- | --- | --- | --- |
| Constitutional Source Record | `CSR-` | 00 | Official locator, retrieval provenance, and content hash present |
| Office and Role Record | `ORR-` | 01 | Lawful source reference and current-status basis present |
| Legislative Lineage Record | `LLR-` | 02 | Measure event and official source locator present |
| Statute to Execution Link | `SEL-` | 03 | Operative provision, claimed effect, and scope present |
| Delegation and Revocation Record | `DLR-` | 04 | Delegator, delegate, basis, scope, and time validity present |
| Jurisdiction Record | `JUR-` | 05 | Actor, basis, subject, geography, and institutional boundary present |

All entries remain subject to the repository integrity boundary and fail-closed rule.
