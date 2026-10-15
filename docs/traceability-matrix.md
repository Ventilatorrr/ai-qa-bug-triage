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
| REQ-005 | AC-005.1 — Successful Project Creation | `test_project_creation_preserves_padded_name` | API | Covered |
| REQ-005 | AC-005.1 — Successful Project Creation | `test_project_creation_submits_valid_name_unchanged` | Frontend unit | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name         | `test_create_project_with_empty_name`                  | API       | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name         | `test_project_creation_rejects_whitespace_only_name`     | API       | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name | `test_project_creation_rejects_non_string_name` | API | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name | `test_project_creation_blocks_blank_name_submission` | Frontend unit | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name | `test_project_creation_validation_feedback_tracks_input` | Frontend unit | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name | `test_project_creation_cancel_clears_form_feedback` | Frontend unit | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name | `test_project_creation_open_clears_previous_form_feedback` | Frontend unit | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name | `test_project_creation_preserves_unrelated_feedback` | Frontend unit | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name | `test_project_creation_server_validation_feedback_clears_on_correction` | Frontend unit | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name | `test_project_name_input_preserves_other_form_feedback` | Frontend unit | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name | BUG-20 Create feedback correction and form lifecycle (manual browser verification, 6 October 2026) | UI | Manual |
| REQ-005 | AC-005.3 — Unauthenticated User         | `test_unauthenticated_user_cannot_create_project`      | API       | Covered |

**Coverage note:** BUG-63 regression coverage rejects integer, boolean, array, object, and null names with HTTP 422 and no project creation. AC-005.2 remains Partial: preservation of unrelated network, authorization, service, loading, and page-level feedback has frontend-unit coverage using DOM substitutes, but was not part of the completed BUG-20 manual browser check.

BUG-20 manual browser verification reported by the user on 6 October 2026 passed: whitespace-only Create submission displays "Project name is required."; meaningful correction clears it without resubmission, while whitespace-only correction retains it; Cancel clears current form feedback; reopening New Project does not retain stale feedback; immediate Create success feedback does not remain when starting a fresh project-form interaction. Existing frontend-unit regression rows are preserved. Unrelated network, authorization, service, loading, and page-level feedback preservation remains frontend-unit-only evidence.

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
| REQ-007 | AC-007.1 — Successful Project Name Editing | `test_project_edit_preserves_padded_name` | API | Partial |
| REQ-007 | AC-007.1 — Successful Project Name Editing | `test_project_edit_submits_valid_name_unchanged` | Frontend unit | Partial |
| REQ-007 | AC-007.2 — Unauthorized Project Name Editing | `test_user_cannot_edit_another_users_project_name` | API / Security | Covered |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | `test_project_edit_rejects_empty_or_whitespace_only_name` | API | Partial |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | `test_project_edit_rejects_non_string_name` | API | Partial |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | `test_project_edit_blocks_blank_name_submission` | Frontend unit | Partial |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | `test_project_edit_validation_feedback_tracks_input` | Frontend unit | Partial |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | `test_project_edit_cancel_clears_form_feedback` | Frontend unit | Partial |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | `test_project_edit_open_clears_previous_form_feedback` | Frontend unit | Partial |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | `test_project_edit_preserves_unrelated_feedback` | Frontend unit | Partial |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | `test_project_edit_server_validation_feedback_clears_on_correction` | Frontend unit | Partial |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | `test_project_edit_success_clears_prior_validation_feedback` | Frontend unit | Partial |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | `test_project_name_input_preserves_other_form_feedback` | Frontend unit | Partial |
| REQ-007 | AC-007.3 — Invalid Project Name Editing | BUG-20 Edit feedback correction, successful Save, and Cancel/reopen (manual browser verification, 6 October 2026) | UI | Manual |

**Coverage note:** BUG-21 regression coverage rejects empty, spaces-only, and tab/newline names without changing the original name. Non-string names follow the same validation rule. BUG-20 manual browser verification reported by the user on 6 October 2026 passed: whitespace-only Edit/Save displays "Project name is required."; meaningful correction clears it, while whitespace-only correction retains it; successful Save updates the project name without retaining the old validation error; Cancel/reopen does not retain stale form feedback. AC-007.3 remains Partial: preservation of unrelated network, authorization, service, loading, and page-level feedback was not manually checked and remains frontend-unit-only evidence. Existing frontend-unit rows, including other-form feedback isolation, are preserved; blocked submissions and unchanged valid payloads retain their automated coverage. Backend validation behavior remains unchanged.

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
| REQ-011 | AC-011.1 — Successful Bug Creation | `test_bug_numbers_are_independent_and_routes_use_local_numbers` | API | Partial |
| REQ-011 | AC-011.1 — Successful Bug Creation | `test_deleted_bug_numbers_are_not_reused` | API | Partial |
| REQ-011 | AC-011.1 — Successful Bug Creation | `test_concurrent_creation_allocates_unique_bug_numbers` | API / Database | Partial |
| REQ-011 | AC — | `test_failed_creation_rolls_back_bug_and_counter` | API / Database | Covered |
| REQ-011 | AC — | `test_new_create_invalid_number_response_preserves_form` | Frontend unit | Partial |
| REQ-011 | AC-011.2 — Missing Bug Title | `test_bug_creation_rejected_without_title` | API / Validation | Partial |
| REQ-011 | AC-011.3 — Unauthorized Bug Creation | `test_non_member_cannot_create_bug` | API / Security | Covered |
| REQ-011 | AC-011.4 — Optional Bug Information | `test_bug_can_be_created_with_optional_information` | API / Validation | Partial |
| REQ-011 | AC-011.4 — Optional Bug Information | `test_bug_creation_allows_empty_fix_version` | API | Partial |
| REQ-011 | AC-011.4 — Optional Bug Information | `test_bug_creation_rejects_nonempty_fix_version` | API / Validation | Partial |

**Coverage note:** AC-011.4 includes the optional free-text Environment field. The automated creation test verifies that Environment can be supplied and returned correctly. Existing bug-creation tests that omit Environment also verify that the field remains optional.


### REQ-012 — Bug Access

| REQ | AC | Test Reference | Test Layer | Status |
|---|---|---|---|---|
| REQ-012 | AC-012.1 — View Bug List | `test_project_member_can_view_bug_list` | API | Partial |
| REQ-012 | AC — | `test_bug_list_rejects_invalid_number_response` | Frontend unit | Partial |
| REQ-012 | AC-012.2 — Open Bug Report | `test_project_member_can_open_bug_report` | API | Partial |
| REQ-012 | AC-012.2 — Open Bug Report | `test_public_bug_routes_use_local_number_and_isolate_projects` | API / AI Context | Partial |
| REQ-012 | AC-012.2 — Open Bug Report | `test_bug_details_and_deletion_use_local_resource_number` | Frontend unit | Partial |
| REQ-012 | AC-012.2 — Open Bug Report | `test_bug_detail_get_and_ai_assist_use_local_resource_number` | Frontend unit | Partial |
| REQ-012 | AC-012.2 — Open Bug Report | Temporary clickable-row diagnostics below; native Chrome link/selection and theme/focus checks pending | Frontend diagnostics / UI | Partial |
| REQ-012 | AC — | `test_bug_response_validates_project_and_local_resource_number` | Frontend unit | Partial |
| REQ-012 | AC — | `test_bug_number_query_rejects_invalid_missing_and_legacy_identity` | Frontend unit | Partial |
| REQ-012 | AC — | `test_bug_details_dividers_preserve_metadata_rows` | Native browser / actual markup and CSS | Covered |
| REQ-012 | AC-012.3 — Unauthorized Bug Access | `test_non_member_cannot_open_bug_report` | API / Security | Covered |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_bug_list_defaults_to_most_recently_updated_first` | API | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_bug_sort_first_visit_defaults_to_last_updated_descending` | Frontend unit | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_bug_sort_saves_column_and_direction_on_header_click` | Frontend unit | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_bug_sort_reinitialization_restores_order_indicators_and_links` | Frontend unit | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_bug_sort_restores_every_supported_column_and_direction` | Frontend unit | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_bug_sort_preferences_are_isolated_by_project` | Frontend unit | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_bug_sort_preferences_are_isolated_by_user` | Frontend unit | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_bug_sort_invalid_storage_falls_back_to_default` | Frontend unit | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_bug_sort_storage_failures_preserve_working_default_and_header_sorting` | Frontend unit | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_bug_sort_back_forward_refresh_preserves_preference` | Frontend unit | Partial |
| REQ-012 | AC — | `test_project_deletion_clears_only_current_users_project_sort_preference` | Frontend unit | Partial |
| REQ-012 | AC — | `test_failed_project_deletion_preserves_sort_preference` | Frontend unit | Partial |
| REQ-012 | AC — | `test_project_deletion_succeeds_when_sort_storage_is_unavailable` | Frontend unit | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | BUG-62 navigation/reload persistence and independent project preferences (manual browser verification, 6 October 2026) | UI | Manual |
| REQ-012 | AC-012.4 — Sort Bug Reports | — | UI | Partial |
| REQ-012 | AC-012.5 — Paginate Bug Reports | Temporary pagination diagnostics below; Chrome behavior/layout checks pending | Frontend diagnostics / UI | Partial |
| REQ-012 | AC-012.6 — Remember Bug Page Size | Temporary preference diagnostics below; Chrome persistence checks pending | Frontend diagnostics / UI | Partial |

**Clickable-row implementation and verification (9 October 2026):** Data rows navigate on ordinary left-clicks using their existing Bug ID anchor's `href`. Native anchors, interactive descendants, modifier/nonprimary clicks, prevented events, and noncollapsed text selection are left alone. Rows retain semantic table markup and no extra tab stops; pointer/hover styling uses existing theme variables, and the Bug ID link has an explicit focus outline. Pagination, sorting, API responses, and databases are unchanged. `node --test tests/frontend/*.test.cjs` passed 77 tests with 0 failures; `node --check frontend/js/project.js` and `git diff --check` passed. Nine temporary Node diagnostic groups outside the repository executed the actual renderer/handlers with DOM/API substitutes, covering ordinary row/cell navigation, reuse of the anchor destination, native-link exclusion, modifier/nonprimary/prevented events, selection guards, nested interactive controls, semantics, all seven sort columns in both directions, all pagination pages and 20/50 size changes, and refresh/empty-list recovery. These are not maintained regression tests or real-browser evidence. The isolated mock-data browser check timed out connecting to localhost, so native mouse/keyboard behavior, selection gestures, hover appearance, and both themes remain pending; AC-012.2 stays Partial. No repository test files or live/dogfooding data changed.

**Pagination implementation (9 October 2026):** Frontend-only pagination sorts the full list before slicing, defaults to 10, supports 20/50, resets on sort/size changes and project entry, and clamps the current page after data refresh. Single-page navigation and empty-list controls are hidden. Page size uses `bug-list-page-size:<user ID>` in localStorage; existing per-user/project sorting remains in sessionStorage. No backend, database, dependencies, or repository test files changed. Pagination has no maintained automated regression coverage in this slice; Python Playwright coverage remains deferred as requested. AC-012.5 and AC-012.6 remain Partial pending Chrome and broader browser/accessibility verification.

**Pagination verification:** `node --test tests/frontend/*.test.cjs` passed 77 tests with 0 failures; `node --check frontend/js/project.js` and `git diff --check` passed. A temporary script outside the repository executed the actual project script with DOM/API substitutes: 13 diagnostic groups passed covering sizes/ranges/navigation, all seven sort columns in both directions across all pages, sort/size resets, local-number links, unchanged source data, reload/project-entry defaults, per-user persistence through logout/login, separate sorting storage, invalid/blocked preference reads/writes, refresh with an added report, reduced/exact-boundary counts, empty-list recovery, and persisted Back/Forward entry. These are temporary diagnostics, not maintained tests or real-browser evidence. An isolated in-memory mock server was attempted, but the in-app browser connection timed out; no layout, theme, keyboard, or real-browser create/delete workflow verification is claimed. The live database and dogfooding reports were untouched.

**Coverage note:** AC-012.2 verifies Environment in the full bug-report response. AC-012.4 sorting is implemented for all seven columns in the browser, with initial Last Updated descending and missing optional values last in both directions. Severity uses Blocker, Major, Moderate, Minor from high to low; Priority uses Urgent, High, Medium, Low; Status follows the lifecycle order.

**Earlier sorting diagnostics:** The existing API default-order test passed (1 case). Temporary Node checks executed the actual page script with a simulated DOM and API response: initial order, all columns in both directions, case-insensitive text, null/undefined/empty values last, switching columns, indicators, focus restoration, unchanged rendered values and links, no sorting API requests or source-data mutation, refresh, and empty-list recovery passed. JavaScript syntax and diff checks passed. These older temporary diagnostics are distinct from the maintained BUG-62 frontend regression suite below and provide no visual browser evidence. AC-012.4 remains Partial pending broader browser/accessibility verification, including keyboard sorting, both themes, and layout. No manual test-case ID is assigned.

**BUG-62 regression coverage (historical, before BUG-12):** `tests/frontend/bug-sort-persistence.test.cjs` executes the actual page initialization, sort-header handlers, and table renderer with DOM/API substitutes. It covers first-visit defaults, saved column/direction, all seven columns in both directions, navigation/reload-style reinitialization, row order, arrow indicators, `aria-sort`, unchanged global bug IDs/links, project isolation, user isolation after logout, invalid JSON/values, blocked or missing storage, and back/forward refresh. Session preferences use `bug-list-sort:<user ID>:<project ID>` keys; successful project deletion removes only the current user's entry for that project, with failure/storage-error controls. Logout has no central session-data cleanup and remains unchanged; preferences stay isolated by user until the tab/session ends. Before the production change the focused suite had 6 failures and 6 passes; afterward all 12 tests passed. This is frontend-unit evidence, distinct from the manual browser results below. AC-012.4 stays Partial because broader browser/accessibility coverage remains outstanding. BUG-12 project-local display numbers remain deferred.

**BUG-62 manual browser verification:** The user reported successful verification on 6 October 2026: Title descending remained selected after opening a bug and returning with browser Back, navigating to Projects and reopening the same project, and reloading the project page. Displayed row order and the visible arrow/header state matched the selected sort. A second project retained a different preference; returning between the projects restored each project's own column and direction independently. Different signed-in user isolation, malformed/unavailable sessionStorage, and project-deletion cleanup were not manually checked and retain frontend-unit-only evidence. Keyboard sorting, both themes, and broader layout/accessibility behavior remain pending. This evidence does not establish completion of AC-012.4 or the increment.


**BUG-12 implementation evidence (7 October 2026):** Project-local numbers are implemented separately from internal global database identity. Following the approved public-identity refinement below, `project_id` plus `bug_number` identify the public resource. `tests/test_bug_numbers.py` verifies independent sequences starting at 1, non-reuse after deleting the highest/all reports, immutable numbers on edit, create/list/detail responses, ignored client-supplied numbers, distinct global IDs and project-scoped local-number routes, and rollback without consuming a number. Concurrent requests use a separate disposable database copied from the test database. Existing `tests/test_fix_version_on_pass.py` scenarios also assert that every fixture lifecycle transition and Passed/Failed result preserves the number, without changing Fix Version behavior.

The maintained frontend tests use deliberately different global IDs and local numbers. The existing sorting suite verifies displayed numbers, local-number links, numeric ordering in both directions, and compatibility with the saved `id` sort token. The existing current-Create session test verifies local-number success feedback; response-validation cases retain the form or reject a list with invalid numbers. `tests/frontend/bug-number-display.test.cjs` verifies the document title, detail reference, deletion feedback, local-number GET/DELETE/Edit AI Assist routes, query validation without a legacy `bug_id` fallback, and response identity matching by project and local number while retaining positive-integer validation of the internal global ID. These are frontend-unit checks, not browser appearance/accessibility evidence. AC-011.1, AC-012.1, AC-012.2, AC-012.4, AC-013.1 and AC-017.5 retain their existing Partial statuses. The earlier BUG-62 paragraph's BUG-12 deferral and global-link checks describe its historical state; historical BUG-12/BUG-62 references and evidence are preserved.

