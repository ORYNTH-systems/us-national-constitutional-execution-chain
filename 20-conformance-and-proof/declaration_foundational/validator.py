"""Fail-closed source-classification checks; not a legal inference engine."""
from dataclasses import dataclass

class AuthorityError(ValueError):
    pass

@dataclass(frozen=True)
class Claim:
    claim_id: str
    source_kind: str
    source_id: str
    source_span: str
    claimed_binding: bool
    legal_basis_id: str = ""
    verified: bool = False

def validate(claim: Claim) -> str:
    if not all((claim.claim_id, claim.source_id, claim.source_span)):
        raise AuthorityError("Missing source provenance")
    if claim.source_kind not in {"FOUNDATIONAL", "BINDING", "ASSESSMENT"}:
        raise AuthorityError("Unknown source classification")
    if claim.claimed_binding:
        if claim.source_kind != "BINDING":
            raise AuthorityError("Nonbinding source cannot authorize legal effect")
        if not claim.legal_basis_id or not claim.verified:
            raise AuthorityError("Unverified or missing independent legal basis")
    return "CLASSIFICATION_PASS"
