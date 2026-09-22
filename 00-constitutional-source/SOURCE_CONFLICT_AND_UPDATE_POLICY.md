# Source Conflict and Update Policy

Source retrieval is append-only. A new retrieval creates a new record, timestamp, snapshot path, and hash; it does not overwrite an earlier source object.

A discrepancy is material when it affects a locator, acquired representation, claimed text, completeness, date context, or downstream link. Material discrepancies set the affected record to `CONTESTED` until a documented comparison is completed.

This repository may preserve comparison evidence. It cannot issue a binding constitutional interpretation or independently decide legal effect. An unavailable source, missing hash, unverified provenance, or unresolved discrepancy blocks any dependent chain from `ADMISSIBLE_FOR_CONSEQUENCE`.
