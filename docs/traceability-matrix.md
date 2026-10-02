# Traceability Matrix

## Purpose

This matrix provides requirements traceability and maintains an inventory of automated tests.

It connects:

* Requirements
* Acceptance Criteria
* Test References
* Test Layers
* Coverage Status

BDD scenarios are maintained separately as behavioural specifications.

Every automated test should appear in this matrix. Not every test must map directly to an Acceptance Criterion; additional tests may be created to cover technical risks, edge cases, security concerns, or other areas not explicitly defined by the requirements.

Test Reference currently contains existing automated test function names, with `—` retained where no test reference is recorded. In future it may also contain formal manual test-case IDs or names; none are introduced here. Each automated test has its own row, with one function per Test Reference cell.

User Stories remain part of requirements.md; they are not a column in this matrix.

The matrix is updated throughout development and testing.

## Status

* **Covered** — The complete acceptance criterion is adequately tested at every required layer. Passing API tests alone do not establish required UI coverage.

* **Partial** — Some aspects of the acceptance criterion are covered, but additional coverage is required.

* **Pending** — The functionality or required test has not yet been implemented.

* **Manual** — The behaviour is currently verified through manual testing rather than automated testing.

* **Specification Only** — A BDD scenario exists as a behavioural specification but is not currently executable.

## Test Layers

* **API** — API-level functional testing

* **Security** — Security and authorization testing

* **Database** — Database and data-integrity testing

* **UI** — User-interface testing

* **BDD** — Executable Behaviour-Driven Development test

* **Validation** — Input and validation testing

---

## Increment 1 — User & Project Management

### REQ-001 — User Registration

| REQ     | AC                                 | Test Reference                                                  | Test Layer           | Status  |
| ------- | ---------------------------------- | --------------------------------------------------------------- | ------------------- | ------- |
| REQ-001 | AC-001.1 — Successful Registration | `test_successful_registration`                                  | API                 | Partial |
| REQ-001 | AC-001.2 — Duplicate Email         | `test_registration_with_duplicate_email`                        | API                 | Partial |
| REQ-001 | AC-001.3 — Invalid Email           | `test_registration_with_invalid_email`                          | API                 | Partial |
| REQ-001 | AC-001.4 — Invalid Password        | `test_registration_with_short_password`                         | API                 | Partial |
| REQ-001 | AC-001.4 — Invalid Password        | `test_registration_without_uppercase_password`                  | API                 | Partial |
| REQ-001 | AC-001.4 — Invalid Password        | `test_registration_without_lowercase_password`                  | API                 | Partial |
| REQ-001 | AC-001.4 — Invalid Password        | `test_registration_without_number_password`                     | API                 | Partial |
| REQ-001 | AC-001.5 — Password Security       | `test_password_is_not_stored_as_plain_text`                     | Database / Security | Covered |
| REQ-001 | —                                  | `test_registration_rejects_invalid_password_for_existing_email` | API / Validation    | Covered |
| REQ-001 | —                                  | `test_registration_rejects_password_over_bcrypt_limit`          | API / Validation    | Covered |

### REQ-002 — User Login

| REQ     | AC                             | Test Reference                       | Test Layer | Status  |
| ------- | ------------------------------ | ------------------------------------ | --------- | ------- |
| REQ-002 | AC-002.1 — Successful Login    | `test_successful_login`              | API       | Covered |
| REQ-002 | AC-002.1 — Successful Login    | —                                    | UI        | Manual  |
| REQ-002 | AC-002.2 — Invalid Credentials | `test_login_with_incorrect_password` | API       | Covered |
| REQ-002 | AC-002.2 — Invalid Credentials | `test_login_with_unknown_email`      | API       | Covered |
| REQ-002 | AC-002.1 — Successful Login | `test_login_and_access_with_configured_secret` | API / Security | Partial |
| REQ-002 | — | `test_token_signed_with_configured_secret` | API / Security | Covered |
| REQ-002 | — | `test_missing_or_blank_jwt_secret_key_rejects_authentication` | API / Security | Covered |
| REQ-002 | — | `test_secret_not_in_login_response` | API / Security | Covered |

### REQ-003 — Protected Access

| REQ     | AC                                | Test Reference                                               | Test Layer      | Status  |
| ------- | --------------------------------- | ------------------------------------------------------------ | -------------- | ------- |
| REQ-003 | AC-003.1 — Authenticated Access   | `test_authenticated_user_can_access_protected_endpoint`      | API            | Covered |
| REQ-003 | AC-003.2 — Unauthenticated Access | `test_unauthenticated_user_cannot_access_protected_endpoint` | API / Security | Covered |
| REQ-003 | AC-003.2 — Unauthenticated Access | —                                                            | UI             | Manual  |
| REQ-003 | AC-003.3 — Invalid Authentication | `test_invalid_token_cannot_access_protected_endpoint`        | API / Security | Partial |
| REQ-003 | AC-003.3 — Invalid Authentication | `test_forged_token_with_old_secret_is_rejected` | API / Security | Partial |
| REQ-003 | — | `test_secret_not_in_protected_response` | API / Security | Covered |
| REQ-003 | — | `test_secret_not_in_error_response` | API / Security | Covered |

### REQ-004 — User Logout

| REQ     | AC                                       | Test Reference | Test Layer | Status |
| ------- | ---------------------------------------- | -------------- | --------- | ------ |
| REQ-004 | AC-004.1 — Successful Logout             | —              | UI        | Manual |
| REQ-004 | AC-004.2 — Protected Access After Logout | —              | UI        | Manual |