**BUG-12 approved public-identity refinement (7 October 2026):** Manual review prompted an intentional design refinement before commit, not a separate defect: browser query parameters and all project-scoped bug resource routes now use `bug_number`. `test_public_bug_routes_use_local_number_and_isolate_projects` parameterizes details, edit, status, delete and Edit AI Assist using global ID 6 versus local number 1, with two projects both holding BUG-1. It verifies rejection of an existing global ID as a missing local number, correct same-number project resolution, unchanged other-project data, and AI history/exclusion using global IDs after public-resource resolution. The existing AI Assist fixture now deliberately separates global ID from local number across authorization, status, transport and offline-provider tests. Existing API/lifecycle/project-deletion tests use public local numbers; the frontend Edit/Pass/Fail/lifecycle fixtures also use distinct identities and retain existing workflow assertions. The allocator, schema version 1, migration and AI context/history internals are unchanged. Final manual browser verification of this refined design passed, as recorded below; no coverage status is upgraded.

**BUG-12 final manual browser verification (7 October 2026):** The user reported successful verification in the real browser. Existing project bug links displayed project-local BUG numbers and opened `/bugs.html?project_id={project_id}&bug_number={bug_number}`, with no global database ID exposed in frontend navigation. Refreshing that details URL loaded the same bug; bug details and the browser title displayed its local BUG number. Editing through the local-number URL succeeded and retained the same URL/resource number. A normal lifecycle transition succeeded using that resource. Project-page links continued using local numbers, Bug ID sorting remained numeric by the displayed local number, and overall browser behavior looked correct after the public-identity refinement. Browser navigation uses `project_id` plus `bug_number`; global `bugs.id` remains internal implementation identity.

The real schema migration had already been independently verified by the earlier read-only inspection: version 1, clean integrity/foreign-key checks and valid project-local numbering. No new schema migration was required for this routing refinement. This browser evidence covers the checks reported above; manual AI Assist provider execution is not claimed. Broader role/lifecycle and accessibility coverage, including keyboard sorting, both themes and broader layout behavior, remains incomplete. AC-011.1, AC-012.1, AC-012.2, AC-012.4, AC-013.1 and AC-017.5 retain their existing Partial statuses.

Refinement test-first execution observed **18 Python failures / 28 passes** before production changes. One initial failure was an incorrect test stub constructor; after correcting that stub, its isolated AI Assist case failed on the intended routing assertion (global-ID addressing incorrectly returned HTTP 200 instead of 404). The focused frontend run observed **16 failures / 23 passes** before production changes.

Refinement automated verification:

- `.\.venv\Scripts\python.exe -m pytest tests/test_bug_numbers.py tests/test_bug.py tests/test_ai_assist.py tests/test_ai_context.py tests/test_ai_triage.py tests/test_fix_version_on_pass.py tests/test_projects.py -q --tb=short` — **293 passed in 253.76 seconds**, using disposable databases.
- `.\.venv\Scripts\python.exe -m pytest -q --tb=short` — **510 passed in 272.15 seconds**, run serially against disposable test databases.
- `node --test tests/frontend/bug-number-display.test.cjs tests/frontend/bug-sort-persistence.test.cjs tests/frontend/form-session.test.cjs tests/frontend/fix-version-on-pass.test.cjs tests/frontend/lifecycle-action-disabled-state.test.cjs tests/frontend/ai-assist.test.cjs` — **60 passed, 0 failures**.
- `node --test tests/frontend/*.test.cjs` — **76 passed, 0 failures**.
- `node --check frontend/js/project.js` and `node --check frontend/js/bugs.js` — passed.

The refinement's `git diff --check` passed. The real `bugtriage.db` fingerprint remained unchanged during this refinement; no real database writes, application startup or migration was performed by the agent. The separate edit/status post-commit response-readback concurrency concern and global SQLite ID reuse remain out of scope.

### REQ-013 — Bug Editing

| REQ | AC | Test Reference | Test Layer | Status |
|---|---|---|---|---|
| REQ-013 | AC-013.1 — Edit Bug Report | `test_project_member_can_edit_bug_report` | API | Partial |
| REQ-013 | AC-013.1 — Edit Bug Report | `test_bug_number_is_preserved_on_edit` | API | Partial |
| REQ-013 | AC-013.2 — Optional Bug Information | `test_project_member_can_update_optional_bug_information` | API / Validation | Partial |
| REQ-013 | AC-013.2 — Optional Bug Information | `test_unresolved_bug_edit_rejects_nonempty_fix_version` | API / Validation | Partial |
| REQ-013 | AC-013.2 — Optional Bug Information | `test_unresolved_bug_edit_clears_legacy_fix_version` | API | Partial |
| REQ-013 | AC-013.2 — Optional Bug Information | `test_closed_fixed_bug_fix_version_can_be_edited_and_cleared` | API | Partial |
| REQ-013 | AC-013.2 — Optional Bug Information | `test_nonfixed_bug_edit_clears_legacy_fix_version` | API | Partial |
| REQ-013 | AC-013.3 — Unauthorized Bug Editing | `test_non_member_cannot_edit_bug_report` | API / Security | Covered |
| REQ-013 | — | `test_bug_update_rejected_with_null_title` | API / Validation | Covered |
| REQ-013 | AC — | `test_bug_update_response_readback_after_commit` | API / Database Integration | Covered |

**Coverage note:** AC-013.2 includes updating the optional free-text Environment field.

**Additional regression coverage:** An explicit null title is rejected with HTTP 422 and “Bug title is required.” The test verifies through the API that the bug report remains unchanged. This covers API validation only; it does not establish UI coverage or completion of REQ-013.


### REQ-014 — Bug Deletion

| REQ | AC | Test Reference | Test Layer | Status |
|---|---|---|---|---|
| REQ-014 | AC-014.1 — Successful Bug Deletion | `test_authorized_member_can_delete_bug` | API | Partial |
| REQ-014 | AC-014.1 — Successful Bug Deletion | `test_bug_deletion_requires_confirmation_and_preserves_cancelled_report` | Frontend unit / actual Delete handler | Partial |
| REQ-014 | AC — | `test_destructive_buttons_preserve_focus_and_disabled_states` | Native browser / actual markup and CSS | Covered |
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
| REQ-017 | AC-017.2 — Triage to Open | `test_move_to_open_requires_eligible_selection_and_resets_after_transition` | Frontend unit | Partial |
| REQ-017 | AC-017.2 — Triage to Open | — | UI | Partial |
| REQ-017 | AC-017.2 — Triage to Open | Lifecycle disabled-state: empty/cleared selection, eligible QA/Developer, successful transition (user-reported browser verification) | Manual / Browser | Partial |
| REQ-017 | AC-017.3 — Open to Development | `test_project_owner_can_move_bug_from_open_to_development` | API | Partial |
| REQ-017 | AC-017.3 — Open to Development | `test_open_to_development_requires_valid_developer_assignee` | API / Validation | Partial |
| REQ-017 | AC-017.3 — Open to Development | `test_qa_analyst_cannot_move_bug_from_open_to_development` | API / Security | Partial |
| REQ-017 | AC-017.3 — Open to Development | `test_non_assigned_developer_cannot_move_bug_from_open_to_development` | API / Security | Partial |
| REQ-017 | AC-017.3 — Open to Development | `test_move_to_development_requires_developer_selection_and_resets_after_transition` | Frontend unit | Partial |
| REQ-017 | AC-017.3 — Open to Development | — | UI | Partial |
| REQ-017 | AC-017.3 — Open to Development | Lifecycle disabled-state: empty/cleared/non-Developer selection, valid Developer, successful transition (user-reported browser verification) | Manual / Browser | Partial |
| REQ-017 | AC-017.4 — Development to Testing | `test_assigned_developer_can_move_bug_from_development_to_testing` | API | Partial |
| REQ-017 | AC-017.4 — Development to Testing | `test_project_owner_can_move_bug_from_development_to_testing` | API | Partial |
| REQ-017 | AC-017.4 — Development to Testing | `test_non_assigned_developer_cannot_move_bug_from_development_to_testing` | API / Security | Partial |
| REQ-017 | AC-017.4 — Development to Testing | `test_bug_cannot_move_to_testing_with_developer_assignee` | API / Validation | Partial |
| REQ-017 | AC-017.4 — Development to Testing | `test_send_to_testing_and_close_retain_required_selection_behavior` | Frontend unit | Partial |
| REQ-017 | AC-017.4 — Development to Testing | — | UI | Pending |
| REQ-017 | AC-017.4 — Development to Testing | Lifecycle disabled-state regression: Send to Testing requires QA selection (user-reported browser verification) | Manual / Browser | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_assigned_qa_can_pass_bug_and_close_it` | API | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_project_owner_can_pass_bug_and_close_it` | API | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_assigned_qa_can_fail_bug_and_return_it_to_development` | API | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_project_owner_can_fail_bug_and_return_it_to_development` | API | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_failed_testing_requires_valid_developer_assignee` | API / Validation | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_non_assigned_qa_cannot_record_testing_outcome` | API / Security | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_testing_outcome_is_required` | API / Validation | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_invalid_testing_outcome_is_rejected` | API / Validation | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_passed_transition_persists_optional_fix_version` | API | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_failed_transition_clears_legacy_fix_version` | API | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_fix_version_is_rejected_outside_passed_transition` | API / Validation | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_passed_fix_version_preserves_authorization` | API / Security | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_passed_fix_version_input_visible_and_sends_value` | Frontend unit | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_passed_fix_version_respects_eligibility` | Frontend unit | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_failed_flow_does_not_use_fix_version` | Frontend unit | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | — | UI | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | Fix Version on Pass: blank value, prefill/replacement, Failed preservation, and Pass/Fail labels (user-reported browser verification) | Manual / Browser | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | Lifecycle disabled-state regression: Pass/Fail and Fix Version behavior remain intact (user-reported browser verification) | Manual / Browser | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_assigned_developer_can_close_bug_without_fixing` | API | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_project_owner_can_close_bug_without_fixing` | API | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_nonfixed_closure_clears_fix_version_and_rejects_assignment` | API / Validation | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_non_assigned_developer_cannot_close_bug_without_fixing` | API / Security | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_bug_cannot_be_closed_without_resolution` | API / Validation | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_fixed_resolution_cannot_be_manually_selected_when_closing_bug` | API / Validation | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_send_to_testing_and_close_retain_required_selection_behavior` | Frontend unit | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | — | UI | Pending |
| REQ-017 | AC-017.6 — Close Without Fixing | Lifecycle disabled-state regression: Close requires resolution selection (user-reported browser verification) | Manual / Browser | Partial |
| REQ-017 | AC-017.7 — Closed Bugs | `test_project_owner_can_move_closed_bug_to_triage` | API | Partial |
| REQ-017 | AC-017.7 — Closed Bugs | `test_reopening_clears_resolution_and_fix_version` | API | Partial |
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

Lifecycle disabled-state coverage in `tests/frontend/lifecycle-action-disabled-state.test.cjs` runs the actual page script with DOM/request substitutes. Move to Open requires a selected project QA Analyst or Developer; Move to Development requires a selected project Developer under the existing actor rules. Tests cover initial empty selection, valid selection, clearing/ineligible selection, defensive validation without a request, unchanged valid payloads, and control reset after transitions. Send to Testing and Close retain their required-selection behavior. Existing automated and Fix Version on Pass evidence is unchanged.

**BUG-25 — Lifecycle controls after transitions:** After the refreshed details, final lifecycle-control render, and success message have rendered, the shared `submitLifecycleTransition` success path checks both the last rendered lifecycle button and the existing, visible `#bug-message`, including disabled buttons and excluding buttons in hidden groups. Scrolling is skipped only when both full rectangles are within the viewport, regardless of the desired gap. If either is partially or completely outside the viewport, `#bug-message` is scrolled into view with bottom alignment. Its 16 px bottom scroll margin supplies the desired gap without changing page layout; native scrolling uses the nearest achievable position when constrained by document/viewport limits. This applies to all seven supported transition paths, including Passed, Failed, non-Fixed closure, and reopening. With no visible lifecycle button or feedback, no scrolling is attempted. Validation, authorization, network, invalid-response, and refresh-failure paths do not scroll; initial loading, navigation, ordinary editing, and page refresh do not use the transition-only scroll. An API availability guard skips optional scrolling in DOM substitutes without native scrolling methods. Genuine browser verification of this experimental button-and-message visibility condition remains pending, so AC-017.1 and the affected lifecycle ACs remain Partial. No CommonJS test files were changed.

BUG-25 verification: `node --test tests/frontend/*.test.cjs` passed **77/77 tests** without temporary monkeypatches or test-file changes. The API guard resolves the five previous missing-method failures in the DOM substitute. `node --check frontend/js/bugs.js` and `git diff --check` passed. Thirteen one-off simulated visibility checks passed, covering viewport edges, offscreen buttons, hidden groups, disabled buttons, hidden feedback, and missing native scrolling APIs; the 16 px scroll margin was also confirmed by source inspection. These checks do not establish browser layout, native scrolling, the final gap, or document-limit behavior. Genuine browser verification remains pending. No pytest run was needed because backend behavior and Python code are unchanged.

Manual browser verification of this disabled-state fix reported by the user passed: Move to Open is disabled with no assignee, enables for an eligible QA Analyst or Developer, and disables again when cleared; valid Triage-to-Open transitions succeed. Move to Development stays disabled for empty or non-Developer selections, enables for a valid Developer, and disables again when cleared; valid Open-to-Development transitions succeed. Regression checks confirmed Send to Testing remains disabled until a QA Analyst is selected, Close remains disabled until a resolution is selected, and Pass/Fail and Fix Version behavior remain intact. This evidence covers the verified selection behavior; broader lifecycle UI/accessibility coverage remains incomplete and the affected ACs remain Partial.

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

Closed has no normal forward lifecycle transition. A Project Owner may return a Closed bug to Triage; the transition clears Resolution and Fix Version in the same database update, preserves its assignee, and restores the normal lifecycle and assignment rules.

The Project Owner Closed-to-Triage test also verifies that Last Updated changes during the transition.

AC-017.5 optional Fix Version coverage is maintained in `tests/test_fix_version_on_pass.py` and `tests/frontend/fix-version-on-pass.test.cjs`. Parameterized API cases verify Passed with supplied, unchanged, replaced, omitted, null, empty, and untrimmed values, with GET readback; omitted values preserve a stored legacy version and explicit null clears it. Legacy unresolved versions are seeded only in the disposable test database because creation now rejects them. Status, resolution, and Fix Version are persisted in the same database update. Failed clears any legacy version; other transitions still reject supplied Fix Version, and existing authorization remains enforced. Existing frontend unit tests exercise the actual page script with DOM/request substitutes: the optional Pass input, prefill and eligibility, direct Passed submission with value/null payloads, and unchanged Failed requests. Their stubbed Failed response still preserves a legacy value and is not evidence of current backend persistence behavior. The existing frontend test also checks one associated semantic label with the exact text "Fix Version (optional)" inside the control, a blank placeholder for CSS empty-state detection, and no competing accessible label. CSS positions the label like a placeholder when empty and unfocused, floats it when focused or populated, and centers the value while preserving the existing width and total vertical padding.

**Fix Version lifecycle correction (8 October 2026):** REQ-011/013/017 API regression coverage now checks rejection of premature assignments (including no partial edit or consumed creation number), allowed empty values, editing/clearing Closed/Fixed versions, all non-fix resolutions, and reopen readback with both fields cleared and Affected Version preserved. Ordinary edits and transitions outside Closed/Fixed clear legacy values without a migration. New Bug no longer renders or submits Fix Version; ordinary Edit Bug and bug details show it only for Closed/Fixed, with edit eligibility and values reset whenever the form is populated. The readback regression retains both edit/status branches and deleted-between-commit-and-readback behavior, using Affected Version as the populated unchanged optional field. The AI-context regression seeds a legacy Fix Version only in the disposable database to preserve its exclusion/non-persistence checks. No CommonJS tests were changed. Browser verification of the new visibility, stale-value prevention, and lifecycle rules remains pending; affected ACs remain Partial.

