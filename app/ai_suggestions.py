"""Internal suggestion contract, independent of provider transport and persistence."""

from dataclasses import dataclass
import re
from typing import Literal


TEXT_FIELDS = frozenset({
    "title", "affected_version", "environment", "description",
    "steps_to_reproduce", "expected_result", "actual_result",
})
SEVERITIES = frozenset({"Blocker", "Major", "Moderate", "Minor"})
PRIORITIES = frozenset({"Urgent", "High", "Medium", "Low"})
SUPPORTED_FIELDS = TEXT_FIELDS | {"severity", "priority", "assignee_id"}

# Text suggestions must be replacement field values, not advice, questions or placeholders.
ADVICE_START = re.compile(
    r"(?i)^\s*(?:please|kindly|consider|you (?:should|could|may|might)|specify|provide|clarify|mention"
    r"|add (?:the|a|an|more|any|browser|device|os|operating|environment|version|details|information|steps))\b"
)
NON_VALUE_TEXT = re.compile(
    r"(?i)\?\s*$|\b(?:todo|tbd|tbc|n/a|not specified|to be (?:determined|confirmed))\b"
    r"|\[[^\]]*\s[^\]]*\]|<[^<>]*\s[^<>]*>"
)


def is_replacement_text(field, value):
    # Numbered steps legitimately start with imperative verbs such as Add.
    advice = field != "steps_to_reproduce" and ADVICE_START.search(value)
    return not advice and not NON_VALUE_TEXT.search(value)


class MalformedSuggestionResponse(ValueError):
    """The response cannot be interpreted as structured field suggestions."""


@dataclass
class SuggestionResult:
    suggestions: dict[str, str | int]

    @property
    def outcome(self) -> Literal["suggestions", "no_usable_suggestions"]:
        return "suggestions" if self.suggestions else "no_usable_suggestions"


def validate_suggestions(raw: object, *, eligible_assignee_ids: set[int]) -> SuggestionResult:
    """Validate {"suggestions": [{"field": <bug field name>, "value": <value>}, ...]}.

    The caller supplies current same-project QA Analyst/Developer IDs eligible
    under the assignment rules for the form's state (AI Assist currently requires
    Triage). This function does not authorize requests or query project members.
    Missing/blank values are omitted, never represented as clearing instructions.
    Nonblank text is preserved exactly. Identical duplicates collapse; conflicting
    nonblank entries exclude the field, even if one of their values is invalid.
    Provider adapters must preserve duplicate entries until validation.
    """
    if not isinstance(raw, dict) or set(raw) != {"suggestions"} or not isinstance(raw["suggestions"], list):
        raise MalformedSuggestionResponse("Expected a suggestions list.")

    candidates = {}
    for entry in raw["suggestions"]:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("field"), str)
            or set(entry) - {"field", "value"}
        ):
            raise MalformedSuggestionResponse("Expected field/value suggestion entries.")
        field = entry["field"]
        value = entry.get("value")
        if field not in SUPPORTED_FIELDS or value is None or (isinstance(value, str) and not value.strip()):
            continue
        candidates.setdefault(field, []).append(value)

    suggestions = {}
    for field, values in candidates.items():
        value = values[0]
        if any(type(other) is not type(value) or other != value for other in values[1:]):
            continue
        if field in TEXT_FIELDS:
            valid = isinstance(value, str) and is_replacement_text(field, value)
        elif field == "severity":
            valid = isinstance(value, str) and value in SEVERITIES
        elif field == "priority":
            valid = isinstance(value, str) and value in PRIORITIES
        else:
            valid = type(value) is int and value > 0 and value in eligible_assignee_ids
        if valid:
            suggestions[field] = value
    return SuggestionResult(suggestions)
