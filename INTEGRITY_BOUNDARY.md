# Integrity Boundary

## Source boundary

`00-constitutional-source/` contains source references, hashes, retrieval provenance, and amendment lineage only. It must not contain normalized constitutional text presented as an authoritative replacement.

## Legal boundary

This repository cannot create office, jurisdiction, delegation, appointment, appropriation, rule, remedy, or legal effect. Those arise only through the lawful constitutional and statutory processes they describe.

## Operational boundary

A record may be `PROPOSED`, `OBSERVED`, `VERIFIED`, `CONTESTED`, `INVALIDATED`, or `CLOSED`. `VERIFIED` means its stated evidence path has passed the defined checks; it does not itself mean a court or other lawful decision-maker has made a legal finding.

## Fail-closed rule

Unknown source, actor, jurisdiction, delegation, material predicate, evidence conflict, or time-validity condition blocks the record from receiving `ADMISSIBLE_FOR_CONSEQUENCE` status.
