# Traceability Matrix

## Purpose

This matrix provides requirements traceability and maintains an inventory of automated tests.

It connects:

* Requirements
* User Stories
* Acceptance Criteria
* BDD scenarios
* Automated tests
* Test types
* Test status

Every automated test should appear in this matrix. Not every test must map directly to an Acceptance Criterion; additional tests may be created to cover technical risks, edge cases, security concerns, or other areas not explicitly defined by the requirements.

The matrix is updated throughout development and testing.

## Status

* **Covered** — The required behaviour is implemented and adequately tested.
* **Partial** — Some aspects of the acceptance criterion are covered, but additional coverage is required.
* **Pending** — The functionality or required test has not yet been implemented.
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

| REQ     | US       | AC                                 | BDD Scenario                                         | Automated Test                                                  | Test Type           | Status  |
| ------- | -------- | ---------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------- | ------------------- | ------- |
| REQ-001 | US-001.1 | AC-001.1 — Successful Registration | Successfully register an account                     | `test_successful_registration`                                  | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.2 — Duplicate Email         | Register with an already registered email address    | `test_registration_with_duplicate_email`                        | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.3 — Invalid Email           | Register with an invalid email address               | `test_registration_with_invalid_email`                          | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.4 — Invalid Password        | Register with a password that is too short           | `test_registration_with_short_password`                         | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.4 — Invalid Password        | Register with a password without an uppercase letter | `test_registration_without_uppercase_password`                  | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.4 — Invalid Password        | Register with a password without a lowercase letter  | `test_registration_without_lowercase_password`                  | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.4 — Invalid Password        | Register with a password without a number            | `test_registration_without_number_password`                     | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.5 — Password Security       | —                                                    | `test_password_is_not_stored_as_plain_text`                     | Security / Database | Covered |
| —       | —        | —                                  | —                                                    | `test_registration_rejects_invalid_password_for_existing_email` | API / Validation    | Covered |


### REQ-002 — User Login

| REQ     | US       | AC                             | BDD Scenario                                 | Automated Test                       | Test Type | Status  |
| ------- | -------- | ------------------------------ | -------------------------------------------- | ------------------------------------ | --------- | ------- |
| REQ-002 | US-002.1 | AC-002.1 — Successful Login    | Successfully log in                          | `test_successful_login`              | API       | Covered |
| REQ-002 | US-002.1 | AC-002.1 — Successful Login    | Successfully log in and redirect to Projects | —                                    | UI        | Manual  |
| REQ-002 | US-002.1 | AC-002.2 — Invalid Credentials | Log in with an incorrect password            | `test_login_with_incorrect_password` | API       | Covered |
| REQ-002 | US-002.1 | AC-002.2 — Invalid Credentials | Log in with an unknown email address         | `test_login_with_unknown_email`      | API       | Covered | 


### REQ-003 — Protected Access

| REQ     | US          | AC                                | BDD Scenario                                               | Automated Test                                               | Test Type        | Status  |
| ------- | ----------- | --------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------ | ---------------- | ------- |
| REQ-003 | US-003.1    | AC-003.1 — Authenticated Access   | Authenticated user accesses a protected area               | `test_authenticated_user_can_access_protected_endpoint`      | API              | Covered |
| REQ-003 | US-003.1    | AC-003.2 — Unauthenticated Access | Unauthenticated user accesses a protected area             | `test_unauthenticated_user_cannot_access_protected_endpoint` | API / Security   | Covered |
| REQ-003 | US-003.1    | AC-003.2 — Unauthenticated Access | Unauthenticated user is redirected to the login page       | —                                                            | UI               | Manual  |
| REQ-003 | US-003.1    | AC-003.3 — Invalid Authentication | User accesses a protected area with invalid authentication | `test_invalid_token_cannot_access_protected_endpoint`        | API / Security   | Covered |


### REQ-004 — User Logout

| REQ     | US       | AC                                       | BDD Scenario                                         | Automated Test | Test Type | Status |
| ------- | -------- | ---------------------------------------- | ---------------------------------------------------- | -------------- | --------- | ------ |
| REQ-004 | US-004.1 | AC-004.1 — Successful Logout             | Successfully log out                                 | —              | UI        | Manual |
| REQ-004 | US-004.1 | AC-004.2 — Protected Access After Logout | Attempt to access a protected area after logging out | —              | UI        | Manual |


### REQ-005 — Project Creation

