"""Provider-neutral processing of untrusted structured suggestion responses."""

from typing import TYPE_CHECKING

from app.ai_suggestions import SuggestionResult, validate_suggestions

if TYPE_CHECKING:
    from app.ai_context import AiTriageContext


def process_provider_response(context: "AiTriageContext", raw_response: object) -> SuggestionResult:
    """Validate against application-supplied eligibility without changing inputs.

    MalformedSuggestionResponse propagates unchanged; a valid empty response
    returns the validator's no_usable_suggestions outcome. No provider call,
    authorization, database access, or persistence occurs here.
    """
    return validate_suggestions(
        raw_response, eligible_assignee_ids=context.eligible_assignee_ids,
    )