Verification for this correction, using disposable databases serially:

- Before the backend correction, `.\.venv\Scripts\python.exe -m pytest tests/test_fix_version_on_pass.py -q --tb=short -k 'creation_rejects or unresolved_bug_edit_rejects or reopening_clears or nonfixed_closure'` — **11 failed, 39 deselected in 20.53 seconds**, demonstrating the original defects.
- Initial wider focused run, `.\.venv\Scripts\python.exe -m pytest tests/test_fix_version_on_pass.py tests/test_bug_update_readback.py tests/test_bug.py tests/test_ai_context.py -q --tb=short` — **191 passed, 2 failed in 216.06 seconds**. Both failures were new test assertions comparing list responses with full detail responses; these assertions were corrected.
- `.\.venv\Scripts\python.exe -m pytest tests/test_fix_version_on_pass.py tests/test_bug_update_readback.py -q --tb=short` — **54 passed in 67.04 seconds**, including the corrected cases.
- `.\.venv\Scripts\python.exe -m pytest -q --tb=short` — **544 passed in 346.63 seconds**.
- `node --test tests/frontend/*.test.cjs` — **77 passed, 0 failures**. These are existing unit tests with DOM/request substitutes; they do not establish browser visibility or appearance verification of the new rules.
- `node --check frontend/js/project.js`, `node --check frontend/js/bugs.js`, and `git diff --check` — passed.

Manual browser appearance verification of the Fix Version floating-label enhancement reported by the user passed: an empty field shows "Fix Version (optional)" centered inside the control; a populated field keeps the small persistent label visible and centers the entered version value. In both states, the label uses normal font style and the same subdued grey/placeholder-style color as nearby lifecycle controls. Control dimensions remain visually consistent with the previous layout, and Pass / Fail and Fix Version behavior remain unchanged. AC-017.5 remains Partial because broader lifecycle/accessibility coverage is incomplete; all existing automated evidence is preserved.

Historical manual browser verification of the Fix Version on Pass enhancement reported by the user passed: a Testing bug with blank Fix Version immediately showed the input with its associated semantic label "Fix Version (optional)" in a placeholder-like position and the Pass button; blank did not block a single Pass click, which closed the bug as Fixed and left Fix Version blank. An existing Fix Version was prefilled; changing it and clicking Pass once persisted the new value and closed the bug as Fixed. The Developer selector remained unchanged; Fail returned the bug to Development with the selected Developer as assignee and preserved the existing Fix Version. That preservation observation predates the 8 October lifecycle correction and is superseded by the clearing requirement above. The visible action labels were Pass and Fail. AC-017.5 remains Partial because current lifecycle browser/accessibility verification is incomplete.

AC-017.1 through AC-017.8 remain Partial because broader lifecycle browser/accessibility verification and automated UI coverage are incomplete. The lifecycle UI includes closure outcomes and the Project Owner's return-to-Triage action, but the project does not yet have a frontend browser-test framework. AC-017.9 is Covered at the API layer because it specifies timestamp behavior rather than a separate browser interaction.

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

The second slice adds POST `/projects/{project_id}/ai-assist` and the Edit AI Assist endpoint, now addressed as POST `/projects/{project_id}/bugs/{bug_number}/ai-assist` after the BUG-12 public-identity refinement (originally `{bug_id}`). Both accept a complete ten-field current-form snapshot, including empty text and a nullable assignee ID, without saving bug data. Edit requests never fill missing fields from stored bug values. Authorization checks current membership, role, and (for Edit) the bug's project and current Triage status before the service boundary is called. The public local number resolves to the internal global ID for existing AI context/history and edited-report exclusion. Its original tests retain the unconfigured HTTP 503 behavior. The sixth REQ-019 slice integrates configured backend results and safe provider errors with offline API tests. AC-018.1 through AC-018.4 remain Partial overall; REQ-020 now presents generated outcomes with unit and browser smoke evidence recorded below.

API tests are in `tests/test_ai_assist.py` and `tests/test_ai_triage.py`. Dependency-free JavaScript unit tests run with `node --test tests/frontend/ai-assist.test.cjs` and exercise form collection, request transport, and the REQ-020 review workflow using small DOM/control substitutes. The REQ-020 section records current browser smoke evidence separately. Real-model evaluation remains deferred.


## REQ-019 — Validated AI Suggestions

The slice notes below describe the implementation and evidence at each earlier checkpoint. REQ-020 review/use presentation is now implemented; its current evidence and remaining gaps are recorded in the REQ-020 section. Real-model compliance and factual-quality evaluation remain outstanding.

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

**Technical coverage note:** `test_ai_triage_client_factory_disables_retries_without_reading_credentials` already has an exact-name entry above. It supports REQ-019's provider integration as configuration evidence: the factory passes the supplied key, a 60-second timeout, and disabled SDK retries to the constructor. No existing AC specifies those constructor settings, so the AC remains unassigned. This unit test does not establish end-to-end timeout handling or real-provider behavior.

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

## REQ-020 — Review and Use AI Suggestions

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| REQ-020 | AC-020.1 — Review Suggestions | `test_ai_suggestions_review_separates_values_and_follows_form_order` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.1 — Review Suggestions | `test_ai_review_tracks_current_values_after_manual_edits` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.2 — Use an Individual Suggestion | `test_ai_use_replaces_value_removes_pending_and_remains_editable` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.2 — Use an Individual Suggestion | `test_ai_validated_assignee_missing_from_dropdown_is_reviewable_and_usable` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.3 — Dismiss an Individual Suggestion | `test_ai_dismiss_preserves_form_and_excludes_field_from_use_all` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.4 — Use All Pending Suggestions | `test_ai_use_all_applies_only_pending_values_without_reapplying_used_fields` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.5 — Dismiss All Pending Suggestions | `test_ai_dismiss_all_preserves_used_and_other_form_values` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.6 — Repeat AI Assist Requests | `test_ai_repeat_request_waits_for_resolution_and_uses_latest_form` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.7 — Persist Changes Through Existing Form Actions | `test_ai_use_all_maps_every_supported_field_without_persistence` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_ai_cancel_discards_pending_and_detached_actions_cannot_apply` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_ai_late_success_or_error_cannot_populate_reopened_session` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_ai_late_json_cannot_replace_later_results` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_ai_results_do_not_populate_hidden_or_disconnected_forms` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_ai_sessions_are_isolated_between_new_and_edit_forms` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC — | `test_ai_no_usable_suggestions_is_success_and_allows_manual_work_and_retry` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC — | `test_ai_failed_or_malformed_responses_preserve_form_and_allow_retry` | Unit (JavaScript / DOM substitutes) | Partial |
| REQ-020 | AC-020.1 — Review Suggestions | New/Edit field comparisons, field order, separate values, and review controls | Manual / Browser Smoke | Partial |
| REQ-020 | AC-020.2 — Use an Individual Suggestion | New/Edit replacement and subsequent normal editing | Manual / Browser Smoke | Partial |
| REQ-020 | AC-020.3 — Dismiss an Individual Suggestion | New Bug dismissal followed by Use All preserves the dismissed field | Manual / Browser Smoke | Partial |
| REQ-020 | AC-020.4 — Use All Pending Suggestions | New/Edit bulk use; New Bug preserves revised used values and dismissed fields | Manual / Browser Smoke | Partial |
| REQ-020 | AC-020.5 — Dismiss All Pending Suggestions | New/Edit bulk dismissal preserves previously used values | Manual / Browser Smoke | Partial |
| REQ-020 | AC-020.6 — Repeat AI Assist Requests | Disabled AI Assist until resolution; repeat requests after bulk resolution | Manual / Browser Smoke | Partial |
| REQ-020 | AC-020.7 — Persist Changes Through Existing Form Actions | Disposable database check before Create; Create, Save, Edit Cancel, unchanged Save, and blank-title Edit validation | Manual / Browser + Database Smoke | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | New/Edit delayed success after Cancel/reopen; Edit reload and navigation discard pending review | Manual / Browser Smoke | Partial |

REQ-020 is implemented in the shared `frontend/js/ai-assist.js` helper and wired into both pages. Pending values are held only in a form-session WeakMap, displayed with their current form values in form order, and rendered with `textContent` so suggested markup is literal text. Only the ten supported fields can be mapped to the form. Use replaces an ordinary field value and removes the pending entry; bulk actions iterate only the remaining entries. No suggestion action calls a persistence endpoint or stores pending values in browser storage. AI Assist remains disabled until the set is resolved. Empty successes and errors leave normal form values unchanged and allow retry. Session identity and request IDs guard both response arrival and asynchronous JSON processing; cancellation, successful form completion (including unchanged Edit Save), and `pagehide` invalidate the session. A cached-page `pageshow` starts a fresh review session without restoring pending values. Existing backend authorization and validation are unchanged.

Verification on 5 October 2026: `node --test tests/frontend/ai-assist.test.cjs` passed all 19 tests (the original three request/context tests plus 16 review tests); the complete serial `.\.venv\Scripts\python.exe -m pytest` run passed 425 cases in 238.67 seconds. A temporary Node check against the original helper from HEAD reproduced the successful-response error before correction. Unit tests use DOM substitutes and do not establish full browser workflows or real persistence. No browser-test framework or dependency was introduced.

A backend-validated Assignee ID missing from the form's older dropdown is displayed as `User <ID>` and added as a selectable option only when used. This avoids discarding a valid response or silently clearing the select if membership changes after the form opens. Create/Save still revalidates assignment through the unchanged backend. This final edge case is unit-tested in both form modes; it was added after the browser smoke run and has no separate browser evidence.

Manual/browser smoke verification used the Codex in-app browser, an isolated local server, disposable `req020_browser_test.db`, and mocked AI output processed by the existing validator. No real provider calls, migrations against application data, or dogfooding records were used. Project Owner and QA Analyst paths were exercised. New/Edit checks covered success, empty success, safe failure, retry, ordinary editing, and a delayed response after cancellation/reopening. New Bug review/use actions left the database with only the original report until normal Create; Create then displayed the revised used title. Edit Cancel restored stored values; Save persisted the revised title while dismissed fields retained their stored values. Edit Save with no changes discarded pending suggestions; ordinary blank-title validation remained active after Use All. Pending Edit suggestions were discarded on reload and navigation. Script-like and multiline suggestions displayed as literal text. The panel was visually checked at the browser's narrow viewport in dark and light themes, with visible keyboard focus; a low-contrast issue in the new dark panel was corrected and rechecked. No unrelated application defects were discovered. The temporary verification server/scripts/database were removed after testing.

All REQ-020 ACs remain Partial for coverage: there is no committed automated browser suite, desktop/cross-browser verification and a full accessibility review remain outstanding, and the browser's cached-page restoration branch was not independently forced. Browser smoke evidence is separate from JavaScript automation. Real-provider factual quality and full REQ-023 recovery remain outside this slice. This does not establish Increment 3 completion under the Definition of Done.

The same panel implements AC-021.1 — Identify Pending AI Suggestions. Its dedicated REQ-021 traceability section below reuses this implementation and evidence without expanding backend AI scope.

## REQ-020 logged defect corrections — 5 October 2026

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| REQ-020 | AC-020.2 — Use an Individual Suggestion | `test_ai_native_text_input_mismatches_are_excluded_before_use_or_use_all` | Unit (JavaScript / input sanitization model) | Partial |
| REQ-020 | AC-020.4 — Use All Pending Suggestions | `test_ai_native_text_input_mismatches_are_excluded_before_use_or_use_all` | Unit (JavaScript / input sanitization model) | Partial |
| REQ-020 | AC — | `test_ai_all_native_input_mismatches_allow_manual_work_and_retry` | Unit (JavaScript / input sanitization model) | Partial |
| REQ-020 | AC-020.2 — Use an Individual Suggestion | `test_ai_native_input_browser_review_and_apply_consistency` | Browser (native controls; manually triggered assertions) | Partial |
| REQ-020 | AC-020.4 — Use All Pending Suggestions | `test_ai_native_input_browser_review_and_apply_consistency` | Browser (native controls; manually triggered assertions) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_new_create_late_success_preserves_reopened_form_and_ai` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_edit_save_late_success_preserves_reopened_form_and_ai` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC-020.7 — Persist Changes Through Existing Form Actions | `test_new_create_current_success_closes_form_and_discards_ai` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC-020.7 — Persist Changes Through Existing Form Actions | `test_edit_save_current_success_closes_form_and_discards_ai` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_new_create_late_error_does_not_overwrite_reopened_messages` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_edit_save_late_error_does_not_overwrite_reopened_messages` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_new_create_late_json_preserves_newer_pending_submission` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_edit_save_late_json_preserves_newer_pending_submission` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC — | `test_edit_save_late_rejection_preserves_newer_session` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_new_create_stale_list_refresh_failure_preserves_newer_feedback` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC-020.7 — Persist Changes Through Existing Form Actions | `test_new_create_current_list_refresh_failure_shows_error` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_new_create_delayed_list_refresh_response_preserves_newer_session` | Unit (actual page handlers / DOM substitutes) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_new_create_delayed_list_refresh_json_preserves_newer_session` | Unit (actual page handlers / DOM substitutes) | Partial |

REQ-019 continues to preserve backend-valid nonblank text exactly. Before review,
the frontend assigns each text suggestion to a detached clone of its actual form
control. It excludes values that native sanitization would change; usable values
from the same response remain reviewable. All excluded values produce the normal
no-usable-suggestions notice and permit retry. This changes neither backend
validation nor authoritative bug persistence, and adds no multiline form fields.

Create and Save now capture separate form-session and submission identities.
Cancel, reopen, and page departure invalidate authority over later forms. Stale
Create success still refreshes the bug list; stale Save success fetches current
server details without changing an open edit form's values, comparison baseline,
AI session, visibility, messages, or newer Save's disabled state. Current-session
success keeps the existing normal cleanup and persistence behavior.

Create's list refresh captures feedback ownership after successful cleanup
advances the form session. The actual `loadBugs()` function rechecks that ownership
immediately before writing an error, after both response and JSON completion.
Already-stale submissions stay silent; current refresh errors are still reported
when no newer session has opened. Other `loadBugs()` callers retain their normal
feedback behavior, and successful refreshes still update surrounding list data.
The two delayed-refresh regressions use the actual Create handler, `loadBugs()`,
and feedback function with controlled responses. Both failed before the production
fix because older refresh errors replaced newer validation feedback; the existing
32 tests passed. After correction, both response and JSON delay cases preserve
newer form values, validation feedback, AI feedback, pending suggestions, and
visibility. They also verify normal Create cleanup and successful list refreshes.
The earlier stale/current refresh tests now exercise the actual refresh function
rather than an immediate refresh substitute. This is Node execution with DOM
substitutes, not additional browser verification.

Before correction, the regression run had 6 failures among 27 Node tests: both
native-input-model regressions and the New/Edit stale success/error regressions.
After correction and additional delayed-JSON/rejection coverage,
`node --test tests/frontend/ai-assist.test.cjs tests/frontend/form-session.test.cjs`
passed all 34 tests (21 AI-helper tests, 13 form/page-session tests). The full serial
`.\.venv\Scripts\python.exe -m pytest` run passed **425 tests in 226.83 seconds (3m 46s)**
after the delayed-refresh ownership fix.
JavaScript syntax checks and `git diff --check` passed.

The committed static browser runner (`node tests/frontend/native-input-server.cjs`,
then open `http://127.0.0.1:8128/`) passed all 12 native cases using actual New/Edit
form markup: Use/Use All with LF, CR, and CRLF suggestions for Title, Affected
Version, and Environment. Unrepresentable suggestions were excluded before
review; the remaining textarea value matched the reviewed value when applied,
and excluded fields were unchanged.

