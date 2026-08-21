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

| REQ     | US       | AC                                              | BDD Scenario                                         | Automated Test                                                  | Test Type           | Status  |
| ------- | -------- | ----------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------- | ------------------- | ------- |
| REQ-001 | US-001.1 | AC-001.1 — Successful Registration              | Successfully register an account                     | `test_successful_registration`                                  | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.2 — Duplicate Email                      | Register with an already registered email address    | `test_registration_with_duplicate_email`                        | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.3 — Invalid Email                        | Register with an invalid email address               | `test_registration_with_invalid_email`                          | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.4 — Invalid Password: Minimum Length     | Register with a password that is too short           | `test_registration_with_short_password`                         | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.5 — Invalid Password: Uppercase Required | Register with a password without an uppercase letter | `test_registration_without_uppercase_password`                  | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.6 — Invalid Password: Lowercase Required | Register with a password without a lowercase letter  | `test_registration_without_lowercase_password`                  | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.7 — Invalid Password: Number Required    | Register with a password without a number            | `test_registration_without_number_password`                     | API                 | Covered |
| REQ-001 | US-001.1 | AC-001.8 — Password Security                    | —                                                    | `test_password_is_not_stored_as_plain_text`                     | Security / Database | Covered |
| —       | —        | —                                               | —                                                    | `test_registration_rejects_invalid_password_for_existing_email` | API / Validation    | Covered |

### REQ-002 — User Login

| REQ     | US       | AC                             | BDD Scenario                    | Automated Test                       | Test Type | Status  |
| ------- | -------- | ------------------------------ | ------------------------------- | ------------------------------------ | --------- | ------- |
| REQ-002 | US-002.1 | AC-002.1 — Successful Login    | Successfully log in             | `test_successful_login`              | API       | Covered |
| REQ-002 | US-002.1 | AC-002.2 — Invalid Credentials | Log in with invalid credentials | `test_login_with_incorrect_password` | API       | Covered |
| REQ-002 | US-002.1 | AC-002.2 — Invalid Credentials | Log in with invalid credentials | `test_login_with_unknown_email`      | API       | Covered |

### REQ-003 — Protected Access

| REQ     | US       | AC                                | BDD Scenario                                               | Automated Test                                               | Test Type      | Status  |
| ------- | -------- | --------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------ | -------------- | ------- |
| REQ-003 | US-003.1 | AC-003.1 — Authenticated Access   | Authenticated user accesses a protected area               | `test_authenticated_user_can_access_protected_endpoint`      | API            | Covered |
| REQ-003 | US-003.1 | AC-003.2 — Unauthenticated Access | Unauthenticated user accesses a protected area             | `test_unauthenticated_user_cannot_access_protected_endpoint` | API / Security | Partial |
| REQ-003 | US-003.1 | AC-003.3 — Invalid Authentication | User accesses a protected area with invalid authentication | `test_invalid_token_cannot_access_protected_endpoint`        | API / Security | Covered |

**Coverage note:** `test_unauthenticated_user_cannot_access_protected_endpoint` verifies that unauthenticated access is rejected, but the current test does not verify the required redirect to the login page.

### REQ-004 — User Logout

| REQ     | US       | AC                                       | BDD Scenario                                         | Automated Test | Test Type | Status  |
| ------- | -------- | ---------------------------------------- | ---------------------------------------------------- | -------------- | --------- | ------- |
| REQ-004 | US-004.1 | AC-004.1 — Successful Logout             | Successfully log out                                 | —              | —         | Pending |
| REQ-004 | US-004.1 | AC-004.2 — Protected Access After Logout | Attempt to access a protected area after logging out | —              | —         | Pending |

**Coverage note:** Logout has not yet been implemented.

### REQ-005 — Project Creation

| REQ     | US       | AC                                     | BDD Scenario                                      | Automated Test        | Test Type | Status  |
| ------- | -------- | -------------------------------------- | ------------------------------------------------- | --------------------- | --------- | ------- |
| REQ-005 | US-005.1 | AC-005.1 — Successful Project Creation | Successfully create a project                     | `test_create_project` | API       | Covered |
| REQ-005 | US-005.1 | AC-005.2 — Invalid Project Name        | Create a project with an empty name               | —                     | —         | Pending |
| REQ-005 | US-005.1 | AC-005.3 — Unauthenticated User        | Unauthenticated user attempts to create a project | —                     | —         | Pending |

---

## Existing Automated Tests Not Yet Mapped to the Current Requirements

The following tests already exist but belong to functionality that has not yet been formally documented in the current requirements.

| REQ | US | AC | BDD Scenario | Automated Test                                  | Test Type      | Status          |
| --- | -- | -- | ------------ | ----------------------------------------------- | -------------- | --------------- |
| —   | —  | —  | —            | `test_get_projects`                             | API            | Pending Mapping |
| —   | —  | —  | —            | `test_user_only_sees_own_projects`              | API / Security | Pending Mapping |
| —   | —  | —  | —            | `test_get_project`                              | API            | Pending Mapping |
| —   | —  | —  | —            | `test_user_cannot_access_another_users_project` | API / Security | Pending Mapping |

These tests cover Project Access behaviour that will be mapped to **REQ-006 — Project Access** once that requirement, its User Story, and its Acceptance Criteria are formally defined.

---

## BDD Specification Status

The current `.feature` files describe intended behaviour but are **not currently executable with pytest-bdd**.

They are therefore treated as behavioural specifications rather than automated tests.

Current feature files:

```text
tests/bdd/features/authentication.feature
tests/bdd/features/project_creation.feature
```

Executable BDD automation may be added later as a representative example rather than being used for the entire test suite.