### REQ-005 — Project Creation

| REQ     | AC                                      | Test Reference                                         | Test Layer | Status  |
| ------- | --------------------------------------- | ------------------------------------------------------ | --------- | ------- |
| REQ-005 | AC-005.1 — Successful Project Creation  | `test_create_project`                                  | API       | Covered |
| REQ-005 | AC-005.2 — Invalid Project Name         | `test_create_project_with_empty_name`                  | API       | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name         | `test_project_creation_rejects_whitespace_only_name`     | API       | Partial |
| REQ-005 | AC-005.3 — Unauthenticated User         | `test_unauthenticated_user_cannot_create_project`      | API       | Covered |

### REQ-006 — Project Access

| REQ     | AC                                     | Test Reference                                  | Test Layer      | Status  |
| ------- | -------------------------------------- | ----------------------------------------------- | -------------- | ------- |
| REQ-006 | AC-006.1 — View Project List           | `test_get_projects`                             | API            | Covered |
| REQ-006 | AC-006.2 — Project List Authorization  | `test_user_only_sees_own_projects`              | API / Security | Covered |
| REQ-006 | AC-006.3 — Open Project                | `test_get_project`                              | API            | Covered |
| REQ-006 | AC-006.4 — Unauthorized Project Access | `test_user_cannot_access_another_users_project` | API / Security | Covered |

### REQ-007 — Project Name Editing

| REQ     | AC                                           | Test Reference                                     | Test Layer      | Status  |
| ------- | -------------------------------------------- | -------------------------------------------------- | -------------- | ------- |
| REQ-007 | AC-007.1 — Successful Project Name Editing   | `test_edit_project_name`                           | API            | Partial |
| REQ-007 | AC-007.2 — Unauthorized Project Name Editing | `test_user_cannot_edit_another_users_project_name` | API / Security | Covered |

### REQ-008 — Project Deletion

| REQ     | AC                                        | Test Reference                                                   | Test Layer                  | Status  |
| ------- | ----------------------------------------- | ---------------------------------------------------------------- | -------------------------- | ------- |
| REQ-008 | AC-008.1 — Successful Project Deletion    | `test_delete_project`                                            | API                        | Partial |
| REQ-008 | AC-008.1 — Successful Project Deletion    | `test_new_project_owner_cannot_access_bugs_from_deleted_project` | API / Database / Security  | Partial |
| REQ-008 | AC-008.2 — Unauthorized Project Deletion  | `test_user_cannot_delete_another_users_project`                  | API / Security             | Covered |

**Coverage note:** AC-008.1 is currently **Partial** because project deletion and deletion-related data isolation are automated at the API/database level, while the required browser confirmation is currently tested manually. Playwright coverage will be added after Increment 1 is complete.

### REQ-009 — Project Member Management

| REQ     | AC                              | Test Reference                                                    | Test Layer        | Status  |
| ------- | ------------------------------- | ----------------------------------------------------------------- | ---------------- | ------- |
| REQ-009 | AC-009.1 — Add Member           | `test_owner_can_add_project_member`                               | API / Validation | Partial |
| REQ-009 | AC-009.1 — Add Member           | `test_added_member_can_access_project`                            | API / Security   | Partial |
| REQ-009 | AC-009.2 — Remove Member        | `test_owner_can_remove_project_member`                            | API              | Partial |
| REQ-009 | AC-009.2 — Remove Member        | `test_removed_member_can_no_longer_access_project`                | API / Security   | Partial |
| REQ-009 | AC-009.2 — Remove Member        | `test_removing_member_unassigns_only_their_bugs_in_that_project`  | API              | Partial |
| REQ-009 | AC-009.3 — Invalid Member       | `test_project_owner_cannot_add_user_who_does_not_have_an_account` | API / Validation | Covered |
| REQ-009 | AC-009.4 — Duplicate Member     | `test_project_owner_cannot_add_same_user_more_than_once`          | API / Validation | Covered |
| REQ-009 | AC-009.5 — View Project Members | `test_project_member_can_view_project_members`                    | API / Security   | Partial |
| REQ-009 | —                               | `test_project_owner_cannot_remove_themselves`                     | API / Security   | Covered |

AC-009.2 has API coverage for member removal, loss of access, automatic unassignment, preservation of other bug data, Last Updated changes, and unaffected assignments. UI/manual verification remains outstanding, so coverage is Partial.

### REQ-010 — Project Roles and Permissions

| REQ     | AC                                                | Test Reference                                 | Test Layer      | Status  |
| ------- | ------------------------------------------------- | ---------------------------------------------- | -------------- | ------- |
| REQ-010 | AC-010.1 — Project Owner Role                     | `test_project_creator_is_project_owner`        | API / Security | Covered |
| REQ-010 | AC-010.2 — QA Analyst Role                        | `test_qa_analyst_can_access_project`           | API / Security | Covered |
| REQ-010 | AC-010.3 — Developer Role                         | `test_developer_can_access_project`            | API / Security | Covered |
| REQ-010 | AC-010.4 — Unauthorized Project Member Management | `test_non_owner_cannot_manage_project_members` | API / Security | Covered |
| REQ-010 | AC-010.5 — Unauthorized Project Actions           | `test_non_owner_cannot_edit_project`           | API / Security | Covered |
| REQ-010 | AC-010.5 — Unauthorized Project Actions           | `test_non_owner_cannot_delete_project`         | API / Security | Covered |

---

## Increment 2 — Bug Management

### REQ-011 — Bug Creation

