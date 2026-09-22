# Official Source Ingestion Protocol

## Purpose

This protocol preserves official source representations without presenting this repository as an authoritative replacement for constitutional text. Every accepted acquisition must retain its official locator, retrieval time, byte-level SHA-256 hash, and retrieval method.

## Admission sequence

1. Obtain an identified official representation through an auditable retrieval path.
2. Preserve the received bytes as an immutable snapshot.
3. Hash those exact bytes with SHA-256.
4. Create an `OBSERVED` Constitutional Source Record that links the snapshot, hash, locator, and retrieval provenance.
5. Independently compare representations before any source record is used as `VERIFIED` for a defined purpose.
6. Preserve conflict, revision, and retrieval-failure evidence; never silently overwrite a prior acquisition.

## Boundaries

- A web representation is evidence of a publication endpoint, not a replacement Constitution.
- A hash identifies acquired bytes; it does not prove legal meaning or effect.
- Interpretive material remains separately attributed and cannot silently become source.
- A source record documents provenance; it cannot confer authority.

## Source acquisition queue

The first acquisition targets are the National Archives Constitution transcription and the Congress.gov Constitution full-text entry point. They remain `PENDING_RETRIEVAL` until their actual received representations, hashes, and provenance are admitted in the dedicated source-hydration batch.
