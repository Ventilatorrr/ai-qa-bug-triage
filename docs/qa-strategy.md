# QA Strategy

## 1. Purpose

This document defines the quality assurance approach for the **AI QA Bug Triage** application.

The goal is to ensure that the application is functional, secure, maintainable, and appropriately tested across its different application layers while keeping the testing effort proportionate to the project's scope and risks.

The strategy will evolve as new increments, requirements, technologies, and risks are introduced.

---

## 2. Relationship to Other Project Documents

The QA Strategy forms part of the project's wider documentation and should be used together with the other project documents.

| Document                | Purpose                                                                                             |
| ----------------------- | --------------------------------------------------------------------------------------------------- |
| **Product Vision**      | Defines the product vision, target users, problem, value, scope, and out-of-scope areas.            |
| **Requirements**        | Defines what the system shall do through requirements, user stories, and acceptance criteria.       |
| **QA Strategy**         | Defines how quality will be assessed and how testing will be approached.                            |
| **Definition of Done**  | Defines the criteria that must be satisfied for an increment to be considered done.                 |
| **Traceability Matrix** | Links requirements and acceptance criteria to automated tests and records test coverage and status. |

These documents should remain independently maintained. The QA Strategy should not duplicate the detailed contents of the Definition of Done or other project documents.

The QA Strategy defines the testing approach that supports the applicable requirements and contributes to satisfying the quality-related criteria in the Definition of Done.

---

## 3. Scope

The QA strategy covers the application's core functionality and quality risks, including:

* User registration and authentication
* Protected application access
* User logout
* Project creation and management
* Project membership and role-based access control
* Bug tracking and bug lifecycle management
* AI-assisted bug triage
* User interaction and usability
* Data persistence and integrity
* Security and authorization

The project is a portfolio/mock application rather than a production SaaS product. Testing will therefore focus on demonstrating sound QA practices and meaningful risk coverage rather than production-scale operational testing.

---

## 4. Testing Layers

Testing will be performed across the application's main architectural layers.

### Presentation Layer — UI

The presentation layer represents the interface users interact with directly.

Primary tool:

* Playwright

Typical coverage includes:

* Navigation
* Forms and validation feedback
* Important user workflows
* Role-based visibility of controls
* Successful and unsuccessful user interactions
* Basic accessibility and usability checks

UI tests will focus on important user journeys rather than duplicating every API test.

### Application Layer — API

The application layer contains the application's business logic, authentication, authorization, validation, and other API behaviour.

Primary tools:

* pytest
* FastAPI TestClient

Typical coverage includes:

* API functional behaviour
* Input validation
* Authentication and authorization
* Positive and negative scenarios
* Business rules
* Error handling
* Security restrictions

The API layer will generally receive substantial automated functional coverage because API tests are fast, precise, and well suited to testing business rules.

### Data Layer — Database

The data layer is responsible for persistence and data integrity.

Primary approach:

* Direct database validation using the isolated test database

Typical coverage includes:

* Data persistence
* Creation, update, and deletion behaviour
* Relationships between records
* Role and membership relationships
* Important data-integrity rules

Database testing will be applied selectively where direct verification provides meaningful additional confidence.

### Layer Coverage Principle

Not every requirement or acceptance criterion requires tests at all three layers.

For each requirement, the appropriate testing layers will be determined based on:

* Risk
* Business importance
* Where the relevant logic is implemented
* Whether additional layer coverage provides meaningful confidence
* The avoidance of unnecessary duplicate testing

As the application evolves, existing tests will periodically be reviewed to determine whether UI, API, and Database coverage is appropriate for each requirement.

---

## 5. Test Types

The project will use a combination of testing types.

### Functional Testing

Verifies that features behave according to requirements and acceptance criteria.

### Validation Testing

Verifies that invalid input is rejected correctly and that appropriate feedback is provided.

### Authorization and Security Testing

Verifies that users can only perform actions permitted by their role and project membership.

Examples include:

* Preventing non-owners from managing project members
* Preventing unauthorized project modification
* Preventing unauthorized project deletion
* Preventing unauthorized project access
* Preventing Project Owner self-removal

### Negative Testing

Tests invalid, unexpected, and unauthorized scenarios in addition to successful scenarios.

### Integration Testing

Verifies that application components work correctly together, particularly API and database interactions.

### UI Testing

Verifies important user-facing workflows through the presentation layer.

### Usability and Accessibility Testing

Basic usability and accessibility checks will be performed where practical, particularly for:

* Navigation
* Form usability
* Labels and controls
* Keyboard interaction
* Readable presentation
* Basic accessibility requirements

### AI-Specific Testing