| REQ | AC | Test Reference | Test Layer | Status |
|---|---|---|---|---|
| REQ-011 | AC-011.1 — Successful Bug Creation | `test_project_member_can_create_bug` | API | Partial |
| REQ-011 | AC-011.2 — Missing Bug Title | `test_bug_creation_rejected_without_title` | API / Validation | Partial |
| REQ-011 | AC-011.3 — Unauthorized Bug Creation | `test_non_member_cannot_create_bug` | API / Security | Covered |
| REQ-011 | AC-011.4 — Optional Bug Information | `test_bug_can_be_created_with_optional_information` | API / Validation | Partial |

**Coverage note:** AC-011.4 includes the optional free-text Environment field. The automated creation test verifies that Environment can be supplied and returned correctly. Existing bug-creation tests that omit Environment also verify that the field remains optional.


### REQ-012 — Bug Access

| REQ | AC | Test Reference | Test Layer | Status |
|---|---|---|---|---|
| REQ-012 | AC-012.1 — View Bug List | `test_project_member_can_view_bug_list` | API | Partial |
| REQ-012 | AC-012.2 — Open Bug Report | `test_project_member_can_open_bug_report` | API | Partial |
| REQ-012 | AC-012.3 — Unauthorized Bug Access | `test_non_member_cannot_open_bug_report` | API / Security | Covered |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_bug_list_defaults_to_most_recently_updated_first` | API | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | — | UI | Partial |

**Coverage note:** AC-012.2 verifies Environment in the full bug-report response. AC-012.4 sorting is implemented for all seven columns in the browser, with initial Last Updated descending and missing optional values last in both directions. Severity uses Blocker, Major, Moderate, Minor from high to low; Priority uses Urgent, High, Medium, Low; Status follows the lifecycle order.

**Sorting verification:** The existing API default-order test passed (1 case). Temporary Node checks executed the actual page script with a simulated DOM and API response: initial order, all columns in both directions, case-insensitive text, null/undefined/empty values last, switching columns, indicators, focus restoration, unchanged rendered values and links, no sorting API requests or source-data mutation, refresh, and empty-list recovery passed. JavaScript syntax and diff checks passed. These checks are not a committed UI test suite or visual browser evidence. AC-012.4 remains Partial until browser verification covers mouse and keyboard interaction, both themes, layout, and navigation through the retained bug links. No manual test-case ID is assigned.


### REQ-013 — Bug Editing

| REQ | AC | Test Reference | Test Layer | Status |
|---|---|---|---|---|
| REQ-013 | AC-013.1 — Edit Bug Report | `test_project_member_can_edit_bug_report` | API | Partial |
| REQ-013 | AC-013.2 — Optional Bug Information | `test_project_member_can_update_optional_bug_information` | API / Validation | Partial |
| REQ-013 | AC-013.3 — Unauthorized Bug Editing | `test_non_member_cannot_edit_bug_report` | API / Security | Covered |
| REQ-013 | — | `test_bug_update_rejected_with_null_title` | API / Validation | Covered |

**Coverage note:** AC-013.2 includes updating the optional free-text Environment field.

**Additional regression coverage:** An explicit null title is rejected with HTTP 422 and “Bug title is required.” The test verifies through the API that the bug report remains unchanged. This covers API validation only; it does not establish UI coverage or completion of REQ-013.


### REQ-014 — Bug Deletion

| REQ | AC | Test Reference | Test Layer | Status |
|---|---|---|---|---|
| REQ-014 | AC-014.1 — Successful Bug Deletion | `test_authorized_member_can_delete_bug` | API | Partial |
| REQ-014 | AC-014.1 — Successful Bug Deletion | — | UI | Pending |
| REQ-014 | AC-014.2 — Unauthorized Bug Deletion | `test_unauthorized_member_cannot_delete_bug` | API / Security | Covered |

**Coverage note:** AC-014.1 is Partial because bug deletion is automated through the API, while the required browser confirmation remains pending.


### REQ-015 — Bug Assignment

| REQ | AC | Test Reference | Test Layer | Status |
|---|---|---|---|---|
| REQ-015 | AC-015.1 — Assign and Unassign Bugs | `test_authorized_member_can_assign_bug` | API | Partial |
| REQ-015 | AC-015.1 — Assign and Unassign Bugs | `test_authorized_member_can_unassign_bug` | API | Partial |
| REQ-015 | AC-015.1 — Assign and Unassign Bugs | — | UI | Pending |
| REQ-015 | AC-015.2 — Invalid Assignment | `test_bug_cannot_be_assigned_to_invalid_member` | API / Validation | Covered |
| REQ-015 | AC-015.3 — Unauthorized Bug Assignment | `test_non_member_cannot_assign_bug` | API / Security | Covered |
| REQ-015 | AC-015.4 — Change Bug Assignee | `test_authorized_member_can_reassign_bug` | API | Partial |

**Coverage note:** AC-015.1 is Partial until assignment and unassignment are also covered through the browser UI.


### REQ-016 — Bug Classification

| REQ | AC | Test Reference | Test Layer | Status |
|---|---|---|---|---|
| REQ-016 | AC-016.1 — Set Bug Severity | `test_project_member_can_set_bug_severity` | API | Partial |
| REQ-016 | AC-016.1 — Set Bug Severity | — | UI | Pending |
| REQ-016 | AC-016.2 — Set Bug Priority | `test_project_member_can_set_bug_priority` | API | Partial |
| REQ-016 | AC-016.2 — Set Bug Priority | — | UI | Pending |
| REQ-016 | AC-016.3 — Update Bug Classification | `test_project_member_can_update_bug_classification` | API | Partial |
| REQ-016 | AC-016.3 — Update Bug Classification | — | UI | Pending |
| REQ-016 | AC-016.4 — Unauthorized Bug Classification | `test_non_member_cannot_update_bug_classification` | API / Security | Covered |
| REQ-016 | — | `test_bug_rejects_invalid_severity` | API / Validation | Covered |
| REQ-016 | — | `test_bug_rejects_invalid_priority` | API / Validation | Covered |

**Coverage note:** `test_project_member_can_set_bug_severity` is parameterized across Project Owner, QA Analyst, and Developer roles and all supported severity values: Blocker, Major, Moderate, and Minor.

`test_project_member_can_set_bug_priority` is parameterized across the same roles and all supported priority values: Urgent, High, Medium, and Low.

The validation tests also verify that unsupported values and values belonging to the opposite classification category are rejected. Critical is explicitly rejected as Severity during creation and editing. Moderate and Blocker remain invalid as Priority. `test_bug_can_be_created_with_optional_information` verifies creation with each of the four supported severity values.


### REQ-017 — Bug Lifecycle

| REQ | AC | Test Reference | Test Layer | Status |
|---|---|---|---|---|
| REQ-017 | AC-017.1 — Bug Status | `test_new_bug_starts_in_triage` | API | Partial |
| REQ-017 | AC-017.1 — Bug Status | — | UI | Pending |
| REQ-017 | AC-017.2 — Triage to Open | `test_project_owner_or_qa_can_move_bug_from_triage_to_open` | API | Partial |
| REQ-017 | AC-017.2 — Triage to Open | `test_triage_to_open_can_assign_eligible_project_member` | API | Partial |
| REQ-017 | AC-017.2 — Triage to Open | `test_triage_to_open_rejects_ineligible_assignee` | API / Validation | Partial |
| REQ-017 | AC-017.2 — Triage to Open | `test_developer_cannot_move_bug_from_triage_to_open` | API / Security | Partial |
| REQ-017 | AC-017.2 — Triage to Open | `test_bug_without_assignee_cannot_move_from_triage_to_open` | API / Validation | Partial |
| REQ-017 | AC-017.2 — Triage to Open | — | UI | Pending |
| REQ-017 | AC-017.3 — Open to Development | `test_project_owner_can_move_bug_from_open_to_development` | API | Partial |
| REQ-017 | AC-017.3 — Open to Development | `test_open_to_development_requires_valid_developer_assignee` | API / Validation | Partial |
| REQ-017 | AC-017.3 — Open to Development | `test_qa_analyst_cannot_move_bug_from_open_to_development` | API / Security | Partial |
| REQ-017 | AC-017.3 — Open to Development | `test_non_assigned_developer_cannot_move_bug_from_open_to_development` | API / Security | Partial |
| REQ-017 | AC-017.3 — Open to Development | — | UI | Pending |
| REQ-017 | AC-017.4 — Development to Testing | `test_assigned_developer_can_move_bug_from_development_to_testing` | API | Partial |
| REQ-017 | AC-017.4 — Development to Testing | `test_project_owner_can_move_bug_from_development_to_testing` | API | Partial |
| REQ-017 | AC-017.4 — Development to Testing | `test_non_assigned_developer_cannot_move_bug_from_development_to_testing` | API / Security | Partial |
| REQ-017 | AC-017.4 — Development to Testing | `test_bug_cannot_move_to_testing_with_developer_assignee` | API / Validation | Partial |
| REQ-017 | AC-017.4 — Development to Testing | — | UI | Pending |
| REQ-017 | AC-017.5 — Testing Outcome | `test_assigned_qa_can_pass_bug_and_close_it` | API | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_project_owner_can_pass_bug_and_close_it` | API | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_assigned_qa_can_fail_bug_and_return_it_to_development` | API | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_project_owner_can_fail_bug_and_return_it_to_development` | API | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_failed_testing_requires_valid_developer_assignee` | API / Validation | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_non_assigned_qa_cannot_record_testing_outcome` | API / Security | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_testing_outcome_is_required` | API / Validation | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_invalid_testing_outcome_is_rejected` | API / Validation | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | — | UI | Pending |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_assigned_developer_can_close_bug_without_fixing` | API | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_project_owner_can_close_bug_without_fixing` | API | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_non_assigned_developer_cannot_close_bug_without_fixing` | API / Security | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_bug_cannot_be_closed_without_resolution` | API / Validation | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_fixed_resolution_cannot_be_manually_selected_when_closing_bug` | API / Validation | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | — | UI | Pending |
| REQ-017 | AC-017.7 — Closed Bugs | `test_project_owner_can_move_closed_bug_to_triage` | API | Partial |
| REQ-017 | AC-017.7 — Closed Bugs | `test_project_owner_can_move_unassigned_closed_bug_to_triage` | API | Partial |
| REQ-017 | AC-017.7 — Closed Bugs | `test_unauthorized_user_cannot_move_closed_bug_to_triage` | API / Security | Partial |
| REQ-017 | AC-017.7 — Closed Bugs | `test_closed_bug_rejects_invalid_direct_transition` | API / Validation | Partial |
| REQ-017 | AC-017.7 — Closed Bugs | `test_closed_to_triage_rejects_extra_transition_data` | API / Validation | Partial |
| REQ-017 | AC-017.7 — Closed Bugs | — | UI | Pending |
| REQ-017 | AC-017.8 — Invalid Status Transitions | `test_bug_cannot_skip_from_triage_to_development` | API / Validation | Partial |
| REQ-017 | AC-017.8 — Invalid Status Transitions | `test_bug_cannot_skip_from_open_to_testing` | API / Validation | Partial |
| REQ-017 | AC-017.8 — Invalid Status Transitions | `test_bug_cannot_move_from_development_back_to_open` | API / Validation | Partial |
| REQ-017 | AC-017.8 — Invalid Status Transitions | `test_bug_cannot_move_from_testing_back_to_open` | API / Validation | Partial |
| REQ-017 | AC-017.8 — Invalid Status Transitions | `test_bug_cannot_move_from_testing_back_to_triage` | API / Validation | Partial |
| REQ-017 | AC-017.8 — Invalid Status Transitions | — | UI | Pending |
| REQ-017 | AC-017.9 — Status Update Timestamp | `test_changing_bug_status_updates_last_updated_timestamp` | API | Covered |

**Coverage note:** Project Owner lifecycle authority is now covered at the API layer for:

- Open → Development
- Development → Testing
- Testing → Closed after a Passed testing outcome
- Testing → Development after a Failed testing outcome
- Development → Closed without fixing

Project Owner authority does not bypass lifecycle or assignee requirements. Development still requires a Developer assignee, Testing still requires a QA Analyst assignee, and failed testing requires a Developer to be selected before the bug returns to Development.

Supported non-fix resolutions are:

- `Won't Fix`
- `Duplicate`
- `Cannot Reproduce`
- `Not a Bug`

