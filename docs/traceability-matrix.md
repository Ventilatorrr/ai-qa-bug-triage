# Traceability Matrix

## Purpose

This matrix provides requirements traceability and maintains an inventory of automated tests.

It connects:

* Requirements
* User Stories
* Acceptance Criteria
* Automated Tests
* Test Types
* Test Status

BDD scenarios are maintained separately as behavioural specifications.

Every automated test should appear in this matrix. Not every test must map directly to an Acceptance Criterion; additional tests may be created to cover technical risks, edge cases, security concerns, or other areas not explicitly defined by the requirements.

The matrix is updated throughout development and testing.

## Status

* **Covered** — The required behaviour is implemented and adequately tested.

* **Partial** — Some aspects of the acceptance criterion are covered, but additional coverage is required.

* **Pending** — The functionality or required test has not yet been implemented.

* **Manual** — The behaviour is currently verified through manual testing rather than automated testing.

* **Specification Only** — A BDD scenario exists as a behavioural specification but is not currently executable.

## Test Types

* **API** — API-level functional testing

* **Security** — Security and authorization testing

* **Database** — Database and data-integrity testing

* **UI** — User-interface testing

* **BDD** — Executable Behaviour-Driven Development test

* **Validation** — Input and validation testing

---

## Increment 1 — User & Project Management

### REQ-001 — User Registration

| REQ     | US       | AC                                 | Automated Test                                                  | Test Type           | Status  |
| ------- | -------- | ---------------------------------- | --------------------------------------------------------------- | ------------------- | ------- |
| REQ-001 | US-001.1 | AC-001.1 — Successful Registration | `test_successful_registration`                                  | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.2 — Duplicate Email         | `test_registration_with_duplicate_email`                        | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.3 — Invalid Email           | `test_registration_with_invalid_email`                          | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.4 — Invalid Password        | `test_registration_with_short_password`                         | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.4 — Invalid Password        | `test_registration_without_uppercase_password`                  | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.4 — Invalid Password        | `test_registration_without_lowercase_password`                  | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.4 — Invalid Password        | `test_registration_without_number_password`                     | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.5 — Password Security       | `test_password_is_not_stored_as_plain_text`                     | Database / Security | Covered |
| —       | —        | —                                  | `test_registration_rejects_invalid_password_for_existing_email` | API / Validation    | Covered |

### REQ-002 — User Login

| REQ     | US       | AC                             | Automated Test                       | Test Type | Status  |
| ------- | -------- | ------------------------------ | ------------------------------------ | --------- | ------- |
| REQ-002 | US-002.1 | AC-002.1 — Successful Login    | `test_successful_login`              | API       | Covered |
| REQ-002 | US-002.1 | AC-002.1 — Successful Login    | —                                    | UI        | Manual  |
| REQ-002 | US-002.1 | AC-002.2 — Invalid Credentials | `test_login_with_incorrect_password` | API       | Covered |
| REQ-002 | US-002.1 | AC-002.2 — Invalid Credentials | `test_login_with_unknown_email`      | API       | Covered |

### REQ-003 — Protected Access

| REQ     | US       | AC                                | Automated Test                                               | Test Type      | Status  |
| ------- | -------- | --------------------------------- | ------------------------------------------------------------ | -------------- | ------- |
| REQ-003 | US-003.1 | AC-003.1 — Authenticated Access   | `test_authenticated_user_can_access_protected_endpoint`      | API            | Covered |
| REQ-003 | US-003.1 | AC-003.2 — Unauthenticated Access | `test_unauthenticated_user_cannot_access_protected_endpoint` | API / Security | Covered |
| REQ-003 | US-003.1 | AC-003.2 — Unauthenticated Access | —                                                            | UI             | Manual  |
| REQ-003 | US-003.1 | AC-003.3 — Invalid Authentication | `test_invalid_token_cannot_access_protected_endpoint`        | API / Security | Covered |

### REQ-004 — User Logout

