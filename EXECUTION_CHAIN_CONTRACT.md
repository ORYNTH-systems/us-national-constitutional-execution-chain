# Constitutional Execution Chain Contract

## Canonical chain

`constitutional source -> office/role -> jurisdiction -> enacted authority -> delegation -> procedure -> evidence -> admissibility -> decision -> execution -> effect receipt -> review/remedy`

## Required links for a consequential action

| Link | Required question |
| --- | --- |
| Constitutional source | What constitutional text supplies, limits, or prohibits the claimed power? |
| Office/role | Which identified office or role is acting, and is its status current? |
| Jurisdiction | What subject, person, place, time, and institutional boundary applies? |
| Enacted authority | What operative legal authority connects the source to this action? |
| Delegation | Who transferred which bounded authority to whom, under what conditions? |
| Procedure | What process had to occur before effect, and is its record present? |
| Evidence | What evidence supports the required predicates, and what remains unresolved? |
| Admissibility | Are all material links current, complete, non-conflicted, and within scope? |
| Decision | What accountable decision was made, by whom, and at what time? |
| Execution | What implementation occurred under that decision? |
| Effect receipt | What effect occurred, for whom, when, through which system, with what provenance? |
| Review/remedy | What lawful route can test, pause, reverse, correct, or remedy the effect? |

## Integrity states

`PROPOSED` - asserted but not yet admitted as an observed record.

`OBSERVED` - captured with provenance but not yet verified.

`VERIFIED` - stated evidence and linkage checks have passed; this is not a legal conclusion.

`CONTESTED` - a material challenge is pending.

`INVALIDATED` - a required predicate, authority, record, or link has failed.

`CLOSED` - retained with durable provenance and any applicable review status.

`ADMISSIBLE_FOR_CONSEQUENCE` - only a chain-completeness status. It never creates legal effect by itself.

## Fail-closed rule

An action cannot receive `ADMISSIBLE_FOR_CONSEQUENCE` where a material source, actor, office status, jurisdiction, enactment, delegation, procedure, predicate, evidence condition, time-validity condition, receipt, or review/remedy route is unknown, stale, conflicted, revoked, expired, or outside stated scope.