The close-without-fixing tests are parameterized across all supported non-fix resolutions.

`Fixed` cannot be selected manually. It is assigned automatically only when a bug in Testing receives a `Passed` testing outcome and moves to Closed.

Closed has no normal forward lifecycle transition. A Project Owner may return a Closed bug to Triage; the transition clears its resolution, preserves its assignee, and restores the normal lifecycle and assignment rules.

The Project Owner Closed-to-Triage test also verifies that Last Updated changes during the transition.

AC-017.1 through AC-017.8 remain Partial because browser verification and automated UI coverage are still pending. The lifecycle UI includes closure outcomes and the Project Owner's return-to-Triage action, but the project does not yet have a frontend browser-test framework. AC-017.9 is Covered at the API layer because it specifies timestamp behavior rather than a separate browser interaction.

## REQ-018 — Request AI-Assisted Triage

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| REQ-018 | AC-018.1 — Access AI Triage | — | UI | Partial |
| REQ-018 | AC-018.1 — Access AI Triage | `test_ai_assist_requires_authorized_project_role` | API / Security | Partial |
| REQ-018 | AC-018.1 — Access AI Triage | `test_ai_assist_requires_authentication` | API / Security | Partial |
| REQ-018 | AC-018.1 — Access AI Triage | `test_ai_assist_checks_current_bug_status` | API / Security | Partial |
| REQ-018 | AC-018.1 — Access AI Triage | `test_ai_assist_rechecks_membership` | API / Security | Partial |
| REQ-018 | AC-018.1 — Access AI Triage | `test_ai_assist_rejects_bug_outside_project` | API / Security | Partial |
| REQ-018 | AC-018.2 — Explicit Request | — | UI | Partial |
| REQ-018 | AC-018.2 — Explicit Request | `test_submit_ai_context_limits_requests_and_reports_unavailable` | Unit (JavaScript) | Partial |
| REQ-018 | AC-018.3 — Use Current Form Information | `test_ai_assist_preserves_current_form_without_saving` | API | Partial |
| REQ-018 | AC-018.3 — Use Current Form Information | `test_ai_assist_rejects_invalid_context` | API / Validation | Partial |
| REQ-018 | AC-018.3 — Use Current Form Information | `test_ai_assist_requires_complete_snapshot` | API / Validation | Partial |
| REQ-018 | AC-018.3 — Use Current Form Information | `test_collect_ai_context_preserves_blank_and_unsaved_values` | Unit (JavaScript) | Partial |
| REQ-018 | AC-018.3 — Use Current Form Information | — | UI | Pending |
| REQ-018 | AC-018.4 — Request Outcome | `test_ai_triage_configured_pipeline_preserves_form_and_returns_validated_suggestions` | API / Mocked Provider Integration | Partial |
| REQ-018 | AC-018.4 — Request Outcome | `test_ai_triage_returns_distinct_no_usable_suggestions` | API / Mocked Provider Integration | Partial |
| REQ-018 | AC-018.4 — Request Outcome | `test_ai_triage_failures_are_safe_errors_without_persistence` | API / Mocked Provider Integration | Partial |
| REQ-018 | AC-018.4 — Request Outcome | — | UI | Pending |
| REQ-018 | AC — | `test_submit_ai_context_recovers_from_network_failure` | Unit (JavaScript) | Partial |