Once AI-assisted triage is implemented, testing will also address AI-related risks such as:

* Relevance of AI suggestions
* Handling incomplete or poor-quality bug descriptions
* Unexpected or malformed input
* AI service failures and timeouts
* Clearly distinguishing AI suggestions from confirmed application data
* The ability for a QA Analyst to review, modify, accept, or reject suggestions
* Potential hallucination or unsupported recommendations
* Unauthorized AI actions
* AI access to data or tools outside its permitted scope

AI output will be treated as **assistance rather than authoritative truth**.

---

## 6. Test Automation Strategy

Automation will be used wherever it provides reliable and repeatable value.

The general approach is:

```text
API tests
    ↓
Fast and precise business-rule coverage

UI tests
    ↓
Critical end-to-end user journeys

Database tests
    ↓
Persistence and integrity verification where valuable
```

The project will avoid excessive UI automation when the same logic can be tested more efficiently at the API layer.

Focused Python Playwright automation now exercises stable, critical frontend
journeys against a dedicated server with a temporary database. Detailed validation
and permission matrices remain at the API/unit layers; broader browser coverage is tracked in
the traceability matrix.

Selected important workflows may intentionally be tested across multiple layers to demonstrate end-to-end coverage and provide additional confidence.

---

## 7. Risk-Based Testing

Testing effort will be prioritised according to risk.

Higher-priority areas include:

* Authentication
* Authorization and role-based access control
* Project and member permissions
* Data integrity
* Creation, modification, and deletion of data
* Bug lifecycle and status transitions
* AI-generated suggestions
* AI failure handling
* AI authorization and data access

Lower-risk cosmetic changes may receive lighter testing unless they affect usability, accessibility, or important user workflows.

---

## 8. Test Data and Environment

Automated tests will use an isolated test database rather than the application's normal development database.

Test fixtures will provide controlled users, projects, memberships, and other required data.

Automated tests should be:

* Repeatable
* Independent of one another
* Independent of execution order
* Safe to run repeatedly
* Based on controlled test data

Where practical, test data should be created as part of test setup rather than relying on manually prepared records.

---

## 9. Traceability

Requirements and acceptance criteria connect to stable test case IDs through the project's Traceability Matrix. User stories remain in the requirements specification.

The current matrix structure is:

| REQ | AC | TC IDs | Test Type | Overall Coverage |
| --- | -- | ------ | --------- | ---------------- |

The `Test Type` field identifies the contributing verification layers and/or purposes, for example:

* UI
* API
* Database
* API / Security
* API / Validation
* UI / Security
* API + UI
* API + Database

The RTM contains exactly one overall assessment per AC. The [test case catalogue](test-cases.md) owns stable global TC IDs, exact implementation references and parameter selectors, including technical, security and infrastructure cases without a business AC mapping. Equivalent parameter variants share an ID; distinct conceptual outcomes may share an implementation with explicit selectors.

