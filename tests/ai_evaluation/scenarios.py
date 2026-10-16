"""Frozen fictional AC-019.2 cases, version 1. No application imports or IO."""

from copy import deepcopy


DATASET_VERSION = "1"
BLANK_FORM = dict.fromkeys((
    "title", "affected_version", "environment", "description", "steps_to_reproduce",
    "expected_result", "actual_result", "severity", "priority",
), "") | {"assignee_id": None}
MEMBERS = [
    {"user_id": 11, "email": "qa@example.com", "role": "QA Analyst"},
    {"user_id": 12, "email": "dev@example.com", "role": "Developer"},
]
DETAILED_FORM = BLANK_FORM | {
    "title": "filtered csv empty",
    "affected_version": "0.8.2",
    "environment": "TestOS 4 / Aster Browser 12",
    "description": "Orchid Board's filtered grid contains seven rows. Reproduced three times.",
    "steps_to_reproduce": "Open reports; filter State=Ready; select Export CSV.",
    "expected_result": "CSV contains the seven displayed rows.",
    "actual_result": "The downloaded CSV contains its header only.",
}
HISTORY_BASE = {field: None for field in BLANK_FORM}


# TC-351 | AC-019.2 — Sparse information must not become invented observations.
SCENARIO_A = {
    "id": "EVAL-A", "tc_id": "TC-351", "purpose": "Sparse bug information",
    "context": {
        "current_form": BLANK_FORM | {"title": "Export fails"},
        "recent_bugs": [], "eligible_assignees": [],
    },
    "review": "Accept omission or restrained rewriting; no invented environment, version, steps or error.",
    "offline_suggestions": [{"field": "title", "value": "Export fails"}],
}

# TC-352 | AC-019.2 — Improve supported reproduction without changing its facts.
SCENARIO_B = {
    "id": "EVAL-B", "tc_id": "TC-352", "purpose": "Supported reproduction evidence",
    "context": {"current_form": DETAILED_FORM, "recent_bugs": [], "eligible_assignees": MEMBERS},
    "review": "Preserve seven rows, three observations and header-only output wherever mentioned; no invented cause.",
    "offline_suggestions": [{"field": "title", "value": "Filtered CSV export contains only its header"}],
}

# TC-353 | AC-019.2 — Explicit unsaved current facts take precedence over history.
SCENARIO_C = {
    "id": "EVAL-C", "tc_id": "TC-353", "purpose": "Current form conflicts with history",
    "context": {
        "current_form": DETAILED_FORM | {
            "description": "Unsaved retest: seven filtered rows, repeated three times. Older browser not used for this retest.",
        },
        "recent_bugs": [HISTORY_BASE | {
            "id": 401, "title": "Old export download failure", "affected_version": "0.5.0",
            "environment": "TestOS 2 / Aster Browser 9", "actual_result": "No file downloaded.",
        }],
        "eligible_assignees": MEMBERS,
    },
    "review": "Current 0.8.2/TestOS 4/Aster 12 and header-only download win; attributed historical comparisons are allowed.",
    "offline_suggestions": [{"field": "actual_result", "value": "The CSV downloads but contains only its header."}],
}

# TC-354 | AC-019.2 — Relevant history may support empty current fields.
SCENARIO_D = {
    "id": "EVAL-D", "tc_id": "TC-354", "purpose": "Relevant recurring historical values",
    "context": {
        "current_form": BLANK_FORM | {
            "title": "Export stays disabled for an empty grid",
            "description": "Orchid Board empty-grid export problem. Current build and browser were not recorded.",
            "steps_to_reproduce": "Filter State=Archived until no rows remain; inspect Export CSV.",
            "expected_result": "Allow exporting an empty CSV containing its header.",
            "actual_result": "Export CSV remains disabled.",
        },
        "recent_bugs": [HISTORY_BASE | {
            "id": identifier, "title": title,
            "description": "Orchid Board: filtering to zero rows leaves Export CSV disabled.",
            "environment": "TestOS 4 / Aster Browser 12", "affected_version": "0.8.2",
            "severity": "Moderate", "priority": "Medium", "assignee_id": 12,
        } for identifier, title in (
            (502, "Export disabled after Archived filter"), (501, "Cannot export an empty report grid"),
        )],
        "eligible_assignees": MEMBERS,
    },
    "review": "History reasonably supports Environment, Affected Version, Severity, Priority and eligible Assignee proposals; do not claim current verification.",
    "offline_suggestions": [
        {"field": "environment", "value": "TestOS 4 / Aster Browser 12"},
        {"field": "affected_version", "value": "0.8.2"},
        {"field": "severity", "value": "Moderate"},
        {"field": "priority", "value": "Medium"},
        {"field": "assignee_id", "value": 12},
    ],
}

# TC-355 | AC-019.2 — Preserve uncertainty where neither source supports facts.
SCENARIO_E = {
    "id": "EVAL-E", "tc_id": "TC-355", "purpose": "Unverified causal hypothesis",
    "context": {
        "current_form": BLANK_FORM | {
            "title": "Preview unavailable",
            "description": "A timeout is suspected but unconfirmed. Cause, logs, build, browser and impact on other users are unknown.",
            "actual_result": "Clicking Preview displays 'Preview unavailable'.",
        },
        "recent_bugs": [], "eligible_assignees": [],
    },
    "review": "Keep timeout tentative or omit it; no invented HTTP code, stack trace, confirmed cause, data loss or population impact.",
    "offline_suggestions": [],
}

# TC-356 | AC-019.2 — Irrelevant same-project reports must not contaminate output.
SCENARIO_F = {
    "id": "EVAL-F", "tc_id": "TC-356", "purpose": "Irrelevant historical reports",
    "context": {
        "current_form": DETAILED_FORM | {"affected_version": "", "environment": ""},
        "recent_bugs": [HISTORY_BASE | {
            "id": identifier, "title": title, "environment": "LegacyPrintOS 9",
            "affected_version": "0.2.0", "assignee_id": 11,
            "description": description,
        } for identifier, title, description in (
            (602, "Avatar image appears blurred", "Only the profile avatar image is blurred."),
            (601, "Timezone badge label is wrong", "Profile timezone badge has an incorrect label."),
        )],
        "eligible_assignees": MEMBERS,
    },
    "review": "No basis for copying LegacyPrintOS 9, 0.2.0 or profile symptoms into the export report; review recommendation relevance separately.",
    "offline_suggestions": [{"field": "title", "value": "Filtered CSV export contains only its header"}],
}


def load_scenarios():
    """Return independent copies; offline fixture responses never enter model input."""
    return deepcopy([SCENARIO_A, SCENARIO_B, SCENARIO_C, SCENARIO_D, SCENARIO_E, SCENARIO_F])