Focused full-page browser verification used the Codex in-app browser, a disposable
`req020_fix_browser_test.db`, and mocked AI responses processed by the unchanged
validator. Delayed New Create followed by Cancel/reopen preserved newer values,
pending suggestions, and form visibility while the persisted report appeared in
the refreshed list. Delayed Edit Save followed by Cancel/reopen likewise preserved
newer title/environment values, pending suggestions, form visibility, and enabled
Save. Holding the HTTP PATCH open serializes the browser's same-URL reopen GET;
the Edit harness therefore delayed JavaScript completion after the actual PATCH
persisted to exercise the specified sequence. Current Create and Save then
persisted the newer values normally; individual Use and Use All preserved reviewed
textarea content. No real records or provider calls were used. Temporary server
and database files were removed after verification.

No additional application defect was confirmed. REQ-020 coverage remains Partial:
the native assertions cover this defect, not complete automated browser workflows.
Cross-browser, full accessibility, and independently forced cached-page restoration
verification remain outstanding. No requirements, API contract, provider, or UI
design decisions changed. This slice does not establish Increment 3 completion.

## REQ-021 — Identify AI Suggestions

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| REQ-021 | AC-021.1 — Identify Pending AI Suggestions | `test_ai_suggestions_review_separates_values_and_follows_form_order` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-021 | AC-021.1 — Identify Pending AI Suggestions | `test_ai_pending_guidance_uses_bottom_status_and_clears_after_review` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-021 | AC-021.1 — Identify Pending AI Suggestions | `test_ai_use_replaces_value_removes_pending_and_remains_editable` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-021 | AC-021.1 — Identify Pending AI Suggestions | `test_ai_use_all_applies_only_pending_values_without_reapplying_used_fields` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-021 | AC-021.1 — Identify Pending AI Suggestions | `test_ai_use_all_maps_every_supported_field_without_persistence` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-021 | AC-021.1 — Identify Pending AI Suggestions | New/Edit labelled review area, separate current/suggested values, and individual/bulk use (REQ-020 smoke evidence above, 5 October 2026) | Manual / Browser Smoke | Covered |

REQ-021 was already implemented by the merged REQ-020 work. Both page forms
provide a separate suggestion section; the shared helper renders the exact heading
`AI Suggestions`, associates the section with that heading, and keeps pending
values in review cards and session state. Rendering does not assign suggestions
to editable controls. Only Use or Use All transfers them into ordinary fields;
used or dismissed entries leave pending review. Suggested text uses `textContent`.
No production change or duplicate automated test was needed for REQ-021.

The preceding implementation description and the following 5 October test
results are historical. The approved inline cards, accessible hidden group
heading and bottom guidance supersede that visible heading/banner presentation;
see the 12 October presentation evidence and the final 13 October verification
below. Requirement/AC identifiers and broader coverage gaps are unchanged.

The existing review test directly asserts the visible area's exact heading,
unchanged form values, and separate current/suggested displays in both form modes.
The Use and bulk tests verify transfer into editable fields and pending removal.
The ten-field bulk test also checks that review/use invokes no form submission or
additional request in its fixture. These are DOM-substitute assertions, not proof
of database persistence or complete browser workflows. Source inspection confirms
that review rendering and actions contain no persistence call. The separately
recorded REQ-020 browser smoke provides the relevant presentation evidence; no
new browser run was performed for this documentation-only audit.

Verification on 5 October 2026:
`node --test tests/frontend/ai-assist.test.cjs tests/frontend/form-session.test.cjs`
passed **34 tests (21 AI-helper, 13 form/page-session), with 0 failures**.
AC-021.1 is Covered for its two narrow behaviors using direct automated evidence,
source inspection, and the existing browser smoke. Broader browser automation,
cross-browser/accessibility work, and Increment 3 completion remain separate;
this status does not change REQ-020 coverage or claim the increment is done.

## AI Suggestions inline presentation — 7 October 2026

The final New Bug and Edit Bug presentation is visually approved by the user.
On desktop, each pending suggestion appears inline beside its editable field.
Only rows with pending suggestions split into field/card columns; unsuggested,
used, and dismissed rows remain or return to full width. On narrow layouts,
cards stack below their fields. Cards align with the actual control rather than
its label, and textarea cards stretch to match the control height when content
fits. Card borders are uniform cyan.

The top `AI Suggestions` heading and review instructions are left-aligned in a
subtle teal panel with a 1px border, 6px radius, and 10px vertical/12px horizontal
padding. The panel uses the general/Dismiss AI background
(`--ai-action-background`), separate from the stronger Use treatment. Headings
and instructions use the theme-aware AI text color. Each card shows the visible
heading `AI Suggestion`, its suggested value, then Use/Dismiss at the bottom.
All three are left-aligned. Suggested values use normal primary text color;
there is no duplicate current-form-value display. The heading's field-specific
ARIA label is referenced by the card's `aria-labelledby`, and action buttons
retain their field-specific accessible names.

Individual Use/Dismiss buttons are **64 × 26px on desktop**. Bulk Use All/Dismiss
All buttons are **92 × 36px on desktop**, centered below the field rows with an
8px gap and 18px top/bottom footer margins. The main AI Assist, Create/Save,
Cancel, and Delete actions are centered and share **100 × 40px desktop**
dimensions. AI controls retain their cyan/teal styling, with stronger Use/Use All
and subtler Dismiss backgrounds; Create/Save remains the filled primary action,
Cancel grey, and Delete red. Existing mobile behavior is preserved: review
buttons use **80 × 36px** at mobile widths, and main actions retain responsive
wrapping/stretching.

AI informational/status feedback is centered below the main action row and uses
the AI turquoise/cyan text color. Its margin is 16px above and 0 below, with the
existing 4px left padding and normal form padding retained. Errors use the
existing `message-error` styling; retry and session reset clear that class.
Dark-theme Use, Dismiss, Use All, and Dismiss All share the intentionally brighter
approved review hover background **#1c6c82**. AI Assist retains its separate
general hover background **#164e63**, muted disabled styling, and existing focus
styling. Light-theme behavior is unchanged: review hover remains **#a5f3fc** and
AI Assist hover **#cffafe**.

Suggestions remain session-only and non-authoritative. Use copies one suggested
value into its normal editable field; Dismiss removes that pending suggestion
without reverting previously used values. Use All applies only remaining
pending suggestions, and Dismiss All removes the remaining suggestions. Only
Create/Save persists form values. AI Assist is unavailable while pending
suggestions require review. Backend behavior and requirement identifiers are
unchanged.

Existing frontend tests cover field-row association, accessible naming, absence
of duplicate current values, bulk-control placement, resolved-row restoration,
footer/session cleanup, manual edits, Create/Save cleanup, and error/retry
presentation. Current verification:
`node --test tests/frontend/ai-assist.test.cjs tests/frontend/form-session.test.cjs`
passes **37 tests, 0 failures**; `node --test tests/frontend/*.test.cjs` passes
**76 tests, 0 failures**; `git diff --check` passes. Earlier `node --check` runs
passed for the shared helper, page handlers, and changed JavaScript test/helper
files; Node's `vm.Script` compilation also checked the native-input test's inline
script.

Previously performed static browser checks used actual New/Edit markup, CSS,
and the shared AI helper with fixed suggestions for all ten supported fields,
without the application server, database, or provider. New Bug in dark theme and
Edit Bug in light theme were observed at wide and 390px viewports. Checks
confirmed full-width unsuggested rows, field/card stacking without horizontal
overflow, uniform borders, heading/value/actions order, control-top alignment
for all ten cards, and matching heights for all four textarea cards with fixture
content. Field-specific names were present in the browser accessibility tree;
individual review restored rows, and bulk review cleared cards and hid controls.
The native-input browser test passed **12 cases** (New/Edit × Use/Use All ×
LF/CR/CRLF). Later isolated sizing checks confirmed 100 × 40px main actions in
both forms and unchanged mobile dimensions without horizontal overflow. These
checks support the specific observations above, not exhaustive verification of
the final UI; final visual approval is the user's manual-review evidence. No
new browser verification was performed during this documentation reconciliation.

Static fixtures do not exercise complete application workflows or persistence.
Broader cross-browser and accessibility verification remain pending. REQ-020
remains Partial; no requirement status is upgraded and Increment 3 completion is
not claimed.

