# Consequence Gate Model

A consequence gate determines whether a proposed action is complete enough to proceed to execution. It does not create authority, decide disputed law, or replace a lawful decision-maker.

The gate evaluates, at effect time: source, actor, office status, jurisdiction, enacted authority, delegation, procedure, evidence, required predicates, temporal validity, scope, reversal path, and receipt requirements.

`INCOMPLETE | BLOCKED | ESCALATE | ADMISSIBLE_FOR_CONSEQUENCE`

`ADMISSIBLE_FOR_CONSEQUENCE` is a bounded integrity state: all required links passed the declared completeness test. It is not a legal conclusion, an instruction to act, or a substitute for independent review.

Any material unknown, conflict, expired predicate, revocation, missing review route, or absent receipt requirement returns `BLOCKED` or `ESCALATE` rather than silently allowing effect.
