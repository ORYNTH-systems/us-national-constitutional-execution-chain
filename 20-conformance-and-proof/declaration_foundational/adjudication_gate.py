"""Fail-closed constitutional relationship adjudication gate."""

SOURCE_STATES = {
    "EXTRACTED_PENDING_VERIFICATION",
    "VERIFIED",
}

RELATIONSHIP_STATES = {
    "NOT_ASSESSED",
    "SUPPORTED",
    "UNSUPPORTED",
}

DISPOSITIONS = {
    "PENDING",
    "RETAIN",
    "NARROW",
    "RECLASSIFY",
    "REJECT",
}


def validate(record):
    required = (
        "source_verification",
        "relationship_assessment",
        "disposition",
        "evidence_rationale",
        "legal_effect",
        "authority_source",
        "authority_verification",
    )

    for field in required:
        if field not in record:
            raise ValueError(f"Missing field: {field}")

    source = record["source_verification"]
    relationship = record["relationship_assessment"]
    disposition = record["disposition"]

    if source not in SOURCE_STATES:
        raise ValueError("Invalid source state")

    if relationship not in RELATIONSHIP_STATES:
        raise ValueError("Invalid relationship state")

    if disposition not in DISPOSITIONS:
        raise ValueError("Invalid disposition")

    if disposition == "PENDING":
        if relationship != "NOT_ASSESSED":
            raise ValueError("Pending disposition has assessed relationship")
    else:
        if source != "VERIFIED":
            raise ValueError("Source not independently verified")

        if not record["evidence_rationale"].strip():
            raise ValueError("Missing adjudication rationale")

        expected = (
            "UNSUPPORTED"
            if disposition == "REJECT"
            else "SUPPORTED"
        )

        if relationship != expected:
            raise ValueError("Disposition and assessment conflict")

    legal_effect = record["legal_effect"]

    if legal_effect == "NONE_INFERRED":
        if record["authority_source"] or record["authority_verification"]:
            raise ValueError("Unexpected authority claim")

    elif legal_effect == "BINDING_AUTHORITY":
        if disposition == "PENDING":
            raise ValueError("Pending relationship cannot assert authority")

        if not record["authority_source"].strip():
            raise ValueError("Missing independent authority source")

        if record["authority_verification"] != "VERIFIED":
            raise ValueError("Authority not verified")

        if record["authority_source"].startswith("DECL-"):
            raise ValueError("Declaration cannot independently grant authority")

        raise ValueError(
            "Binding authority requires a separate execution-authority gate"
        )

    else:
        raise ValueError("Invalid legal effect")

    return True
