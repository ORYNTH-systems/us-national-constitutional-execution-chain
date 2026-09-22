# Source Snapshot Immutability Policy

Once a source representation has been committed, that committed representation remains an immutable retrieval event. A later retrieval must not overwrite its event, hash, attestation, or identity.

## Re-retrieval rule

1. Create a new retrieval-event identifier and preserved artifact path.
2. Record both the new artifact digest and its parent or comparison event.
3. State whether the representation is byte-identical, changed, unavailable, or rejected.
4. Do not promote a new representation as the current review target until comparison and review are recorded.

Git history is retained as an additional preservation layer, but it is not a substitute for explicit event records. The source record and its interpretation status remain distinct from the retrieval event.