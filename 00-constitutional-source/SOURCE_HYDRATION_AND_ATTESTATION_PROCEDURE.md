# Source Hydration and Attestation Procedure

The repository begins with source governance, not downloaded source claims. A source is not added merely because a URL is known, a page was reachable once, or an automated request returned content.

## Admission steps

1. Identify the official publisher, canonical locator, retrieval time, and intended record family.
2. Retrieve the representation through a permitted method. Do not treat a challenge page, login page, redirect artifact, error page, or unauthenticated mirror as the source text.
3. Preserve the retrieved representation unchanged; calculate its SHA-256 digest; record media type, retrieval method, and any known representation limitations.
4. Create a source acquisition attestation linking the preserved artifact, digest, official locator, and reviewer status.
5. Run conflict review against any existing source record before marking the record admitted.
6. If acquisition is unavailable or ambiguous, retain it in the queue as unresolved. Do not synthesize, infer, or substitute source content.

This procedure intentionally separates source acquisition from interpretation, normalization, and legal conclusion.