The [execution record](test-execution.md) separates dated suite results, structured manual groups and exploratory observations. The [defect summary](defect-summary.md) indexes only verified tracker information. Four feature files contain five representative BDD scenarios, all executable through pytest-bdd and the existing Playwright fixtures (TC-386–TC-390); no specifications-only BDD scenarios remain. BDD supplements existing coverage; expanded BDD coverage remains deferred. GitHub Actions CI runs the existing offline Python, JavaScript and Playwright/BDD suites in independent jobs, which are required checks protecting `main`. See the [README](../README.md#continuous-integration) for triggers and results.

Layer coverage will be reviewed over time rather than assuming that every acceptance criterion requires UI, API, and Database tests.

---

## 10. Defect Handling

When a defect is identified, it should be:

1. Reproduced and understood.
2. Documented with sufficient information to support investigation.
3. Classified according to impact and relevance.
4. Fixed in the appropriate application layer.
5. Covered by an automated or manual regression test where appropriate.

Defects that reveal missing or unclear requirements should also lead to a review of the relevant requirements or acceptance criteria.

---

## 11. Regression Testing

Existing automated tests will be run regularly as the application evolves.

Changes to one feature should not be assumed to affect only that feature.

Regression testing will pay particular attention to shared functionality such as:

* Authentication
* Authorization
* Project membership
* Navigation
* Database relationships
* Common frontend components

As the project grows, the automated suite will provide the primary regression safety net.

---

## 12. Definition of Done

The project's **Definition of Done** is maintained in a separate document and applies to every product increment.

The QA Strategy does not duplicate the Definition of Done. Instead, it defines the testing approach that supports the applicable development, functional testing, integration/API, UI, security, AI, CI/CD, documentation, and traceability activities defined there.

An increment should only be considered complete when the applicable Definition of Done criteria have been satisfied.

---

## 13. Development and QA Workflow

Testing will be integrated throughout development rather than postponed until the end of an increment.

The preferred workflow is:

```text
Requirement
    ↓
Acceptance Criteria
    ↓
Implementation
    ↓
Automated Tests
    ↓
Frontend / UI
    ↓
UI Tests
    ↓
Layered Coverage Review
    ↓
Traceability Update
    ↓
Regression Testing
```

Where appropriate, tests will be implemented alongside or shortly after the related functionality.

---

## 14. Current Project Status

Current implementation status (15 October 2026; execution evidence is dated separately):

* Core authentication functionality has been implemented and tested.
* Project management functionality has been implemented and tested.
* Project membership and role-based authorization have been implemented and tested.
* The frontend has been developed alongside the existing API functionality.
* Automated API coverage is currently the strongest test layer.
* A focused Python Playwright E2E suite is implemented under `tests/e2e/`, with explicit collection opt-in, unique fictional data, a dedicated server with a temporary SQLite database, and deterministic mocked AI responses. README documents separate backend, frontend, and browser commands; the catalogue and execution record identify evidence and limitations.
* Increment 2 has not yet been formally reviewed and completed.
* Increment 2 APIs are implemented through REQ-017. Frontend bug creation, viewing, editing, deletion, assignment, lifecycle actions, sorting, and pagination are implemented. Maintained JavaScript tests and dated browser checks provide partial UI evidence; broader browser coverage remains outstanding.
* Increment 3 AI-assisted triage is implemented, including validated suggestions, user-controlled review, and failure handling. Automated provider integration uses mocked responses; real-model evaluation remains deferred.
* Existing API tests use fresh per-test SQLite paths under pytest temporary directories, with cached configuration rebound before application startup. Migration and subprocess tests retain separate temporary databases. Test suites remain serial.
* Historical evidence (10 September 2026): pytest passed 148 cases in 114.52 seconds after the member-removal timestamp fix. The 38 temporary frontend validation-message checks recorded then were not a maintained regression suite. These historical results are not the current suite inventory or a new execution result.
* Current maintained frontend coverage runs with `node --test tests/frontend/*.test.cjs`. Exact recorded suite results are in [test execution](test-execution.md).
* About and Bugs have theme and Logout controls. Dated isolated browser/theme checks are linked from the execution record; broader cross-browser and accessibility verification remains outstanding.
* Versioning update (8 October 2026): `APP_VERSION` in `app/version.py` is the single source reported through FastAPI metadata, `/version`, and the About page; it then reported `1.0.0-dev`. The annotated tag and published GitHub Release `v0.1.0` remain the first stable release. `0.1.0-dev` is only a retrospective development-period label, not an actual release or Git tag.
* Versioning update (24 October 2026): `APP_VERSION` is `0.2.0` for the core application release, without Try Demo or production hosting. The development line after `v0.1.0` is retrospectively `0.2.0-dev`, although the application displayed `1.0.0-dev`.
* The Semantic Versioning workflow is core release `v0.2.0` -> next development phase `1.0.0-dev` (Try Demo and deployment) -> planned first release candidate `1.0.0-rc.1` -> planned first production release `v1.0.0`. The `v0.2.0` tag and GitHub Release have not been created yet.
* Affected Version identifies the version where a defect was observed or reproduced, including an observed development build such as the `1.0.0-dev` label displayed before `0.2.0`, not necessarily where it was introduced. It is not populated automatically. Fix Version identifies the release in which the fix is included or planned to be included, which need not be published yet. Leave Affected Version blank when no appropriate observed or released version is known, and Fix Version blank when no target release is known; do not assign released versions to defects found only in unreleased feature work.

---

## 15. QA Principles

The project will follow these principles:

**Test at the appropriate layer.**
Use the lowest practical layer that provides meaningful confidence, while adding higher-layer tests where they provide distinct value.

**Test both expected and unexpected behaviour.**
Successful scenarios alone do not provide sufficient coverage.

**Treat security as a backend responsibility.**
Frontend restrictions improve usability, but authorization must be enforced by the API.

**Prefer meaningful coverage over test quantity.**
A larger number of redundant tests does not automatically provide better quality.

**Keep AI under human control.**
AI-generated information is advisory and must remain reviewable and overridable.

**Maintain traceability.**
Testing should remain connected to requirements and acceptance criteria throughout development.

**Review coverage as the system evolves.**
Testing strategy and layer coverage should be reassessed when new features, risks, technologies, or application layers are introduced.

**Keep QA proportional to risk and project scope.**
Testing effort should focus on behaviours and risks that matter most to the quality of the application.