| REQ     | US       | AC                                       | Automated Test | Test Type | Status |
| ------- | -------- | ---------------------------------------- | -------------- | --------- | ------ |
| REQ-004 | US-004.1 | AC-004.1 — Successful Logout             | —              | UI        | Manual |
| REQ-004 | US-004.1 | AC-004.2 — Protected Access After Logout | —              | UI        | Manual |

### REQ-005 — Project Creation

| REQ     | US       | AC                                     | Automated Test                                    | Test Type | Status  |
| ------- | -------- | -------------------------------------- | ------------------------------------------------- | --------- | ------- |
| REQ-005 | US-005.1 | AC-005.1 — Successful Project Creation | `test_create_project`                             | API       | Covered |
| REQ-005 | US-005.1 | AC-005.2 — Invalid Project Name        | `test_create_project_with_empty_name`             | API       | Covered |
| REQ-005 | US-005.1 | AC-005.3 — Unauthenticated User        | `test_unauthenticated_user_cannot_create_project` | API       | Covered |

### REQ-006 — Project Access

| REQ     | US       | AC                                     | Automated Test                                  | Test Type      | Status  |
| ------- | -------- | -------------------------------------- | ----------------------------------------------- | -------------- | ------- |
| REQ-006 | US-006.1 | AC-006.1 — View Project List           | `test_get_projects`                             | API            | Covered |
| REQ-006 | US-006.1 | AC-006.2 — Project List Authorization  | `test_user_only_sees_own_projects`              | API / Security | Covered |
| REQ-006 | US-006.1 | AC-006.3 — Open Project                | `test_get_project`                              | API            | Covered |
| REQ-006 | US-006.1 | AC-006.4 — Unauthorized Project Access | `test_user_cannot_access_another_users_project` | API / Security | Covered |

### REQ-007 — Project Name Editing

| REQ     | US       | AC                                           | Automated Test                                     | Test Type      | Status  |
| ------- | -------- | -------------------------------------------- | -------------------------------------------------- | -------------- | ------- |
| REQ-007 | US-007.1 | AC-007.1 — Successful Project Name Editing   | `test_edit_project_name`                           | API            | Covered |
| REQ-007 | US-007.1 | AC-007.2 — Unauthorized Project Name Editing | `test_user_cannot_edit_another_users_project_name` | API / Security | Covered |

### REQ-008 — Project Deletion

| REQ     | US       | AC                                       | Automated Test                                  | Test Type      | Status  |
| ------- | -------- | ---------------------------------------- | ----------------------------------------------- | -------------- | ------- |
| REQ-008 | US-008.1 | AC-008.1 — Successful Project Deletion   | `test_delete_project`                           | API            | Partial |
| REQ-008 | US-008.1 | AC-008.2 — Unauthorized Project Deletion | `test_user_cannot_delete_another_users_project` | API / Security | Covered |

**Coverage note:** AC-008.1 is currently **Partial** because the API deletion is automated, while the required browser confirmation is currently tested manually. Playwright coverage will be added after Increment 1 is complete.

### REQ-009 — Project Member Management

| REQ     | US       | AC                              | Automated Test                                                    | Test Type        | Status  |
| ------- | -------- | ------------------------------- | ----------------------------------------------------------------- | ---------------- | ------- |
| REQ-009 | US-009.1 | AC-009.1 — Add Member           | `test_owner_can_add_project_member`                               | API / Validation | Covered |
| REQ-009 | US-009.1 | AC-009.1 — Add Member           | `test_added_member_can_access_project`                            | API / Security   | Covered |
| REQ-009 | US-009.1 | AC-009.2 — Remove Member        | `test_owner_can_remove_project_member`                            | API              | Covered |
| REQ-009 | US-009.1 | AC-009.2 — Remove Member        | `test_removed_member_can_no_longer_access_project`                | API / Security   | Covered |
| REQ-009 | US-009.1 | AC-009.3 — Invalid Member       | `test_project_owner_cannot_add_user_who_does_not_have_an_account` | API / Validation | Covered |
| REQ-009 | US-009.1 | AC-009.4 — Duplicate Member     | `test_project_owner_cannot_add_same_user_more_than_once`          | API / Validation | Covered |
| REQ-009 | US-009.1 | AC-009.5 — View Project Members | `test_project_member_can_view_project_members`                    | API / Security   | Covered |
| —       | —        | —                               | `test_project_owner_cannot_remove_themselves`                     | API / Security   | Covered |