| REQ     | US       | AC                                     | BDD Scenario                                      | Automated Test                                    | Test Type | Status  |
| ------- | -------- | -------------------------------------- | ------------------------------------------------- | ------------------------------------------------- | --------- | ------- |
| REQ-005 | US-005.1 | AC-005.1 — Successful Project Creation | Successfully create a project                     | `test_create_project`                             | API       | Covered |
| REQ-005 | US-005.1 | AC-005.2 — Invalid Project Name        | Create a project with an empty name               | `test_create_project_with_empty_name`             | API       | Covered |
| REQ-005 | US-005.1 | AC-005.3 — Unauthenticated User        | Unauthenticated user attempts to create a project | `test_unauthenticated_user_cannot_create_project` | API       | Covered |


### REQ-006 — Project Access

| REQ     | US       | AC                                     | BDD Scenario                            | Automated Test                                  | Test Type      | Status  |
| ------- | -------- | -------------------------------------- | --------------------------------------- | ----------------------------------------------- | -------------- | ------- |
| REQ-006 | US-006.1 | AC-006.1 — View Project List           | View the project list                   | `test_get_projects`                             | API            | Covered |
| REQ-006 | US-006.1 | AC-006.2 — Project List Authorization  | View only authorized projects           | `test_user_only_sees_own_projects`              | API / Security | Covered |
| REQ-006 | US-006.1 | AC-006.3 — Open Project                | Open an authorized project              | `test_get_project`                              | API            | Covered |
| REQ-006 | US-006.1 | AC-006.4 — Unauthorized Project Access | Attempt to open an unauthorized project | `test_user_cannot_access_another_users_project` | API / Security | Covered |

### REQ-007 — Project Name Editing

| REQ     | US       | AC                                           | Automated Test                                | Test Type      | Status  |
| ------- | -------- | -------------------------------------------- | --------------------------------------------- | -------------- | ------- |
| REQ-007 | US-007.1 | AC-007.1 — Successful Project Name Editing   | `test_update_project`                         | API            | Covered |
| REQ-007 | US-007.1 | AC-007.2 — Unauthorized Project Name Editing | `test_user_cannot_edit_another_users_project` | API / Security | Covered |

### REQ-008 — Project Deletion

| REQ     | US       | AC                                       | Automated Test                                  | Test Type      | Status  |
| ------- | -------- | ---------------------------------------- | ----------------------------------------------- | -------------- | ------- |
| REQ-008 | US-008.1 | AC-008.1 — Successful Project Deletion   | `test_delete_project`                           | API            | Partial |
| REQ-008 | US-008.1 | AC-008.2 — Unauthorized Project Deletion | `test_user_cannot_delete_another_users_project` | API / Security | Covered |

**Coverage note:** AC-008.1 is currently **Partial** because the API deletion is automated, while the required browser confirmation is currently tested manually. Playwright coverage will be added after Increment 1 is complete.

### REQ-009 — Project Member Management

| REQ     | US       | AC                                        | BDD Scenario                              | Automated Test                                                     | Test Type        | Status  |
| ------- | -------- | ----------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------ | ---------------- | ------- |
| REQ-009 | US-009.1 | AC-009.1 — Add Member                     | Add a member to a project                 | `test_owner_can_add_project_member`                                | API              | Covered |
| REQ-009 | US-009.1 | AC-009.1 — Add Member                     | Access a project as an added member       | `test_added_member_can_access_project`                             | API / Security   | Covered |
| REQ-009 | US-009.1 | AC-009.2 — Remove Member                  | Remove a member from a project            | `test_owner_can_remove_project_member`                             | API              | Covered |
| REQ-009 | US-009.1 | AC-009.2 — Remove Member                  | Access a project after being removed      | `test_removed_member_can_no_longer_access_project`                 | API / Security   | Covered |
| REQ-009 | US-009.1 | AC-009.3 — Invalid Member                 | Attempt to add a nonexistent user         | `test_project_owner_cannot_add_user_who_does_not_have_an_account`  | API / Validation | Covered |
| REQ-009 | US-009.1 | AC-009.4 — Unauthorized Member Management | Attempt to add a member as a non-owner    | `test_user_who_is_not_project_owner_cannot_add_project_members`    | API / Security   | Covered |
| REQ-009 | US-009.1 | AC-009.4 — Unauthorized Member Management | Attempt to remove a member as a non-owner | `test_user_who_is_not_project_owner_cannot_remove_project_members` | API / Security   | Covered |
| REQ-009 | US-009.1 | AC-009.5 — Duplicate Member               | Attempt to add the same member twice      | `test_project_owner_cannot_add_same_user_more_than_once`           | API / Validation | Covered |

## BDD Specification Status

The current `.feature` files describe intended behaviour but are **not currently executable with pytest-bdd**.

They are therefore treated as behavioural specifications rather than automated tests.

Current feature files:

```text
tests/bdd/features/authentication.feature
tests/bdd/features/project_creation.feature
```

Executable BDD automation may be added later as a representative example rather than being used for the entire test suite.