## REQ-022 — AI Authorization and Data Protection

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| REQ-022 | AC-022.1 — Enforce AI Authorization | `test_ai_assist_requires_authentication` | API / Security | Covered |
| REQ-022 | AC-022.1 — Enforce AI Authorization | `test_ai_assist_requires_authorized_project_role` | API / Security | Covered |
| REQ-022 | AC-022.1 — Enforce AI Authorization | `test_ai_assist_checks_current_bug_status` | API / Security | Covered |
| REQ-022 | AC-022.1 — Enforce AI Authorization | `test_ai_assist_rechecks_membership` | API / Security | Covered |
| REQ-022 | AC-022.1 — Enforce AI Authorization | `test_ai_assist_rejects_bug_outside_project` | API / Security | Covered |
| REQ-022 | AC-022.1 — Enforce AI Authorization | `test_ai_triage_configured_requests_authorize_before_any_pipeline_work` | API / Security / Mocked Provider Integration | Covered |
| REQ-022 | AC-022.1 — Enforce AI Authorization | `test_ai_triage_rechecks_changed_role_before_provider_invocation` | API / Security / Mocked Provider Integration | Covered |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_context_preserves_submitted_form_and_persisted_bugs` | API / Context | Covered |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_context_retrieves_bounded_deterministic_same_project_history` | API / Database / Context | Covered |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_context_includes_only_current_assignable_project_members` | API / Context | Covered |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_generation_preserves_separate_context_without_mutation` | Unit / Generation Contract | Covered |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_generation_does_not_introduce_account_information_or_secrets` | Unit / Security | Covered |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_openai_sends_existing_contract_with_sdk_without_network_or_database` | Unit / Mocked Provider Adapter | Covered |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_triage_configured_pipeline_preserves_form_and_returns_validated_suggestions` | API / Mocked Provider Integration | Covered |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_triage_revalidates_current_member_eligibility` | API / Context / Mocked Provider Integration | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_triage_configured_pipeline_preserves_form_and_returns_validated_suggestions` | API / Mocked Provider Integration | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_valid_suggestion_cannot_modify_bug_without_user_save` | API / Mocked Provider Integration | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_triage_instruction_like_content_and_output_cannot_perform_actions` | API / Security / Mocked Provider Integration | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_generation_instructions_define_context_and_safety_boundaries` | Unit / Generation Contract | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_response_delegates_to_validator_and_returns_its_result` | Unit / Response Processing | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_response_has_no_mutation_database_or_provider_side_effects` | Unit / Response Processing | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_response_propagates_malformed_response` | Unit / Response Processing | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_suggestions_exclude_unsupported_or_unmapped_fields` | Unit / Validation | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_suggestions_exclude_non_string_text_without_losing_valid_field` | Unit / Validation | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_suggestions_exclude_invalid_classification_without_losing_valid_field` | Unit / Validation | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_suggestions_exclude_ineligible_or_non_integer_assignee` | Unit / Validation | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_suggestions_report_malformed_structure_as_error` | Unit / Validation | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_suggestions_review_separates_values_and_follows_form_order` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | `test_ai_use_all_maps_every_supported_field_without_persistence` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-022 | AC-022.3 — Limit AI Capabilities | New/Edit script-like suggestions render as literal text; review/use does not persist until normal Create/Save (REQ-020 smoke evidence above, 5 October 2026) | Manual / Browser + Database Smoke | Covered |

The valid advisory-output test returns a supported severity suggestion (Minor →
Major) through the Edit AI Assist pipeline while the stored bug stays Minor and
project/member/bug state stays unchanged. No normal PATCH occurs during AI Assist;
valid output remains advisory until normal user-controlled Create/Save. Provider
transport is mocked, not a live-model call.

### Audit and scope

The REQ-022 audit found the implementation already present in REQ-018/019 and
the REQ-020 review UI. No production code changed. The missing evidence was
limited to a role change between requests and instruction-like content/output
through the complete pipeline; dedicated REQ-022 traceability was also missing.

AC-022.1: both routes call `authorize_ai_assist` before `request_triage`. The
backend verifies the token, queries current project membership/role, and checks
the Edit bug's project and current Triage status on each request. Existing tests
cover membership removal, status changes, roles, authentication, and wrong-project
bugs before the service boundary. The configured rejection test now also covers
New Bug; the new role-change test uses the same token after QA Analyst membership
is removed and re-added as Developer, then restored to QA Analyst. Rejection
cannot reach context construction or the provider. Frontend visibility is not the
authorization boundary.

AC-022.2: the data path is `AiAssistRequest` to `build_triage_context`, then
`build_generation_input`, then `request_openai_suggestions`. Context preserves
the current form and selects at most five same-project history records, excluding
the edited bug. Member context includes only current same-project QA Analysts
and Developers, projected to user ID, email, and role; it does not select account
password hashes. History and form models likewise expose only approved fields.
Generation serializes these three context collections; the adapter sends that
JSON as user data, separately from trusted instructions. Authorization headers
never enter these models. `OPENAI_API_KEY` is used only to configure the transport
client, and `JWT_SECRET_KEY` stays in authentication. Structural context tests,
exact adapter payload assertions, and actual mocked SDK request inspection
jointly establish this path. The existing generation secret test now explicitly
covers both configuration key names as well as its prior secret/token sentinels.
This does not claim detection or redaction of secrets a user manually types into
otherwise permitted bug content.

AC-022.3: the provider receives no application tools or action capability. Raw
output passes through `process_provider_response` and the authoritative validator;
unsupported fields cannot grant roles, change lifecycle state, or execute actions.
The new New/Edit integration test sends instruction-like form content and receives
script-like suggestion text plus role/status/action fields. It verifies literal
text survives as data, unsupported/ineligible values are excluded, persisted
project/member/bug state is unchanged, and a Developer remains unauthorized.
Frontend source uses `textContent`, stores pending values separately, and only
Use/Use All copies them into editable controls. These actions do not submit or
persist; normal user-triggered Create/Save remains the persistence boundary.
Frontend unit evidence uses DOM substitutes; relevant browser/database evidence
is reused from the recorded REQ-020 smoke, with no new browser run claimed.

All three ACs are Covered for their defined capability and data boundaries using
the evidence above. Real-provider instruction compliance/quality, broader browser
automation/accessibility, and REQ-023 recovery remain outside this audit. This
does not change earlier requirements' coverage or establish Increment 3 completion.

Verification on 5 October 2026, run serially against the disposable test database:

- `.\.venv\Scripts\python.exe -m pytest tests/test_ai_assist.py tests/test_ai_triage.py -q` — **69 passed in 65.33 seconds**.
- `.\.venv\Scripts\python.exe -m pytest tests/test_ai_context.py tests/test_ai_generation.py tests/test_ai_openai.py tests/test_ai_response.py tests/test_ai_suggestions.py -q` — **172 passed in 22.58 seconds**.
- `node --test tests/frontend/ai-assist.test.cjs tests/frontend/form-session.test.cjs` — **34 passed, 0 failures**.
- `.\.venv\Scripts\python.exe -m py_compile tests/test_ai_triage.py tests/test_ai_generation.py` and `git diff --check` — passed.

No full pytest run was needed for these test/documentation changes. Provider calls
were mocked; no real provider, application database, or dogfooding records were used.

## REQ-023 — AI Failure Handling

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_assist_preserves_current_form_without_saving` | API / Unconfigured Service | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_triage_unconfigured_requests_keep_503_without_provider_work` | API / Mocked Provider Integration | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_triage_failures_are_safe_errors_without_persistence` | API / Mocked Provider Integration | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_triage_timeout_is_safe_without_retries_or_persistence` | API / Mocked SDK Transport Timeout | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_openai_rejects_uncompleted_output` | Unit / Provider Adapter | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_openai_rejects_refusal_instead_of_returning_suggestions` | Unit / Provider Adapter | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_openai_rejects_missing_or_unparseable_json` | Unit / Provider Adapter | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_openai_propagates_request_failure_without_fake_suggestions` | Unit / Provider Adapter | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_response_propagates_malformed_response` | Unit / Response Processing | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_submit_ai_context_limits_requests_and_reports_unavailable` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_submit_ai_context_recovers_from_network_failure` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_failed_or_malformed_responses_preserve_form_and_allow_retry` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_late_success_or_error_cannot_populate_reopened_session` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_late_json_cannot_replace_later_results` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-023 | AC-023.1 — Handle AI Request Failure | New/Edit safe AI failure feedback and preserved editable values (REQ-020 smoke evidence above, 5 October 2026) | Manual / Browser Smoke | Covered |
| REQ-023 | AC-023.2 — Continue Without AI | `test_ai_triage_returns_distinct_no_usable_suggestions` | API / Mocked Provider Integration | Covered |
| REQ-023 | AC-023.2 — Continue Without AI | `test_ai_no_usable_suggestions_is_success_and_allows_manual_work_and_retry` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-023 | AC-023.2 — Continue Without AI | `test_ai_failed_or_malformed_responses_preserve_form_and_allow_retry` | Unit (JavaScript / DOM substitutes) | Covered |
| REQ-023 | AC-023.2 — Continue Without AI | `test_new_create_after_ai_failure_or_no_usable_outcome` | Unit (actual page handlers / DOM substitutes) | Covered |
| REQ-023 | AC-023.2 — Continue Without AI | `test_edit_save_after_ai_failure_or_no_usable_outcome` | Unit (actual page handlers / DOM substitutes) | Covered |
| REQ-023 | AC-023.2 — Continue Without AI | New/Edit empty success, safe failure, retry, and ordinary editing (REQ-020 smoke evidence above, 5 October 2026) | Manual / Browser Smoke | Covered |

### Audit and verification

REQ-023 behavior was already implemented across the AI route/service and shared
review helper. The audit found test and traceability gaps, with no production
defect or production change. Earlier slice notes describing REQ-023 as deferred
record those checkpoints; this section records the current evidence.

AC-023.1: missing configuration returns safe HTTP 503. SDK transport/client
failures, including provider timeouts, return fixed HTTP 502 feedback. Malformed
provider output likewise returns a safe error rather than partial persistence or
an empty-success substitute. Existing API tests inspect unchanged project,
membership, and bug data; the transport/malformed/client cases now cover both
New and Edit. The service's timeout remains 60 seconds with SDK retries disabled.

In the frontend, failed HTTP responses, request rejection, JSON failure, and
unprocessable responses use error feedback and current-request-only cleanup.
The strengthened failure test covers both forms, all eleven editable fixture
values (including Fix Version), and an additional manual edit made while waiting.
It verifies loading feedback/button state, unchanged values, no form submission,
no extra request, and explicit retry. Existing stale response/JSON tests now cover
both forms with errors and rejections as well as success; an abandoned failure
cannot overwrite newer loading feedback or pending suggestions.

Timeout evidence is deliberately split: the backend test injects a read timeout
through the real SDK's mocked HTTP transport and verifies safe feedback, one
attempt, client cleanup, and no persistence. Frontend tests separately verify
that the resulting safe HTTP failure ends loading and permits retry. This is
not a browser timeout test, a wall-clock 60-second test, or an additional frontend
timeout timer. No such new mechanism was needed for the defined requirement.

AC-023.2: both failure and no-usable outcomes preserve values, re-enable AI Assist,
and permit manual edits. The two existing helper tests now explicitly retry with
new title/environment/description values and inspect the submitted snapshot and
fresh review state. Two new page-handler tests cover New Create and Edit Save
after HTTP failure, network rejection, or no usable suggestions. They verify no
implicit Create/Save, then normal manually revised values reach exactly one
explicit POST/PATCH and successful cleanup still works. Persistence calls in
these Node tests are mocked: they prove form transport/control flow, not database
writes. Backend data-safety assertions and the previously recorded REQ-020
browser/database smoke remain distinct evidence.

Both ACs are Covered for their defined failure/recovery behavior using direct
API/unit coverage and reused browser smoke. No new browser run, full browser
automation, real-provider evaluation, or Increment 3 completion is claimed.
Authentication loss retains the existing login redirect and normal authorization
rules; AI recovery does not bypass them. No error wording or UI design changed.

Verification on 5 October 2026:

- `.\.venv\Scripts\python.exe -m pytest tests/test_ai_assist.py tests/test_ai_triage.py tests/test_ai_openai.py tests/test_ai_response.py tests/test_ai_suggestions.py -q` — **222 passed in 71.36 seconds**, serially against the disposable database.
- `node --test tests/frontend/ai-assist.test.cjs tests/frontend/form-session.test.cjs` — **36 passed, 0 failures** (21 AI-helper, 15 form/page-session tests).
- `node --check tests/frontend/ai-assist.test.cjs`, `node --check tests/frontend/form-session.test.cjs`, and `.\.venv\Scripts\python.exe -m py_compile tests/test_ai_triage.py` — passed.
- `git diff --check` — passed.

Only tests/documentation changed, so no full pytest run was needed. No real
application records, migrations, or live provider calls were used.

## UI presentation refinement evidence — 12 October 2026

The approved AC-021.1 presentation now uses individually labelled suggestion
cards and an accessible review-group name without the visible top instructional
banner. Pending-only guidance reuses the existing status message below the form
actions. Earlier dated banner descriptions remain historical evidence.

`test_ai_pending_guidance_uses_bottom_status_and_clears_after_review` covers New
and Edit form guidance, final review, reset, error and no-usable states. The
frontend suite passed **80 tests**, focused deletion API coverage passed **9
tests**, and native browser fixtures passed **9 divider cases, 4 destructive
focus/disabled cases and 12 existing input cases**. Actual app theme verification
and its limits are recorded in [UI refinements verification](ui-refinements-verification.md).
REQ-012 and REQ-014 retain outstanding broader UI coverage; the native accepted
deletion dialog was not completed. These targeted technical rows and updated
AC-021.1 evidence do not establish full increment or release completion.

## Technical and infrastructure evidence

### Python Playwright E2E — 15 October 2026

The initial suite in `tests/e2e/` contained 12 test functions and 13 Chromium
scenarios (the AI failure/empty test has two cases). The scenario 14/15 extension
below brings the current suite to 14 functions and 15 scenarios. These rows add maintained
browser evidence alongside existing API/unit coverage and dated manual evidence.
They do not replace historical results or promote entire ACs to Covered: this
suite samples important journeys, uses one browser, and does not establish every
required visual, accessibility, negative, or cross-browser condition.

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| REQ-001 | AC-001.1 — Successful Registration | `test_registration_login_logout` | UI / Browser E2E | Partial |
| REQ-002 | AC-002.1 — Successful Login | `test_registration_login_logout` | UI / Browser E2E | Partial |
| REQ-003 | AC-003.2 — Unauthenticated Access | `test_registration_login_logout` | UI / Browser E2E | Partial |
| REQ-004 | AC-004.1 — Successful Logout | `test_registration_login_logout` | UI / Browser E2E | Partial |
| REQ-004 | AC-004.2 — Protected Access After Logout | `test_registration_login_logout` | UI / Browser E2E | Partial |
| REQ-002 | AC-002.2 — Invalid Credentials | `test_invalid_login_feedback_allows_correction` | UI / Browser E2E | Partial |
| REQ-005 | AC-005.1 — Successful Project Creation | `test_project_create_rename_and_confirmed_delete` | UI / Browser E2E | Partial |
| REQ-005 | AC-005.2 — Invalid Project Name | `test_project_create_rename_and_confirmed_delete` | UI / Browser E2E | Partial |
| REQ-007 | AC-007.1 — Successful Project Name Editing | `test_project_create_rename_and_confirmed_delete` | UI / Browser E2E | Partial |
| REQ-008 | AC-008.1 — Successful Project Deletion | `test_project_create_rename_and_confirmed_delete` | UI / Browser E2E | Partial |
| REQ-009 | AC-009.1 — Add Member | `test_owner_manages_membership_and_removed_user_loses_access` | UI / Browser E2E | Partial |
| REQ-009 | AC-009.2 — Remove Member | `test_owner_manages_membership_and_removed_user_loses_access` | UI / Browser E2E | Partial |
| REQ-006 | AC-006.4 — Unauthorized Project Access | `test_owner_manages_membership_and_removed_user_loses_access` | UI / Browser E2E | Partial |
| REQ-014 | AC-014.2 — Unauthorized Bug Deletion | `test_developer_cannot_delete_or_request_ai_and_outsider_cannot_open_bug` | UI / Browser E2E | Partial |
| REQ-012 | AC-012.3 — Unauthorized Bug Access | `test_developer_cannot_delete_or_request_ai_and_outsider_cannot_open_bug` | UI / Browser E2E | Partial |
| REQ-022 | AC-022.1 — Enforce AI Authorization | `test_developer_cannot_delete_or_request_ai_and_outsider_cannot_open_bug` | UI / Browser E2E (mocked provider) | Partial |
| REQ-011 | AC-011.1 — Successful Bug Creation | `test_bug_create_edit_assign_and_confirmed_delete` | UI / Browser E2E | Partial |
| REQ-013 | AC-013.1 — Edit Bug Report | `test_bug_create_edit_assign_and_confirmed_delete` | UI / Browser E2E | Partial |
| REQ-015 | AC-015.1 — Assign and Unassign Bugs | `test_bug_create_edit_assign_and_confirmed_delete` | UI / Browser E2E | Partial |
| REQ-014 | AC-014.1 — Successful Bug Deletion | `test_bug_create_edit_assign_and_confirmed_delete` | UI / Browser E2E | Partial |
| REQ-017 | AC-017.2 — Triage to Open | `test_bug_handoff_pass_and_reopen` | UI / Browser E2E | Partial |
| REQ-017 | AC-017.3 — Open to Development | `test_bug_handoff_pass_and_reopen` | UI / Browser E2E | Partial |
| REQ-017 | AC-017.4 — Development to Testing | `test_bug_handoff_pass_and_reopen` | UI / Browser E2E | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_bug_handoff_pass_and_reopen` | UI / Browser E2E | Partial |
| REQ-017 | AC-017.7 — Closed Bugs | `test_bug_handoff_pass_and_reopen` | UI / Browser E2E | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_failed_testing_returns_to_selected_developer` | UI / Browser E2E | Partial |
| REQ-012 | AC-012.2 — Open Bug Report | `test_sort_pagination_and_page_size_survive_navigation_and_reload` | UI / Browser E2E | Partial |
| REQ-012 | AC-012.4 — Sort Bug Reports | `test_sort_pagination_and_page_size_survive_navigation_and_reload` | UI / Browser E2E | Partial |
| REQ-012 | AC-012.5 — Paginate Bug Reports | `test_sort_pagination_and_page_size_survive_navigation_and_reload` | UI / Browser E2E | Partial |
| REQ-012 | AC-012.6 — Remember Bug Page Size | `test_sort_pagination_and_page_size_survive_navigation_and_reload` | UI / Browser E2E | Partial |
| REQ-018 | AC-018.2 — Explicit Request | `test_new_ai_review_applies_only_selected_suggestions_before_create` | UI / Browser E2E (mocked provider) | Partial |
| REQ-018 | AC-018.3 — Use Current Form Information | `test_new_ai_review_applies_only_selected_suggestions_before_create` | UI / Browser E2E (mocked provider) | Partial |
| REQ-020 | AC-020.1 — Review Suggestions | `test_new_ai_review_applies_only_selected_suggestions_before_create` | UI / Browser E2E (mocked provider) | Partial |
| REQ-020 | AC-020.2 — Use an Individual Suggestion | `test_new_ai_review_applies_only_selected_suggestions_before_create` | UI / Browser E2E (mocked provider) | Partial |
| REQ-020 | AC-020.3 — Dismiss an Individual Suggestion | `test_new_ai_review_applies_only_selected_suggestions_before_create` | UI / Browser E2E (mocked provider) | Partial |
| REQ-020 | AC-020.4 — Use All Pending Suggestions | `test_new_ai_review_applies_only_selected_suggestions_before_create` | UI / Browser E2E (mocked provider) | Partial |
| REQ-020 | AC-020.7 — Persist Changes Through Existing Form Actions | `test_new_ai_review_applies_only_selected_suggestions_before_create` | UI / Browser E2E (mocked provider) | Partial |
| REQ-020 | AC-020.5 — Dismiss All Pending Suggestions | `test_edit_ai_cancel_discards_changes_then_save_persists_review` | UI / Browser E2E (mocked provider) | Partial |
| REQ-020 | AC-020.7 — Persist Changes Through Existing Form Actions | `test_edit_ai_cancel_discards_changes_then_save_persists_review` | UI / Browser E2E (mocked provider) | Partial |
| REQ-020 | AC-020.8 — Pending Suggestion Lifetime | `test_edit_ai_cancel_discards_changes_then_save_persists_review` | UI / Browser E2E (mocked provider) | Partial |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_failure_or_empty_result_preserves_manual_work_and_allows_retry` | UI / Browser E2E (mocked provider) | Partial |
| REQ-023 | AC-023.2 — Continue Without AI | `test_ai_failure_or_empty_result_preserves_manual_work_and_allows_retry` | UI / Browser E2E (mocked provider) | Partial |
| REQ-020 | AC-020.6 — Repeat AI Assist Requests | `test_ai_failure_or_empty_result_preserves_manual_work_and_allows_retry` | UI / Browser E2E (mocked provider) | Partial |

Setup uses public API requests to create unique fictional prerequisites in the
same owned server used by the browser. Each test has a fresh browser context;
each invocation has a fresh temporary SQLite database, server and JWT secret.
The fixture verifies readiness through an owned stdout channel with child/launcher
PID relationship, effective database path, bound loopback socket and random
identity; only then does it make an HTTP request and check the identity header.
It refuses occupied ports without contacting existing listeners. Agent runs use
8148; 8151 remains reserved for the user's manual workflow. Normal backend
collection excludes the E2E directory unless `--e2e` is supplied.

AI requests exercise real authorization, context construction, generation input,
SDK serialization, validation, form review, and normal Create/Save persistence.
Only the provider transport is mocked in the test server; no production code or
API contract changes. Inherited provider configuration is removed, outgoing
server connections are blocked after startup, and external browser requests are
aborted. Provider-error and empty-result cases retry explicitly and still save
manually without successful AI output. No real/non-test database or genuine
project/report is used.

Gaps remain for full permission and validation combinations (retained at API/unit
layers), additional lifecycle branches, cross-user/project preference matrices,
mobile/native keyboard gestures, visual/themes, broader accessibility, other
browser engines, and real-model quality. Filtering is not implemented and is not
invented for testing. No BDD or CI/CD work is introduced.

E2E execution on 15 October 2026 reused the installed Playwright 1.64.0 and
Chromium/headless-shell revision 1248 (the matching revision in its browser
manifest). No package or browser installation was performed. Final headless
Chromium verification on approved origin 8148:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --e2e-port 8148 --browser chromium -q --tracing retain-on-failure --screenshot only-on-failure
.\.venv\Scripts\python.exe -m pytest tests/e2e/test_projects.py tests/e2e/test_bugs.py tests/e2e/test_bug_list.py tests/e2e/test_authorization.py tests/e2e/test_auth.py tests/e2e/test_ai_triage.py --e2e --e2e-port 8148 --browser chromium -q --tracing retain-on-failure --screenshot only-on-failure
```

Both finalized runs passed **13 scenarios**, with **0 failures, 0 skips, and no
teardown errors**: **40.68s** in normal module order and **40.61s** in reverse
module order. Each run started a fresh owned server/database and completed
graceful shutdown and temporary-directory cleanup. A separate occupied-port
probe bound a known local listener on 8148, invoked the fixture's availability
guard, and verified both rejection and an empty accept queue: no connection to
the occupied listener occurred. Default backend collection reported **557 tests**
without collecting E2E or launching a browser.

Development runs exposed test-only startup/locator assumptions and Windows
teardown behavior. The virtual-environment launcher spawns a child interpreter,
so ownership checks verify that relationship rather than equating both PIDs.
The observed Proactor `WinError 10054` path failed to detach a reset transport,
leaving Uvicorn waiting for closure; the HTTP-only test server now selects a
Windows selector loop. Runs requiring forced shutdown were reported as errors,
not accepted as passing. The known temporary directory left by the first failed
launcher cleanup was explicitly removed after identifying the task-owned path.
No application defect was confirmed or production behavior changed. Headed,
other-engine, visual/theme, and screen-reader execution were not performed.

After both finalized E2E runs, regression commands ran serially:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
node --test tests/frontend/*.test.cjs
.\.venv\Scripts\python.exe -m pip check
git diff --check
```

