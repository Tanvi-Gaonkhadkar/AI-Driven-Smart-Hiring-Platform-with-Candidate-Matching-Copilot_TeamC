"""
Duplicate Resume Detection.

Rule-based (no AI call needed - this should be instant and deterministic):
flags when a newly analyzed resume looks like a repeat application, either
because the same person applied again, or because someone resubmitted a
near-identical resume under different contact details.
"""

import difflib


def check_duplicate(new_entry: dict, existing_entries: list) -> list:
    """
    new_entry / each item in existing_entries: dicts with keys
    name, email, phone, resume_text.

    Returns a list of matches: [{"match_name": str, "reasons": [str, ...], "similarity": float}]
    """
    matches = []
    new_email = (new_entry.get("email") or "").strip().lower()
    new_name = (new_entry.get("name") or "").strip().lower()
    new_text = new_entry.get("resume_text") or ""

    for existing in existing_entries:
        if existing is new_entry:
            continue
        existing_email = (existing.get("email") or "").strip().lower()
        existing_name = (existing.get("name") or "").strip().lower()
        existing_text = existing.get("resume_text") or ""

        reasons = []
        if new_email and existing_email and new_email == existing_email:
            reasons.append("same email address as a previous application")
        if new_name and existing_name and new_name == existing_name and existing_email != new_email:
            reasons.append("same name, different contact details")

        similarity = 0.0
        if new_text and existing_text:
            similarity = difflib.SequenceMatcher(
                None, new_text[:3000], existing_text[:3000]
            ).ratio()
            if similarity > 0.85:
                reasons.append(f"resume text is {int(similarity * 100)}% similar to a previous submission")

        if reasons:
            matches.append({
                "match_name": existing.get("name") or "Unknown candidate",
                "reasons": reasons,
                "similarity": round(similarity, 2),
            })

    return matches