### REQ-010 — Project Roles and Permissions

| REQ     | US       | AC                                                | Automated Test                                 | Test Type      | Status  |
| ------- | -------- | ------------------------------------------------- | ---------------------------------------------- | -------------- | ------- |
| REQ-010 | US-010.1 | AC-010.1 — Project Owner Role                     | `test_project_creator_is_project_owner`        | API / Security | Covered |
| REQ-010 | US-010.1 | AC-010.2 — QA Analyst Role                        | `test_qa_analyst_can_access_project`           | API / Security | Covered |
| REQ-010 | US-010.1 | AC-010.3 — Developer Role                         | `test_developer_can_access_project`            | API / Security | Covered |
| REQ-010 | US-010.1 | AC-010.4 — Unauthorized Project Member Management | `test_non_owner_cannot_manage_project_members` | API / Security | Covered |
| REQ-010 | US-010.1 | AC-010.5 — Unauthorized Project Actions           | `test_non_owner_cannot_edit_project`           | API / Security | Covered |
| REQ-010 | US-010.1 | AC-010.5 — Unauthorized Project Actions           | `test_non_owner_cannot_delete_project`         | API / Security | Covered |

---

## Increment 2 — Bug Management

### REQ-011 — Bug Creation

| REQ     | US     | AC                                   | Automated Test                                      | Test Type        | Status  |
| ------- | ------ | ------------------------------------ | --------------------------------------------------- | ---------------- | ------- |
| REQ-011 | US-011 | AC-011.1 — Successful Bug Creation   | `test_project_member_can_create_bug`                | API              | Covered |
| REQ-011 | US-011 | AC-011.2 — Missing Bug Title         | `test_bug_creation_rejected_without_title`          | API / Validation | Covered |
| REQ-011 | US-011 | AC-011.3 — Unauthorized Bug Creation | `test_non_member_cannot_create_bug`                 | API / Security   | Covered |
| REQ-011 | US-011 | AC-011.4 — Optional Bug Information  | `test_bug_can_be_created_with_optional_information` | API / Validation | Covered |

### REQ-012 — Bug Access

| REQ     | US     | AC                                 | Automated Test                            | Test Type      | Status  |
| ------- | ------ | ---------------------------------- | ----------------------------------------- | -------------- | ------- |
| REQ-012 | US-012 | AC-012.1 — View Bug List           | `test_project_member_can_view_bug_list`   | API            | Covered |
| REQ-012 | US-012 | AC-012.2 — Open Bug Report         | `test_project_member_can_open_bug_report` | API            | Covered |
| REQ-012 | US-012 | AC-012.3 — Unauthorized Bug Access | `test_non_member_cannot_open_bug_report`  | API / Security | Covered |
| REQ-012 | US-012 | AC-012.4 — Sort Bug Reports        | —                                         | UI             | Pending |

### REQ-013 — Bug Editing

| REQ     | US     | AC                                  | Automated Test                                            | Test Type        | Status  |
| ------- | ------ | ----------------------------------- | --------------------------------------------------------- | ---------------- | ------- |
| REQ-013 | US-013 | AC-013.1 — Edit Bug Report          | `test_project_member_can_edit_bug_report`                 | API              | Covered |
| REQ-013 | US-013 | AC-013.2 — Optional Bug Information | `test_project_member_can_update_optional_bug_information` | API / Validation | Covered |
| REQ-013 | US-013 | AC-013.3 — Unauthorized Bug Editing | `test_non_member_cannot_edit_bug_report`                  | API / Security   | Covered |

### REQ-014 — Bug Deletion