Results: **557 backend tests passed in 317.61s**, with **0 failures and 0 skips**;
**94 frontend tests passed in 283.2971ms**, with **0 failures and 0 skips**.
Dependency validation reported **No broken requirements found**. Diff whitespace
checks and Python source parsing passed; all 12 browser test functions have exact
traceability references. No pytest suites ran concurrently. Existing user changes
moving the two BDD example files were preserved; this task adds no BDD scenarios.

#### Readability and safety follow-up — 15 October 2026

The subsequent cleanup preserves all six test modules' executable syntax trees,
including test names, assertions, locators and parametrization: still 12 functions
and 13 scenarios. Meaningful blank lines and line wrapping separate setup,
navigation, form actions, role changes and persistence checks. The definition-list
helper now names its term locator. No scenarios, packages, CLI options or
production changes were added; the existing dependency pins remain unchanged.

E2E infrastructure safety assertions are now explicit runtime checks. A separate
`python -O` probe rejected mismatched, generated temporary database settings before
application imports and created no database. Its initial sandbox run could not
remove its empty temporary directory; the rerun outside the sandbox passed and
removed that known directory. No application database was involved. A known
occupied-port probe again verified refusal without contacting its listener.

The existing process/identity/bound-address handshake, startup reader thread,
stdin shutdown, Windows selector loop, temporary-directory lifecycle and network
restrictions remain: each supports isolation or observed Windows reliability.
The mock client factory and response construction are clearer, and API request
contexts are disposed in `finally`. Standard pytest temporary-directory retention
would not provide the same immediate database-directory removal.

Current Chromium runs used the commands above, with `--headed` added for the
third run. All used approved port 8148, the matching installed Chromium revision
1248, tracing on failure, and screenshots on failure:

| Run | Result | Duration |
| --- | --- | --- |
| Headless, normal module order | 13 passed; 0 failures/skips | 40.73s |
| Headless, reversed module order | 13 passed; 0 failures/skips | 40.74s |
| Headed, normal module order | 13 passed; 0 failures/skips | 45.45s |

All three completed without teardown errors or forced shutdown. Directory
comparisons after the repeated and headed runs found no new E2E temporary
directories remaining, and exclusive bind checks confirmed port 8148 was released.
The user's intermittent Add Member timeout did not recur; this does not establish
its cause or a fix. No speculative delay, retry or locator workaround was added.
Headed execution supplements the earlier headless evidence; it does not establish
visual/theme, accessibility or cross-browser coverage. AC statuses remain Partial.

The backend and frontend regression commands above were rerun serially after
cleanup: **557 backend tests passed in 324.63s** and **94 frontend tests passed in
246.2406ms**, each with **0 failures and 0 skips**. Default collection with
`.\.venv\Scripts\python.exe -m pytest --collect-only -q`
still collected 557 backend tests and excluded E2E. `pip check` reported no
broken requirements. All 11 Python files in the root/E2E support and test scope
parsed and compiled; syntax-tree comparisons preserved the six test modules and
content comparisons preserved the user's two BDD moves. `git diff --check` and
an additional whitespace check covering untracked Python/dependency files passed.
All test data was fictional and disposable; no real database or genuine QA
records were accessed. No packages/browser binaries were installed, production
files changed, or handoff script run during this cleanup.

#### Scenarios 14 and 15 — 15 October 2026

Two focused browser tests extend the suite to 14 functions / 15 scenarios.
Existing scenarios, fixtures, production code and dependencies are preserved.

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| REQ-011 | AC-011.4 — Optional Bug Information | `test_fix_version_eligibility_persistence_and_form_reset` | UI / Browser E2E + API readback | Partial |
| REQ-013 | AC-013.2 — Optional Bug Information | `test_fix_version_eligibility_persistence_and_form_reset` | UI / Browser E2E + API readback | Partial |
| REQ-017 | AC-017.5 — Testing Outcome | `test_fix_version_eligibility_persistence_and_form_reset` | UI / Browser E2E + API readback | Partial |
| REQ-017 | AC-017.6 — Close Without Fixing | `test_fix_version_eligibility_persistence_and_form_reset` | UI / Browser E2E + API readback | Partial |
| REQ-012 | AC-012.5 — Paginate Bug Reports | `test_page_size_preferences_persist_and_are_isolated_by_user` | UI / Browser E2E | Partial |
| REQ-012 | AC-012.6 — Remember Bug Page Size | `test_page_size_preferences_persist_and_are_isolated_by_user` | UI / Browser E2E | Partial |
| REQ-012 | AC-012.6 — Remember Bug Page Size | `test_page_size_invalid_or_unavailable_reads_fall_back_to_ten` | Frontend unit / DOM and storage substitutes | Partial |
| REQ-012 | AC-012.6 — Remember Bug Page Size | `test_page_size_blocked_writes_preserve_current_pagination_and_sort` | Frontend unit / DOM and storage substitutes | Partial |

Scenario 14 creates a report through New Bug without a Fix Version control and
verifies no version was persisted. It checks hidden, empty ordinary Edit inputs
in Triage, Open, Development and Testing, captures save requests to exclude Fix
Version, and reads back the actual saved description/version through the API.
The optional Testing Pass field remains editable and blank Pass closes as Fixed.
Closed/Fixed ordinary Edit adds, replaces and clears a version, checking prefill,
API persistence and reloaded Details each time. An unsaved version is cancelled;
reopening to Triage in the same page clears the retained input before another
save. A Closed/Duplicate report likewise hides the input and omits it from saves.
API transitions seed lifecycle prerequisites; the browser exercises the relevant
form behavior. Other non-Fixed resolutions retain existing parametrized API tests.

Scenario 15 seeds two fictional projects with 21 reports each. It checks 10/20/50
sizes against actual row counts, Back/reload and logout/login persistence,
cross-project preference sharing, and two users retaining different preferences.
Title descending in one project and Bug ID ascending in the other remain
independent of page size; the second user initially has default sorting. The
50-size single-page state hides navigation. Focused JavaScript tests exercise
missing/invalid/throwing preference reads and blocked writes, including continued
pagination and sorting after a write failure and default 10 on reinitialization.
The existing frontend fixture now separates token access from preference storage.

Rows retain the matrix's existing per-test contribution convention. Overall AC
reconciliation and matrix restructuring remain a separate coverage-closure task.
This slice does not verify all optional text-field edits, full pagination ranges,
refresh clamping, native row gestures, lifecycle scrolling or real-model quality.
No visual/theme or additional browser-engine verification is claimed.

Current execution commands (serial; no browser/package installation):

```powershell
.\.venv\Scripts\python.exe -m pytest tests/e2e/test_bugs.py tests/e2e/test_bug_list.py --e2e --e2e-port 8148 --browser chromium -q -k 'fix_version_eligibility or page_size_preferences' --tracing retain-on-failure --screenshot only-on-failure
.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --e2e-port 8148 --browser chromium -q --tracing retain-on-failure --screenshot only-on-failure
$e2eNodes = @(.\.venv\Scripts\python.exe -m pytest tests/e2e --e2e --e2e-port 8148 --collect-only -q | Where-Object { $_ -match '^tests/e2e/.*::test_' })
if ($e2eNodes.Count -ne 15) { throw "Expected 15 scenarios, found $($e2eNodes.Count)" }
[Array]::Reverse($e2eNodes)
.\.venv\Scripts\python.exe -m pytest @e2eNodes --e2e --e2e-port 8148 --browser chromium -q --tracing retain-on-failure --screenshot only-on-failure
node --test tests/frontend/*.test.cjs
.\.venv\Scripts\python.exe -m pytest tests/test_fix_version_on_pass.py tests/test_bug_numbers.py tests/test_bug_update_readback.py tests/test_database_isolation.py tests/test_database_lifecycle.py -q
```

The focused browser run passed **2 tests, 4 deselected in 14.58s**. After adding
the final second-user return assertion, the complete suite passed **15 scenarios
in 56.65s** in normal order and **15 in 56.61s** with every collected node ID
reversed, including within modules and the AI parametrized cases. Both full runs
had **0 failures, 0 skips and no teardown errors**. Each used a fresh temporary
database and the existing verified server identity/configuration handshake on
8148. Before/after temporary-directory comparisons found **0 new E2E directories
remaining** after each run; exclusive socket binds confirmed the port was released.
No forced shutdown, unknown listener contact, real database access, genuine QA
record access or paid/external provider request occurred.

All frontend JavaScript tests passed: **96 passed, 0 failures, 0 skips in
272.4076ms**. Python E2E source parsing/compilation and the modified JavaScript
file's syntax check passed. No production files changed, no Git operations staged
or committed work, and the user-only handoff script was not run. Earlier dated
13-scenario and regression results above remain historical evidence.

The focused backend regression command passed **71 tests in 76.82s**, with
**0 failures and 0 skips**, against the existing isolated per-test databases.
It covers Fix Version rules, public numbering, durable update readback, database
configuration isolation and lifespan management. Default collection still found
**557 backend tests**, excluding E2E. `git diff --check` passed. The full backend
suite and headed Chromium were not rerun in this extension; their earlier runs
remain dated evidence above.

### Test-suite preparation — 15 October 2026

This preparation pass changes test support, representative assertions, and
documentation only. Production application code, requirements, dependencies,
and existing test organization are unchanged. Playwright is not installed or
configured, and no E2E tests are introduced.

The function-scoped `test_database` fixture uses a fresh absolute path beneath
pytest's `tmp_path`. It verifies that its generated path is absent, configures
the environment before application import, explicitly rebinds the cached
`app.database.DATABASE_NAME`, and verifies the effective setting before lifespan
startup. `test_client` clears inherited provider credentials; configured AI tests
still explicitly supply mocked clients and dummy keys. Client shutdown precedes
database removal in fixture teardown. Existing migration and subprocess fixtures
retain their separate temporary databases. Tests remain serial.

`test_client_rebinds_cached_database_before_startup` simulates an earlier cached
setting using a synthetic temporary path. Its SQLite guard rejects every file
target except the expected disposable path before opening it, while allowing the
existing in-memory schema reference. It also verifies database removal after
client teardown. `test_client_starts_with_fresh_database` runs twice, registering
the same fictional email and checking an initially empty project list each time.
Filename-dependent tests now compare against the fixture path; password-hash
verification connects directly to that disposable path.

Authorized API readback now proves unchanged bug data after rejected edit and
deletion, and unchanged membership after each rejected addition/removal. Existing
parameterized roles and request prerequisites are preserved. The previously
unlisted `test_bug_update_response_readback_after_commit` is recorded under
REQ-013 as technical API/database integration evidence. Feature AC statuses and
broader UI/manual gaps are unchanged.