AI Assist visibility was manually checked in the first slice for Project Owner, QA Analyst, Developer, empty New Bug, Triage and non-Triage Edit Bug, and a Closed bug returned to Triage. Browser verification of the second slice's form transport, loading state, and duplicate-request guard remains pending; JavaScript unit tests do not establish browser coverage.

The second slice adds POST `/projects/{project_id}/ai-assist` and POST `/projects/{project_id}/bugs/{bug_id}/ai-assist`. Both accept a complete ten-field current-form snapshot, including empty text and a nullable assignee ID, without saving bug data. Edit requests never fill missing fields from stored bug values. Authorization checks current membership, role, and (for Edit) the bug's project and current Triage status before the service boundary is called. Its original tests retain the unconfigured HTTP 503 behavior. The sixth REQ-019 slice integrates configured backend results and safe provider errors with offline API tests. AC-018.1 through AC-018.4 remain Partial overall; presenting generated outcomes in the browser remains pending.

API tests are in `tests/test_ai_assist.py` and `tests/test_ai_triage.py`. Dependency-free JavaScript unit tests run with `node --test tests/frontend/ai-assist.test.cjs` and exercise form collection and request transport using small form/control substitutes. REQ-020 suggestion presentation/use UI and real-model evaluation remain deferred.


## REQ-019 — Validated AI Suggestions

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| REQ-019 | AC-019.1 — Supported Suggestion Fields | `test_ai_suggestions_accept_all_supported_fields` | Unit / Validation | Partial |
| REQ-019 | AC-019.1 — Supported Suggestion Fields | `test_ai_suggestions_exclude_unsupported_or_unmapped_fields` | Unit / Validation | Partial |
| REQ-019 | AC-019.1 — Supported Suggestion Fields | `test_ai_generation_defines_only_supported_output_fields` | Unit / Generation Contract | Partial |
| REQ-019 | AC-019.1 — Supported Suggestion Fields | `test_ai_triage_configured_pipeline_preserves_form_and_returns_validated_suggestions` | API / Mocked Provider Integration | Partial |
| REQ-019 | AC-019.2 — Use Bug and Project Context | `test_ai_context_preserves_submitted_form_and_persisted_bugs` | API / Context | Partial |
| REQ-019 | AC-019.2 — Use Bug and Project Context | `test_ai_context_retrieves_bounded_deterministic_same_project_history` | API / Database / Context | Partial |
| REQ-019 | AC-019.2 — Use Bug and Project Context | `test_ai_context_includes_only_current_assignable_project_members` | API / Context | Partial |
| REQ-019 | AC-019.2 — Use Bug and Project Context | `test_ai_context_supports_empty_project_history_and_assignees` | API / Context | Partial |
| REQ-019 | AC-019.2 — Use Bug and Project Context | `test_ai_context_is_not_constructed_for_rejected_requests` | API / Security | Partial |
| REQ-019 | AC-019.2 — Use Bug and Project Context | `test_ai_generation_preserves_separate_context_without_mutation` | Unit / Generation Contract | Partial |
| REQ-019 | AC-019.2 — Use Bug and Project Context | `test_ai_generation_instructions_define_context_and_safety_boundaries` | Unit / Generation Contract | Partial |
| REQ-019 | AC-019.2 — Use Bug and Project Context | `test_ai_openai_sends_existing_contract_with_sdk_without_network_or_database` | Unit / Mocked Provider Adapter | Partial |
| REQ-019 | AC-019.2 — Use Bug and Project Context | `test_ai_triage_configured_pipeline_preserves_form_and_returns_validated_suggestions` | API / Mocked Provider Integration | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_suggestions_exclude_non_string_text_without_losing_valid_field` | Unit / Validation | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_suggestions_exclude_invalid_classification_without_losing_valid_field` | Unit / Validation | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_suggestions_accept_classification_matching_bug_validation` | Unit / Validation | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_suggestions_exclude_ineligible_or_non_integer_assignee` | Unit / Validation | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_suggestions_use_current_assignable_project_member_context` | API + Unit / Validation | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_suggestions_exclude_conflicting_duplicate_field` | Unit / Validation | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_suggestions_collapse_identical_duplicates_and_ignore_blank_entries` | Unit / Validation | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_generation_classification_rules_match_application` | Unit / Generation Contract | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_generation_limits_assignees_to_supplied_eligible_context` | Unit / Generation Contract | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_response_delegates_to_validator_and_returns_its_result` | Unit / Response Processing | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_response_uses_only_context_assignee_eligibility` | Unit / Response Processing | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_response_preserves_conflicting_duplicate_behavior` | Unit / Response Processing | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_triage_configured_pipeline_preserves_form_and_returns_validated_suggestions` | API / Mocked Provider Integration | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_triage_revalidates_current_member_eligibility` | API / Mocked Provider Integration | Partial |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_triage_excludes_assignee_removed_during_generation` | API / Mocked Provider Integration | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_suggestions_accept_partial_set_without_mutating_input` | Unit / Validation | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_suggestions_omit_blank_values_without_clearing_fields` | Unit / Validation | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_suggestions_report_malformed_structure_as_error` | Unit / Validation | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_suggestions_report_no_usable_suggestions_for_valid_structure` | Unit / Validation | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_generation_reuses_suggestion_envelope_and_allows_zero_suggestions` | Unit / Generation Contract | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_response_retains_partial_valid_suggestions` | Unit / Response Processing | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_response_preserves_no_usable_suggestions_outcome` | Unit / Response Processing | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_response_propagates_malformed_response` | Unit / Response Processing | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_openai_returns_raw_data_without_domain_validation` | Unit / Mocked Provider Adapter | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_openai_rejects_uncompleted_output` | Unit / Mocked Provider Adapter | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_openai_rejects_refusal_instead_of_returning_suggestions` | Unit / Mocked Provider Adapter | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_openai_rejects_missing_or_unparseable_json` | Unit / Mocked Provider Adapter | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_triage_configured_pipeline_preserves_form_and_returns_validated_suggestions` | API / Mocked Provider Integration | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_triage_returns_distinct_no_usable_suggestions` | API / Mocked Provider Integration | Partial |
| REQ-019 | AC-019.4 — Partial and Empty Suggestions | `test_ai_triage_failures_are_safe_errors_without_persistence` | API / Mocked Provider Integration | Partial |
| REQ-019 | AC — | `test_ai_generation_does_not_introduce_account_information_or_secrets` | Unit / Security | Partial |
| REQ-019 | AC — | `test_ai_response_has_no_mutation_database_or_provider_side_effects` | Unit / Response Processing | Partial |
| REQ-019 | AC — | `test_ai_openai_does_not_expose_mutable_input_to_client` | Unit / Mocked Provider Adapter | Partial |
| REQ-019 | AC — | `test_ai_openai_propagates_request_failure_without_fake_suggestions` | Unit / Mocked Provider Adapter | Partial |
| REQ-019 | AC — | `test_ai_triage_configured_requests_authorize_before_any_pipeline_work` | API / Security | Partial |
| REQ-019 | AC — | `test_ai_triage_unconfigured_requests_keep_503_without_provider_work` | API / Configuration | Partial |
| REQ-019 | AC — | `test_ai_triage_configuration_is_checked_on_each_request` | API / Configuration | Partial |
| REQ-019 | AC — | `test_ai_triage_client_factory_disables_retries_without_reading_credentials` | Unit / Configuration | Partial |
| REQ-019 | AC — | `test_ai_triage_timeout_is_safe_without_retries_or_persistence` | API / Mocked Provider Integration | Partial |

The first REQ-019 slice adds a pure validator in `app/ai_suggestions.py`. Its internal application contract is `{"suggestions": [{"field": "title", "value": "Suggested title"}]}`, using existing bug field keys (including `assignee_id`). The envelope contains only `suggestions`; each entry has a string `field` and an optional `value`, with no extra entry keys. Uninterpretable structures raise `MalformedSuggestionResponse`. Unsupported fields and invalid values are excluded independently. Missing/null/blank values are omitted, not clearing instructions. Nonblank text is preserved exactly; identical duplicates collapse, while conflicting nonblank values exclude that field. Providers must preserve duplicate entries before validation.

The result contains only usable field/value pairs and an outcome of `suggestions` or `no_usable_suggestions`. The caller must supply the IDs of current same-project members who are eligible for assignment under the existing assignment rules. QA Analysts and Developers are assignable, while Project Owners are not. An API-backed context test verifies this eligibility, excludes members from other projects, and rechecks eligibility after member removal. The validator itself performs no database access or persistence.

AC-019.1, AC-019.3, and AC-019.4 remain Partial: validation and configured endpoint integration are tested offline, but real provider compliance/factual quality, presentation, and browser verification remain outstanding. Unconfigured REQ-018 endpoints retain their unavailable response; no fake suggestions are returned in production. Validation tests are in `tests/test_ai_suggestions.py`.

The second REQ-019 slice adds `app/ai_context.py`, with separate `current_form`, `recent_bugs`, and `eligible_assignees` context sections. The submitted ten-field snapshot is copied exactly, including blanks and unsaved Edit values; history never fills or overwrites it. Project-scoped SQL retrieves at most five supporting bug reports, ordered by `updated_at DESC, id DESC`, excluding the current Edit bug before applying the limit. History contains only the ten suggestion-supported fields plus source bug ID; it is not verified fact for the current report. Assignee context contains only current same-project QA Analyst/Developer user IDs, emails, and roles. Owners, other-project members, and removed members are excluded; `eligible_assignee_ids` can be passed directly to the existing validator. No credentials, authentication tokens, or other user-account fields are queried into context.

Context construction runs after existing AI Assist authorization; the second slice retained the unconfigured provider boundary and HTTP 503. Context retrieval performs no writes. Tests in `tests/test_ai_context.py` verify transport to that boundary without simulating a provider, current-form preservation, project isolation, bounded deterministic history, member eligibility/removal, empty context, authorization-before-retrieval, and unchanged persisted bugs. AC-019.2 remains Partial: context construction and configured integration are API-tested, while real generation using that context, factual-support behavior, and browser verification remain pending.

The third REQ-019 slice adds the pure `build_generation_input(context)` function in `app/ai_generation.py`. It returns application-owned instructions, the three separate serialized context sections, and an output contract comprising the existing `suggestions` envelope schema plus field-specific value rules. Supported fields and classification values are reused from the validator; allowed assignee IDs come only from the supplied eligible members. Instructions identify the current form as primary, history as supporting/unverified, prohibit fabricated filler and application actions, allow zero suggestions, and require omission of unjustified fields. Context content remains untrusted data, separate from the instructions. The schema describes envelope structure; field rules and instructions guide generation, while the existing validator remains authoritative for all raw output.

Tests in `tests/test_ai_generation.py` verify context preservation/serialization, no mutation or database queries by the builder, supported fields, classification and assignee constraints, instruction boundaries, empty output, and no added account/configuration secrets. The builder does not select or invoke a provider and is not wired into the unavailable stub by this slice; endpoints retain their existing behavior. All REQ-019 ACs remain Partial because instruction tests do not establish provider compliance, real generated output, factual correctness, or browser coverage.

The fourth REQ-019 slice adds `process_provider_response(context, raw_response)` in `app/ai_response.py`. It passes the raw structured response unchanged to `validate_suggestions`, supplies only `context.eligible_assignee_ids`, and returns the existing `SuggestionResult` directly. Malformed structures propagate `MalformedSuggestionResponse`; valid output with no usable values retains the `no_usable_suggestions` outcome. Tests in `tests/test_ai_response.py` verify delegation, partial results, current eligibility rather than historical/provider-supplied IDs, duplicate conflicts, malformed versus empty outcomes, input preservation, and no database/provider/network access or persistence. That slice kept processing independent of the unavailable service; the sixth slice now uses it for configured endpoint results. All REQ-019 ACs remain Partial. Real provider execution/compliance, factual quality, REQ-020 review/use UI, and browser verification remain pending.

The fifth REQ-019 slice adds the independent `request_openai_suggestions(generation_input, client=...)` adapter in `app/ai_openai.py`, using OpenAI `gpt-6-luna`, the Responses API, and strict Structured Outputs with the existing application schema. The caller must inject a configured SDK client; the adapter does not read credentials or enable live endpoints. `requirements-ai.txt` pins the optional adapter SDK dependency to the tested `openai==3.23.0`; it is not a complete application dependency manifest. Application instructions and field rules are sent as trusted instructions, while the three permitted context sections are serialized into user input. No unrelated account/configuration data is added, no tools are enabled, and response storage is disabled with `store=False`.

Tests in `tests/test_ai_openai.py` use fake responses and an SDK client backed by in-memory HTTP transport, never live OpenAI requests. They verify request shape, context/instruction separation, schema reuse, no input mutation or database access, no live network requests in tests, no credentials in request context, raw duplicate/invalid/empty output preservation for the authoritative application validator, and propagation of request errors. Incomplete responses, refusals, and missing/unparseable JSON raise the adapter-specific `OpenAiSuggestionResponseError`; they never become fake or empty-success suggestions. This is minimal structured-output extraction, not the full REQ-023 failure-handling feature. The fifth slice kept the adapter independent; the sixth integrates it into `app/ai_triage.py`. All REQ-019 statuses remain Partial: real provider execution/compliance, factual-quality testing, REQ-020 UI, and browser verification remain outstanding. API syntax follows the official [Responses reference](https://developers.openai.com/api/reference/python/resources/responses/methods/create), [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs), and [GPT-6 Luna model page](https://developers.openai.com/api/docs/models/gpt-6-luna).

The sixth REQ-019 slice wires authorized New/Edit AI Assist requests through context, generation input, the OpenAI adapter, response processing, and the existing authoritative validator. `OPENAI_API_KEY` is read and trimmed per request; missing/blank configuration retains HTTP 503 with `AI assistance is not configured yet.` The SDK is loaded only for configured requests, clients are closed after each call, and automatic SDK retries are disabled. HTTP 200 returns only `SuggestionResult` semantics: `{"outcome": "suggestions", "suggestions": {"title": "..."}}` or `{"outcome": "no_usable_suggestions", "suggestions": {}}`. Provider/client failures and malformed suggestion structures return fixed safe HTTP 502 errors, never raw SDK details or empty-success results. Full REQ-023 timeout/recovery behavior remains deferred.

Tests in `tests/test_ai_triage.py` exercise this endpoint pipeline through the real SDK/adapter with in-memory HTTP transport, not live OpenAI calls. They cover authorization before pipeline work, exact current/unsaved form transport, QA/Developer eligibility and member removal, validator rejection of invalid/unsupported/conflicting fields, distinct empty outcomes, sanitized failures, unchanged persisted data, request-time configuration, and client cleanup. Existing unconfigured tests explicitly clear the key so a developer's environment cannot enable live requests in those tests. The existing JavaScript request/duplicate guard is unchanged and remains unit-tested. No REQ-020 UI has been added; successful suggestion presentation, real-model factual quality, and manual/browser verification remain pending. All REQ-019 statuses remain Partial.

Assignee eligibility is refreshed after generation and before authoritative validation, without changing the context already sent to the provider. New/Edit regression tests remove a QA Analyst or Developer during the simulated provider request and verify that the final suggestions exclude that assignee while retaining other valid fields. An offline SDK transport timeout test verifies safe HTTP 502 feedback, no exposed private details or application writes, one attempt with retries disabled, and client cleanup. Coverage statuses remain Partial; this does not implement full REQ-023 recovery.

## Coverage limitations from the pre-commit review

- User Stories remain in requirements.md. The previously noted missing REQ-005 user-story heading remains a specification follow-up; the matrix no longer contains US references, and no new ID is introduced here.
- Registration feedback, project-name display, member management, bug creation/list/detail/editing, and reassignment remain Partial where required browser verification is outstanding. Existing Manual entries record earlier manual verification, not automated UI coverage. AC-009.5 also lacks an explicit test of alphabetical ordering within a role.
- AC-003.3 is Partial: invalid-token coverage exists, but dedicated expired-token coverage is missing.
- Three function names are duplicated in test_projects.py: `test_non_owner_cannot_manage_project_members`, `test_non_owner_cannot_edit_project`, and `test_non_owner_cannot_delete_project`. Python collects only the last definition of each. The matrix inventories each collected name once; test cleanup is pending.
- The frontend validation helper was checked with 38 temporary simulated JavaScript handler/helper assertions, plus syntax checks. These checks are not a committed automated suite or visual browser evidence and do not complete UI coverage.

## BDD Specification Status

The current `.feature` files describe intended behaviour but are **not currently executable with pytest-bdd**.

They are therefore treated as behavioural specifications rather than automated tests.

Current feature files:

```text
tests/bdd/features/authentication.feature
tests/bdd/features/project_creation.feature
```

Executable BDD automation may be added later as a representative example rather than being used for the entire test suite.

The authentication feature still uses historical password AC references: all password-policy examples belong to AC-001.4 — Invalid Password, and password security belongs to AC-001.5 — Password Security. There are 17 scenarios across the two files, rather than the intended small representative showcase. Updating those specification files is deferred because this review does not change files under tests/.