| REQ     | US     | AC                                      | Automated Test                               | Test Type      | Status  |
| ------- | ------ | --------------------------------------- | -------------------------------------------- | -------------- | ------- |
| REQ-014 | US-014 | AC-014.1 — Successful Bug Deletion      | `test_authorized_member_can_delete_bug`      | API            | Covered |
| REQ-014 | US-014 | AC-014.1 — Delete Confirmation Required | —                                            | UI             | Pending |
| REQ-014 | US-014 | AC-014.2 — Unauthorized Bug Deletion    | `test_unauthorized_member_cannot_delete_bug` | API / Security | Covered |

### REQ-015 — Bug Assignment

| REQ     | US     | AC                                     | Automated Test                                  | Test Type        | Status  |
| ------- | ------ | -------------------------------------- | ----------------------------------------------- | ---------------- | ------- |
| REQ-015 | US-015 | AC-015.1 — Assign and Unassign Bugs    | `test_authorized_member_can_assign_bug`         | API              | Covered |
| REQ-015 | US-015 | AC-015.1 — Assign and Unassign Bugs    | `test_authorized_member_can_unassign_bug`       | API              | Covered |
| REQ-015 | US-015 | AC-015.2 — Invalid Assignment          | `test_bug_cannot_be_assigned_to_invalid_member` | API / Validation | Covered |
| REQ-015 | US-015 | AC-015.3 — Unauthorized Bug Assignment | `test_unauthorized_member_cannot_assign_bug`    | API / Security   | Covered |
| REQ-015 | US-015 | AC-015.4 — Change Bug Assignee         | `test_authorized_member_can_reassign_bug`       | API              | Covered |

### REQ-016 — Bug Classification

| REQ | US | AC | Automated Test | Test Type | Status |
|---|---|---|---|---|---|
| REQ-016 | US-016 | AC-016.1 — Set Bug Severity | `test_project_member_can_set_bug_severity` | API | Covered |
| REQ-016 | US-016 | AC-016.2 — Set Bug Priority | `test_project_member_can_set_bug_priority` | API | Covered |
| REQ-016 | US-016 | AC-016.3 — Update Bug Classification | `test_project_member_can_update_bug_classification` | API | Covered |
| REQ-016 | US-016 | AC-016.4 — Unauthorized Bug Classification | `test_non_member_cannot_update_bug_classification` | API / Security | Covered |
| REQ-016 | US-016 | — | `test_developer_can_update_bug_classification` | API | Covered |
| REQ-016 | US-016 | — | `test_bug_rejects_invalid_severity` | API / Validation | Covered |
| REQ-016 | US-016 | — | `test_bug_rejects_invalid_priority` | API / Validation | Covered |

### REQ-017 — Bug Lifecycle

| REQ     | US     | AC                                    | Automated Test | Test Type        | Status  |
| ------- | ------ | ------------------------------------- | -------------- | ---------------- | ------- |
| REQ-017 | US-017 | AC-017.1 — Bug Status                 | —              | API / Validation | Pending |
| REQ-017 | US-017 | AC-017.2 — Triage to Open             | —              | API / Security   | Pending |
| REQ-017 | US-017 | AC-017.3 — Open to Development        | —              | API / Security   | Pending |
| REQ-017 | US-017 | AC-017.4 — Development to Testing     | —              | API / Security   | Pending |
| REQ-017 | US-017 | AC-017.5 — Testing Outcome            | —              | API / Security   | Pending |
| REQ-017 | US-017 | AC-017.6 — Closed Bugs                | —              | API / Validation | Pending |
| REQ-017 | US-017 | AC-017.7 — Invalid Status Transitions | —              | API / Validation | Pending |
| REQ-017 | US-017 | AC-017.8 — Status Update Timestamp    | —              | API              | Pending |




## BDD Specification Status

The current `.feature` files describe intended behaviour but are **not currently executable with pytest-bdd**.

They are therefore treated as behavioural specifications rather than automated tests.

Current feature files:

```text
tests/bdd/features/authentication.feature
tests/bdd/features/project_creation.feature
```

Executable BDD automation may be added later as a representative example rather than being used for the entire test suite.