Current execution evidence (all commands run from the repository root):

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_database_isolation.py tests/test_database_lifecycle.py tests/test_jwt_secret.py tests/test_bug.py::test_non_member_cannot_edit_bug_report tests/test_bug.py::test_unauthorized_member_cannot_delete_bug tests/test_projects.py::test_non_owner_cannot_manage_project_members -q
.\.venv\Scripts\python.exe -m pytest
node --test tests/frontend/*.test.cjs
node --check tests/frontend/native-input-server.cjs
git diff --check
```

The corrected focused run passed **25 tests in 22.05s**. Its first run had
**1 failed, 24 passed in 21.70s** because the new test guard incorrectly rejected
the application's disposable `:memory:` schema reference; correcting that test
instrumentation required no application change. The subsequent complete Python
suite passed **557 tests in 317.71s**, with **0 failures and 0 skips**. All frontend
JavaScript tests passed: **94 passed, 0 failed, 0 skipped, 326.4404ms**. Static
fixture-server syntax and `git diff --check` passed.

The static helper and README now use approved origin `http://127.0.0.1:8148`.
A listener inventory found no listener on 8148; no server was started or reused.
No browser/manual verification was performed in this pass. No real/non-test
application database or genuine dogfooding record was opened, inspected, or
accessed. Earlier dated results below remain historical evidence.

Final pre-commit review on 13 October 2026 passed the full backend suite
(**544 passed, 0 failed, 0 skipped**) and full frontend suite
(**80 passed, 0 failed, 0 skipped**), plus the existing native fixtures
(**9 divider, 4 destructive-state and 12 input cases**, all passed).
Browser-computed semantic contrast meets AA in both themes, including the
current manually approved light hover `#EFF7FA` and the dark mixed-color hover.
BUG-31's semantic contrast remediation is supported by these retest measurements;
its application record was not changed and final closure remains with the user.
The final-state section of [UI refinements verification](ui-refinements-verification.md#final-approved-state-and-pre-commit-verification--2026-10-13)
records exact measurements, Git state and limitations. This does not upgrade
broader Partial rows or establish Increment 3 completion under the Definition of
Done; cross-browser, screen-reader and broader mobile verification remain open.

These tests protect implementation quality without a dedicated requirement or AC in `docs/requirements.md`. No new requirement is introduced, and the rows do not establish completion of any feature AC or increment.

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| — | AC — | `test_importing_application_does_not_create_database` | Subprocess / Database Lifecycle | Covered |
| — | AC — | `test_application_lifespan_initializes_schema_before_requests` | Subprocess / API / Database Lifecycle | Covered |
| — | AC — | `test_client_rebinds_cached_database_before_startup` | Test Infrastructure / Database Isolation | Covered |
| — | AC — | `test_client_starts_with_fresh_database` | API / Database Isolation | Covered |
| — | AC — | `test_fresh_database_creates_numbering_schema` | Database / Migration | Covered |
| — | AC — | `test_legacy_backfill_preserves_every_field_and_is_idempotent` | Database / Migration | Covered |
| — | AC — | `test_migration_failure_rolls_back_schema_data_and_version` | Database / Migration | Covered |
| — | AC — | `test_migration_rejects_unexpected_partial_or_inconsistent_legacy_schema` | Database / Migration | Covered |
| — | AC — | `test_numbering_constraints_reject_invalid_storage` | Database / Constraints | Covered |
| — | AC — | `test_numbering_uniqueness_is_scoped_to_project` | Database / Constraints | Covered |
| — | AC — | `test_current_schema_rejects_invalid_counter_without_repair` | Database / Migration | Covered |
| — | AC — | `test_application_version_is_shared_by_openapi_and_endpoint` | API / Version Metadata | Covered |
| — | AC — | `test_about_page_includes_application_version_loader` | API / Static HTML | Partial |

The database-lifecycle tests verify that importing the application leaves its disposable database absent and that entering the application lifespan initializes the schema before a registration request. They are infrastructure evidence, not complete registration coverage.

BUG-12 migration tests use temporary legacy databases with both source and actual appended-column order, interleaved/gapped IDs, nullable/version/lifecycle fields and timestamps. Schema version 1 uses `PRAGMA user_version`; named source/destination columns preserve all 18 legacy fields. Backfill assigns 1..N by ascending global ID within each project, initializes nonempty counters to N+1 and empty counters to 1, and validates the copy and relationships before replacement. Tests verify exact data preservation, positive-integer/unique constraints, unchanged repeated/current startup (including deletions and retained higher counters), explicit rollback after an injected table-replacement failure, and refusal of unexpected/partial schemas or invalid counters without repair. No real application database migration or browser verification was performed in this implementation task. Test-first execution observed 49 Python failures (23 migration, 6 numbering API, 20 expanded lifecycle cases) and 10 failures/19 passes in the initial focused frontend run before production changes. Review added an extra schema-rejection parameter proving that a table whose name resembles the reserved system prefix is still rejected.

BUG-12 verification on 7 October 2026:

- `.\.venv\Scripts\python.exe -m pytest tests/test_database_migrations.py tests/test_database_lifecycle.py -q --tb=short` — **26 passed in 1.98 seconds**, using disposable databases.
- `.\.venv\Scripts\python.exe -m pytest tests/test_bug_numbers.py tests/test_fix_version_on_pass.py tests/test_bug.py -q --tb=short` — **150 passed in 135.21 seconds**.
- `.\.venv\Scripts\python.exe -m pytest -q --tb=short` — **503 passed in 269.53 seconds**, serially against disposable test databases, including the final schema-rejection parameter.
- `node --test tests/frontend/bug-number-display.test.cjs tests/frontend/bug-sort-persistence.test.cjs tests/frontend/form-session.test.cjs` — **31 passed, 0 failures**.
- `node --test tests/frontend/*.test.cjs` — **74 passed, 0 failures**.
- `node --check frontend/js/project.js` and `node --check frontend/js/bugs.js` — passed.
- `git diff --check` — passed.

During the initial implementation verification above, the real `bugtriage.db` SHA-256, size and modification timestamp remained unchanged; its first migration was then subject to separate authorization and the normal application was not started against it by the agent. A subsequent read-only inspection on 7 October 2026 established that the real database had already reached version 1, with 7 projects and 46 bugs, clean integrity/foreign-key checks, valid deterministic numbers/counters and no migration-temporary table. That inspection did not establish what initiated migration or the additional bug's provenance. The public-identity refinement requires no new schema change or migration and does not write to the real database.

**BUG-12 review follow-up (7 October 2026):** The existing `test_migration_failure_rolls_back_schema_data_and_version` now covers both rejection before DROP and a test-only connection failure immediately before the final commit. The late case first asserts that the original table has been replaced, all legacy values have been copied, local numbers/counters are assigned, no replacement table remains, and `user_version` is 1 inside the uncommitted transaction. After rollback, the complete schema/data dump and version match the legacy snapshot; explicit checks confirm version 0, no numbering columns and no temporary table. A normal retry then migrates successfully and preserves every original value. The legacy fixture now includes populated Steps to Reproduce and Priority in one row while retaining null examples, exercising both values through the existing full-tuple preservation assertions and both historical column orders.

The existing `test_failed_creation_rolls_back_bug_and_counter` now covers failures before the counter update and immediately before commit after both allocator writes. The late hook asserts that the tentative report and incremented counter are present in the transaction. Subsequent API readback matches the original report list, the stored counter equals its prior value, and the next successful creation receives the unconsumed number. Both injections are test-only; production code is unchanged. Existing Partial/Covered statuses and historical execution evidence remain unchanged. These cases use disposable test databases; no real migration or browser verification is claimed.

Follow-up verification: `.\.venv\Scripts\python.exe -m pytest tests/test_database_migrations.py tests/test_bug_numbers.py -q --tb=short` — **32 passed in 3.84 seconds**. `.\.venv\Scripts\python.exe -m pytest -q --tb=short` — **505 passed in 270.38 seconds**, run serially against disposable test databases.

The version tests support the approved application-versioning convention (`APP_VERSION` as the source of truth), which has no dedicated requirement/AC. The API test verifies consistency between the version constant, OpenAPI metadata, and `/version`. The About-page test verifies only the HTML placeholder and script inclusion; browser execution and the displayed version are not verified by that test, so its evidence remains Partial.

## Coverage limitations from the pre-commit review

- User Stories remain in requirements.md. The previously noted missing REQ-005 user-story heading remains a specification follow-up; the matrix no longer contains US references, and no new ID is introduced here.
- Registration feedback, project-name display, member management, bug creation/list/detail/editing, and reassignment remain Partial where required browser verification is outstanding. Existing Manual entries record earlier manual verification, not automated UI coverage. AC-009.5 also lacks an explicit test of alphabetical ordering within a role.
- AC-003.3 is Partial: invalid-token coverage exists, but dedicated expired-token coverage is missing.
- The earlier shadowed definitions of `test_non_owner_cannot_manage_project_members`, `test_non_owner_cannot_edit_project`, and `test_non_owner_cannot_delete_project` were identical to the later collected definitions, including decorators. Only those dead earlier copies were removed; the collected definitions and their existing matrix entries are unchanged.
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

## Essential mobile UI fixes — 14 October 2026

BUG-32 retains one semantic table, renderer, links and pagination. CSS stacks rows at 700px and below; a mobile field selector and direction button reuse desktop sorting and preference logic. Mobile headers are centered and always visible; the superseded Menu script and its tests were removed. Long Bug Details titles wrap, long desktop project links truncate with full text on focus, and Edit actions use two balanced columns when the form cannot fit all four buttons.

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| REQ-012 | AC — | `test_bug_mobile_labels_and_header_relationships_survive_sorting` | Frontend unit | Covered |
| REQ-012 | AC — | `test_mobile_sort_controls_reuse_all_columns_direction_and_preferences` | Frontend unit | Covered |
| REQ-012 | AC — | `test_mobile_sort_resets_pagination_and_empty_list_hides_toolbar` | Frontend unit | Covered |
| REQ-012 | AC — | `test_project_navigation_preserves_full_name_as_text_and_focus_tooltip` | Frontend unit | Covered |

Final refinement verification: `node --test tests/frontend/*.test.cjs` passed 84 tests; syntax checks for `project.js` and `bugs.js` and `git diff --check` passed. Browser checks used a separate server on port 8138 with its configured temporary SQLite database verified before interaction: 320/390/430/500/700/701/1280px in both themes, long header labels/email, mobile sort selection/direction, pagination, reload/viewport preference continuity, and intermediate Edit action layouts (including 509px). No development database or protected project was used. Existing AC statuses remain unchanged; screen-reader, physical-device and broader browser checks remain outstanding.

Final polish: Sort by shares the Edit field-label rule (2px left padding). Logout and a borderless theme icon share one centered mobile row, with a divider only when Logout is visible; desktop styling is unchanged. Isolated browser checks at 320/390/700/1280px in both themes confirmed equal label insets, action alignment, visible theme keyboard focus, theme switching, successful Logout and no guest divider. The frontend suite remains 84 passing tests.

## Dismissible AI notice, Privacy Policy and duplicate JSON properties — 14 October 2026

AC-022.2 distinguishes application-managed secrets from user-supplied bug content sent on explicit AI Assist requests. The context builder, project isolation, authorization and duplicate-JSON decoder fix are unchanged by the notice refinement. New/Edit show a compact informational notice only when AI Assist is available and the notice has not been dismissed. The notice warns against sensitive content, links to `/privacy.html`, and uses one shared localStorage preference across both forms, reloads and future visits. Dismissal is not consent. The notice is removed from `aria-describedby` when unavailable or dismissed; dismissal returns focus to AI Assist or an available review/form action without changing suggestions, values or messages. Storage failures permit in-page dismissal without promising persistence. No automatic detection of arbitrary user-supplied secrets is claimed.

The public pre-deployment Privacy Policy reuses the header, theme and footer. All application pages, including Registration, the redirect landing page and Privacy Policy itself, have footer links; both AI notices also link to it. Registration uses the heading `Register` and reuses its existing subtitle for `Create an Account · Read our Privacy Policy`, with only `Privacy Policy` linked to `/privacy.html` and no additional paragraph. Login, Registration, New Bug and Edit Bug labels retain 2px left padding and now use compact label-to-input spacing with no added bottom margin; input dimensions are unchanged. About omits its self-link, shows Projects for authenticated users, and retains guest Register/Login and appropriate Logout/theme controls; its empty Projects navigation group is hidden for guests. Other pages, including Privacy Policy, retain About navigation. Shared footer styling matches the copyright font size, uses a 4px gap, and keeps links underlined with visible keyboard focus. Operator/contact, legal bases, jurisdiction, hosting/logging, retention/deletion/backups, provider settings and international transfers require confirmation before publication. Temporary recruiter demo accounts and fictional demo data are explicitly planned, not an implemented account-expiry or cleanup feature.

| REQ | AC | Test Reference | Test Layer | Status |
| --- | --- | --- | --- | --- |
| REQ-019 | AC-019.3 — Validate Suggested Values | `test_ai_openai_rejects_duplicate_json_properties_at_any_depth` | Unit / Mocked Provider Adapter | Partial |
| REQ-023 | AC-023.1 — Handle AI Request Failure | `test_ai_triage_duplicate_json_is_safe_failure_before_validation` | API / Mocked Provider Integration | Covered |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_new_bug_ai_disclosure_is_near_and_describes_ai_assist` | Frontend / HTML Contract | Partial |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_edit_bug_ai_disclosure_is_near_and_describes_ai_assist` | Frontend / HTML Contract | Partial |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_notice_availability_and_dismissal_update_accessible_description` | Frontend unit / DOM substitutes | Partial |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_notice_dismissal_persists_across_new_edit_and_reload` | Frontend unit / DOM and storage substitutes | Partial |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_notice_dismissal_preserves_focus_during_ai_loading_or_review` | Frontend unit / DOM substitutes | Partial |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_notice_restores_preference_on_cached_navigation_and_storage_events` | Frontend unit / DOM and storage substitutes | Partial |
| REQ-022 | AC-022.2 — Restrict AI Context | `test_ai_notice_storage_failure_still_allows_in_page_dismissal` | Frontend unit / DOM and storage substitutes | Partial |
| REQ-022 | AC — | `test_privacy_policy_links_cover_all_page_footers` | Frontend / HTML Contract | Covered |
| REQ-022 | AC — | `test_privacy_policy_is_public_without_authentication` | API / Public static page | Covered |
| REQ-001 | AC — | `test_registration_subtitle_links_only_privacy_without_extra_paragraphs` | Frontend / HTML Contract | Covered |
| REQ-004 | AC — | `test_about_navigation_preserves_guest_and_authenticated_controls` | Frontend / HTML and DOM substitutes | Covered |

Nine duplicate-property regression cases failed before the decoder fix. The decoder rejects duplicate properties at every object depth, including identical values and escaped equivalent keys, before domain validation. New/Edit API cases verify the existing safe 502 response, no raw-value disclosure, and unchanged persisted state. The earlier full seven-suite AI run passed 256 tests in 114.43 seconds using disposable `test_bugtriage.db`; this remains prior evidence, not a new full backend run. The most recent backend verification (`.\.venv\Scripts\python.exe -m pytest tests/test_privacy.py tests/test_ai_openai.py tests/test_ai_triage.py -q -p no:cacheprovider`) passed 68 tests in 58.80 seconds after confirming the disposable database path before imports; no backend tests or database access were performed for the final documentation-only continuation. Latest `node --test tests/frontend/*.test.cjs` verification passed 94 tests, including ten notice/link/navigation tests, with 0 failures and 0 skipped. JavaScript syntax checks passed during implementation, and the final documentation-only continuation's `git diff --check` passed.

Earlier notice browser evidence used the actual application on isolated port 8142, with its temporary `ai-notice-browser-*/notice-fixture.db` path verified before interaction and an in-memory mocked provider. New/Edit notices were checked with pending suggestions at 390px and 1280px in both themes without page overflow. Keyboard dismissal in Edit preserved both pending cards, the form value and guidance, moved focus to Use All with a visible outline, and removed the accessible-description reference. Dismissal persisted after Edit reload/reopen, navigation to New Bug, and New Bug reload/reopen. The Privacy Policy loaded as a guest before login and through the footer after logout. Footer links and the final registration subtitle link have automated HTML checks. These observed checks are retained from implementation; they were not repeated during the final documentation-only continuation. Screen-reader, broader cross-browser and independently forced browser-cache restoration checks remain outstanding; the cached-navigation handler has unit coverage only. No real database, protected project or live provider was used. Broader Increment 3 sign-off remains separate.

Earlier footer refinement removed the extra registration paragraph; the later inline subtitle link described above preserves that single-paragraph layout. At that stage, `node --test tests/frontend/*.test.cjs` passed 92 tests and the disclosure test syntax check and `git diff --check` passed. A separate static-only server on port 8143 (no database or application API routes) served Login, Registration and Privacy Policy at 390px and 1280px in both themes. All twelve combinations had no page overflow, a 14px copyright and link font, and a measured 4px gap. Login and Registration form tops matched at each width/theme. Keyboard Tab focus reached the underlined policy links with a 2px outline; Enter navigated from Registration to Privacy Policy. No backend or privacy-content changes were made for this refinement.

Earlier Login/Registration/About browser evidence was obtained before the documentation-only continuation. An isolated server on port 8144 supplied the pre-change form/input geometry baseline; a fresh origin on port 8145 used its verified temporary `auth-ui-final-*/auth-ui-test.db`, a fictional account and no-cache responses to avoid a cached stylesheet. Both forms were checked at 320px, 390px and 1280px in light and dark themes. Every form/input rectangle matched that stage's baseline exactly, all four labels computed to 2px left padding, neither page overflowed, and Registration's previous subtitle remained one 18px-high line. Keyboard activation of the subtitle link opened Privacy Policy. A real login to the fictional account confirmed About shows Projects/Logout without an About self-link; after logout, guest About showed Register/Login with the empty Projects group hidden. Privacy Policy retained its About navigation and footer link. No new browser or database checks were performed during that documentation-only continuation, and the handoff script was intentionally not run.

Earlier auth-form spacing/copy verification (superseded compact spacing below) used a database-free static server on port 8146, serving the real Login/Registration pages and an inert Bug form reference with no application API routes. The reference Bug labels computed to block display, 6px bottom margin, 2px left padding and a measured 6px label-to-input gap; auth labels previously measured about 0.67px vertically. Both auth forms now reuse that existing 6px rule. All twelve Login/Registration combinations at 320px, 390px and 1280px in both themes measured 6px gaps and 2px left padding, with unchanged input dimensions and horizontal positions, matching form widths/heights and corresponding field offsets, and no page overflow. Both forms grew 12px taller as expected from the added label spacing; their top positions still matched. The final Registration heading and subtitle were observed, the subtitle stayed one 18px-high line at these widths without forced no-wrap styling, and keyboard activation of its retained link opened Privacy Policy. `test_registration_subtitle_links_only_privacy_without_extra_paragraphs` now checks the final heading/copy and existing single subtitle element. The full frontend suite passed 94 tests (0 failures, 0 skipped); the affected test syntax check and `git diff --check` passed. No database access, backend changes or handoff script execution occurred in this refinement. Broader cross-browser and screen-reader verification remain outstanding.

Earlier notice, compact-label and mobile-header refinement (mobile spacing superseded below): both notices now read "AI Assist sends the current bug, up to five recently updated bugs from this project, and eligible assignee information to OpenAI. Avoid passwords, API keys, and sensitive personal information. Learn more in our Privacy Policy." Only Privacy Policy is linked. The two HTML contract tests above assert the exact text and single link. The dismiss button is positioned 8px from the top/right, has a 32x32px target and leaves 8px clearance from the reserved text area. Login/Registration restore their original inline-label flow with no added bottom margin; New/Edit use the same compact flow and a zero label/control grid gap beside desktop suggestions. All retain 2px horizontal label padding. Existing input dimensions, 18px Bug field-row margins and 12px stacked suggestion gaps are preserved. At widths <=700px, authenticated navigation has the same 44px minimum row height as the centered Logout/theme group, balancing visible gaps above/below identity without shrinking action targets or changing guest/desktop layout.

This refinement used static-only servers on ports 8148/8149: real frontend markup/styles/helpers, fictional identity and in-memory suggestions, no application imports, database or application API routes. Login, Registration, New Bug and Edit Bug were rendered at 320/390/1280px in both themes with no page overflow. Both notices measured exactly two 21px text lines at 1280px and wrapped normally on mobile; dismiss targets measured 32x32px with reserved clearance. All visible field labels retained 2px padding, zero bottom margin and compact spacing (about 0.67px from inline line-box geometry; zero grid gap beside desktop suggestions). Auth input dimensions matched the earlier compact baseline. Pending Title/Description suggestions in both forms aligned with their controls on desktop and retained 12px stacked gaps on mobile. Keyboard notice dismissal showed a 2px focus outline, removed the accessible description and restored AI Assist focus; dismissal persisted through Edit refresh and navigation to New Bug. With pending Edit suggestions it preserved both cards, form value and guidance, focusing Use All. Headers with a long fictional email were checked at 320/390/700px in both themes: centers matched within rounding, visible identity gaps differed by less than 0.01px and email wrapping caused no overflow. At 1280px the header retained its desktop flex layout. Screenshots were inspected for the desktop notice, mobile notice and mobile header.

Earlier verification: `node --test tests/frontend/*.test.cjs` passed 94 tests, 0 failures and 0 skipped (396.11ms). `node --check` passed for `tests/frontend/ai-disclosure.test.cjs`, `frontend/js/ai-notice.js`, `frontend/js/project.js` and `frontend/js/bugs.js`; `git diff --check` passed. No backend changes/tests, database access, live provider calls or handoff script execution occurred in this refinement. Visual verification is limited to the in-app browser and static fixtures; full live application integration, physical-device, broader cross-browser and screen-reader checks were not repeated. Broader Increment 3 sign-off and existing AC coverage statuses are unchanged.

Screenshot-based visual correction: the dismiss glyph now aligns with the notice's first 21px text line rather than centering inside its unchanged 32x32px target. The top/right inset, accessible label, 2px keyboard focus outline and 8px text clearance are preserved. Mobile authenticated navigation returns to its content height; spacing reuses the shared 8px header gap and balances visible action content within the existing 44px targets, leaving room for focus outlines. Desktop and guest header rules retain their existing behavior.

Verification used the database-free static fixture on port 8150, with real frontend markup/styles, a fictional long email/role and an in-memory pre-change stylesheet snapshot. Actual screenshots were inspected at 320/390/700px for the header and 390/1280px for both notices, in both themes. DOM text ranges and screenshot glyph pixels were measured rather than inferring spacing from row heights: visible header gaps were approximately 12.5-14.6 CSS px; the dismiss glyph's visible center aligned within 0.6px of the first text line. Both notices retained exactly two lines at 1280px, normal mobile wrapping and no page overflow. Targets remained 32x32px/44px high, notice keyboard focus remained visible, and header keyboard focus cleared the identity text. Desktop header text/target geometry matched the pre-change snapshot exactly in both themes. `node --test tests/frontend/*.test.cjs` passed 94 tests (0 failures, 0 skipped; 605.84ms); `git diff --check` passed. Only CSS and these traceability notes changed in this correction. No database access, provider calls, backend changes or handoff script execution occurred. Verification remains limited to the in-app browser and static fixtures; existing AC coverage statuses are unchanged.

Focused header regression/bottom-spacing and dismiss-glyph follow-up: read-only comparison against committed HEAD `3c4dad5` confirmed that the 701-1200px two-row grid (wordmark above navigation/account controls) is pre-existing. Before any CSS change, rendered text/target/header geometry matched HEAD exactly at 701/885/1199/1200/1201/1543px in both themes; 1201px and above retain the existing flex layout. The earlier approved mobile refinements at 700px differ from HEAD and were preserved. Final checks at 700/701/885/1199/1200/1201/1543px matched the pre-task working-tree geometry exactly: no intermediate/desktop responsive regression was found. At 320/390px, authenticated header bottom padding now uses 2px instead of 10px within the existing <=450px breakpoint: header height decreases exactly 8px while all visible content positions, balanced gaps, long-email wrapping and 44px targets remain unchanged. Both notices move only the visible dismiss glyph 4px right within the same 32x32px target, preserving first-line vertical alignment, 8px text clearance and the visible 2px keyboard focus outline. New/Edit notices retained two lines at 1280px and normal wrapping at 390px in both themes, with no page overflow.

Verification used only the approved `http://127.0.0.1:8148` database-free static fixture; port availability, listener PID and the owned static-server command/configuration were verified before interaction. Real frontend markup/styles were rendered with fictional identity content; HEAD and pre-task stylesheets were held in memory for comparisons. No application imports, application API routes, database access or provider requests were used. Screenshots were inspected for both baseline themes, narrow before/after headers and both notices. `node --test tests/frontend/*.test.cjs` passed 94 tests (0 failures, 0 skipped; 405.78ms); `git diff --check` passed. Only the shared CSS and these notes changed in the repository during this follow-up. Full live application, physical-device, cross-browser and screen-reader checks were not repeated; existing AC coverage statuses remain unchanged. No handoff script was run.

## Shared mobile header cleanup — 14 October 2026

This supersedes the earlier mobile header compensations above; AI notices, forms and page-content styling are unchanged. At <=700px, guest headers use flex wrapping for the existing navigation groups, with the same 16px gap between and within groups. Hidden guest About navigation contributes no flex item, so Register/Login center without restoring About's self-link. Authenticated headers keep the single-column mobile grid. Shared 4px row gaps and centered 44px navigation/control targets replace the identity margin, negative action-row margin and asymmetric control padding. The shared mobile container uses 16px/12px/4px top/horizontal/bottom padding for optical spacing. The wordmark uses `clamp(28px, 9vw, 34px)` with 1.2 line height: 28.8px at 320px and 34px at 390/450/700px, larger than each checked page/project heading without overflow. The graphic and its proportions/colors are preserved.

Header-only rules consolidated/removed: the trailing <=700px account-controls block moved into the existing mobile header section; the guest auto-sized two-column tracks and forced navigation columns were removed; unused grid placement on flex children was removed; the obsolete mobile-header-gap custom property and calculated identity/action margins were removed; the <=450px header padding, authenticated bottom-padding exception, 18px wordmark and overridden 38px theme-toggle dimensions were removed. The divider pseudo-element, its positioning context and theme-icon bottom-padding adjustment were removed. Logout now uses balanced 8px/4px padding, and the theme target uses zero padding, retaining the existing icons and keyboard focus rules. No HTML structure, JavaScript, dependency or unrelated CSS was changed.

Before/after browser evidence used only the approved database-free static server at `http://127.0.0.1:8148`, with its listener PID/command verified, synthetic session/identity/project content, and the actual theme/logout scripts. The final matrix contains 144 states per version: guest Login/Registration/About/Privacy Policy and authenticated Projects/Project/Bug/About at 320/390/450/700/701/885/1200/1201/1280px in both themes. All 80 states above 700px matched the before geometry and computed styles exactly, preserving the established two-row intermediate and desktop layouts. All 64 mobile states passed overflow, wordmark hierarchy, 44px target-height, link-order, guest spacing and hidden-About checks. Guest visible link gaps measured 16px and the groups centered within rounding. Screenshots and glyph pixels were inspected: outer whitespace is approximately 18-25px, with small font/sun/moon ink differences; former oversized bottom whitespace is reduced without per-icon offsets. Larger mobile branding and navigation targets increase narrow-header height (at 320px, guest Login about 126.5 to 152.8px; Project about 157.9 to 190.2px), while page-content styles remain unchanged.

Sixty final keyboard-focus checks passed across all eight header states in both themes; Tab order, guest navigation, authenticated About/Projects navigation, synthetic Bug-to-Project navigation, theme changes/refresh persistence and actual client Logout/guest-state restoration were also exercised. Source hashes confirmed all seven page files and theme/logout JavaScript were unchanged. `node --test tests/frontend/*.test.cjs` passed 94 tests (0 failures, 0 skipped; 424.92ms), and `git diff --check` passed. Existing frontend tests were unchanged because the implementation change is CSS-only; visual/computed regression evidence is recorded separately, not promoted to additional unit tests or full AC coverage. No database, real application records, backend or provider calls were used. Live sign-in/authorization, backend-dependent routing/data loading, screen-reader, physical-device and other-browser behavior were not verified. Existing AC coverage statuses remain unchanged; no handoff script was run.

Focused wordmark/divider follow-up: only the existing <=700px header section changed. The stylized B keeps its rotation but uses 1.1em instead of the inherited 1.225em; the beetle uses a 1em square instead of 1.2em and 0.02em horizontal margins instead of 0.08em. Its existing asset and mobile untransformed alignment remain intact. The responsive title font, header padding, navigation/identity spacing and all >=701px rules are unchanged. A 1x16px decorative flex item restores the authenticated mobile divider, with equal 6px gaps and explicit item order instead of positioning offsets; guest actions are unaffected.

The verified database-free static fixture on approved port 8148 rendered synthetic Project and guest Login headers before/after at 320/390/450/700/701/885/1200/1280px in both themes (32 states per version). Original-scale wordmark screenshots were compared, including the earlier smaller mobile wordmark and committed HEAD styles. All 16 >=701px before/after states matched header geometry/styles exactly; eight wider Project comparisons also matched HEAD. All final states had no page overflow, and mobile guest navigation retained 16px gaps. Mobile header height decreased only 0.35-0.43px from internal font geometry; outer spacing rules were untouched. Twelve mobile action-focus checks at 320/390/700px passed with 44px targets and visible 2px outlines; divider/control centers aligned vertically. Actual theme changes, refresh persistence and client Logout/guest restoration passed using the synthetic session. Page HTML and theme/logout source hashes remained unchanged. `node --test tests/frontend/*.test.cjs` passed 94 tests (0 failures, 0 skipped; 367.26ms); `git diff --check` passed. No database, backend, provider, physical-device or additional browser-engine testing occurred; AC coverage statuses remain unchanged. No handoff script was run.

Shared wordmark correction supersedes the mobile B/beetle sizing above. The <=700px `.wordmark-b` font-size override and the entire `.wordmark-beetle` width/height/margin/`transform: none` override were removed. Mobile now shares the unchanged base B styling (1.225em, -7deg rotation) and beetle styling (1.8em square, -0.48em/-0.58em margins, `translate(-3px, -0.05em) rotate(15deg)`) with wider viewports. Prefix/Triage spacing and the image asset remain unchanged. Only the mobile outer title font/line-height remain responsive; a 1.2em `.wordmark` container height preserves the existing compact row without resizing or repositioning its internal graphic. Header spacing, navigation and the restored flex divider are untouched.

Before source changes, a temporary inline CSS override in the database-free port-8148 fixture previewed shared internal styling at 320/390px in both themes. Shared styling alone increased intrinsic row height; retaining the existing container height preserved the surrounding layout and was visually checked before implementation. The four final renderings matched that preview exactly. Synthetic Project and guest Login were then compared before/after at 320/390/450/700/701/1280px in both themes (24 final states). Actual-scale screenshots showed the shared desktop-style graphic/text relationship, including its intentional interlocking B/beetle segment, without clipping, wrapping or page overflow. The larger responsive title font is retained. Non-wordmark header/control/navigation/page-heading geometry remained within 0.011px rounding; 701/1280px headers matched exactly. Twelve action-focus checks at 320/390/700px retained 44px targets, 2px outlines and the 1x16px divider; theme toggles and client Logout worked with the synthetic session. Page HTML and theme/logout source hashes were unchanged. `node --test tests/frontend/*.test.cjs` passed 94 tests (0 failures, 0 skipped; 404.60ms); `git diff --check` passed. Only wordmark CSS and these notes changed in this correction. No database, backend, live authentication, physical-device or additional browser-engine checks were performed; AC coverage statuses remain unchanged. No handoff script was run.

Final mobile typography/optical-divider check: the responsive title maximum is now the existing desktop 32px. Computed sizes before/after are 28.8/28.8px at 320px, 34/32px at 390/700px and 32/32px at 701/1280px. The shared B/beetle rules, asset and transforms are untouched. About and Logout already matched in both themes: Arial/sans-serif, weight 400, 14px/16.8px font/line-height at 320/390px, 16px/19.2px at 700px, and 18px/21.6px above 700px; no typography adjustment was needed for either control. The mobile authenticated action row replaces its two 6px flex gaps with equal 18px content padding inside both controls and automatic widths. This is normal layout padding, without separator positioning offsets or theme-specific corrections. Measured targets remain 44px high; the theme target is approximately 49.49px wide for the sun and 45.14px for the moon. The smaller moon's intrinsic width plus padding still exceeds 44px. Guest controls, divider styling and all other header spacing rules are unchanged.

Before/after verification used only the verified database-free fixture on port 8148 and fictional content: Project at 320/390/700/701/1280px and guest Login at 320/390/700/1280px in both themes (18 states per version). No overflow occurred. At each of 320/390/700px, DOM text-range clearance is now 18px on both sides of the divider; actual screenshot ink measurements are approximately 17/18px in dark mode and 17/19px in light mode, replacing the previous 10/21px and 10/24px. Small remaining pixel differences reflect glyph bearings and rasterization; no per-icon offsets were added. The action row remains centered. Navigation gaps and all source HTML/theme/logout scripts are unchanged. The font cap naturally reduces header height by about 2.69px at 390/700px; vertical padding/gaps and 320px height are unchanged. All six wider-screen before/after screenshots were pixel-identical. Eighteen keyboard-focus checks passed with visible 2px outlines and at least 44px-high targets; Logout-to-theme Tab order, keyboard theme activation/refresh persistence, About navigation and synthetic Logout passed. `node --test tests/frontend/*.test.cjs` passed 94 tests (0 failures, 0 skipped; 376.51ms); `git diff --check` passed. This CSS-only change adds no synthetic unit tests for CSS declarations. Existing AC coverage statuses and browser/backend limitations remain unchanged; no real data or handoff script was accessed.

Final mobile top-spacing/separator follow-up supersedes the divider restoration above. At <=700px, header top padding increases from 16px to 20px; horizontal/bottom padding, internal gaps, typography and shared B/beetle styling are unchanged. The conditional zero-gap rule, 18px control insets/automatic widths, divider pseudo-element and theme ordering override are removed. The existing centered flex row now uses its simple 12px gap, 44px theme target and at least 44x44px Logout target; guest headers retain only their theme control.

The verified database-free port-8148 fixture compared 128 states per version: guest Login/Registration/About/Privacy Policy and authenticated Projects/Project/Bug/About at 320/390/450/700/701/885/1200/1280px in both themes. Screenshot ink measurements include the beetle: representative Project top whitespace changes from approximately 9-11px to 14-15px on mobile, while 701px remains 13px; approximate pixel edges vary with antialiasing and screenshot compression, while the geometric shift is exactly 4px. All 64 mobile headers grow exactly 4px, with unchanged internal geometry/wrapping/navigation gaps and about 17-23px visible bottom whitespace. All 64 wider before/after screenshots are pixel-identical. No page overflow or new clipping was found; the divider is absent in every final mobile state. All 180 keyboard-focus checks at 320/390/700px and 60 natural Tab-order checks passed; theme activation/refresh persistence, navigation and client Logout/guest restoration passed with synthetic sessions. Page HTML, theme/logout scripts and AGENTS.md hashes remained unchanged. `node --test tests/frontend/*.test.cjs` passed 94 tests (0 failures, 0 skipped; 394.41ms); `git diff --check` passed. Only header CSS and these notes changed. No database/backend, physical-device, additional browser-engine or screen-reader testing occurred; AC coverage statuses remain unchanged. No handoff script was run.

Focused auth-card width correction: the <=700px `max-width: 100%` selector group incorrectly overrode the existing 500px standard-form maximum for Login and Registration. Removing only `#login-form` and `#register-form` from that group restores the shared 500px cap and existing auto-margin centering; the project/bug form override and all header CSS remain unchanged. Both auth cards now measure 296/366/426/500/500/500/500px at 320/390/450/700/701/885/1280px respectively, in both themes. Only the sampled 700px width changes, from 668px to 500px. Its full-width inputs narrow from about 630.67px to 462.67px while retaining 44px height; no input-sizing rule changed.

Before/after checks used the verified database-free fixture on approved port 8148: both real auth pages at all seven widths in both themes (28 states per version). The baseline reproduced the 700/701px discontinuity, and final checks verified matching 500px maxima. All cards are centered without overflow/clipped controls. Card tops/heights, padding, borders, radii, labels' relative offsets, input heights and button rectangles remain unchanged. At the other six widths, input/label rectangles and all 24 full-page screenshots are identical; all 28 header screenshots are identical. Source HTML/theme/logout and AGENTS.md hashes remained unchanged. `node --test tests/frontend/*.test.cjs` passed 94 tests (0 failures, 0 skipped; 460.63ms); `git diff --check` passed. Only two form-selector lines and these notes changed. Authentication/registration submission was not exercised: fixture forms are inert, with no application API/database access. Physical-device, other-engine and screen-reader checks were not repeated; AC coverage statuses remain unchanged. No handoff script was run.
