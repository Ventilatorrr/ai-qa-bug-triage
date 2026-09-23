# Requirements

## Requirement Structure

Each requirement may include a User Story and one or more Acceptance Criteria.

- **REQ** — Requirement: a high-level statement of what the system shall do.
- **US** — User Story: a user-focused statement describing who wants a capability, what they want, and why.
- **AC** — Acceptance Criterion: a specific, testable condition that must be satisfied for the requirement to be accepted.

---

## Increment 1 — User & Project Management

### REQ-001 — User Registration

The system shall allow a new user to register an account using a unique email address and password.

#### US-001.1 — Register an Account

As a new user, I want to register an account so that I can access the system.

#### AC-001.1 — Successful Registration

- A new user can register using a unique email address and a valid password.
- A user account is created after successful registration.

#### AC-001.2 — Duplicate Email

- Registration is rejected when the email address is already associated with an existing account.
- The user receives a `409 Conflict` response.
- The user is informed that the email address is already registered.

#### AC-001.3 — Invalid Email

- Registration is rejected when an invalid email address is provided.
- The user receives a `422 Unprocessable Content` response.
- The user is informed that the email address is invalid.

#### AC-001.4 — Invalid Password

- Registration is rejected when the password does not meet the required password policy.
- The password must contain at least 8 characters.
- The password must contain at least one uppercase letter.
- The password must contain at least one lowercase letter.
- The password must contain at least one number.
- The user receives a `422 Unprocessable Content` response.
- The user is informed which password requirement has not been met.

#### AC-001.5 — Password Security

- User passwords are not stored as plain text.
- User passwords are stored using a secure password hash.

---

### REQ-002 — User Login

The system shall allow registered users to log in using valid account credentials.

#### US-002.1 — Log In

As a registered user, I want to log in so that I can access the system.

#### AC-002.1 — Successful Login

- A registered user can log in using valid credentials.
- The user receives an access token after a successful login.
- The user is redirected to the Projects page after a successful login.

#### AC-002.2 — Invalid Credentials

- Login is rejected when an incorrect email or password is provided.
- The user is informed that the credentials are invalid.

---

### REQ-003 — Protected Access

The system shall restrict protected application functionality to authenticated users.

#### US-003.1 — Access Protected Areas

As an authenticated user, I want to access protected areas of the application so that I can use functionality available to my account.

#### AC-003.1 — Authenticated Access

- An authenticated user can access areas of the application that require authentication.

#### AC-003.2 — Unauthenticated Access

- An unauthenticated user cannot access areas of the application that require authentication.
- The user is redirected to the login page.

#### AC-003.3 — Invalid Authentication

- A request containing an invalid or expired authentication token cannot access a protected area.
- The user receives a `401 Unauthorized` response.

---

### REQ-004 — User Logout

The system shall allow authenticated users to log out of their account.

#### US-004.1 — Log Out

As an authenticated user, I want to log out so that I can end my session securely.

#### AC-004.1 — Successful Logout

- An authenticated user can log out of their account.
- The user's authentication token is removed from the browser.
- The user is redirected to the login page.

#### AC-004.2 — Protected Access After Logout

- After logging out, the browser no longer sends the user's authentication token with protected requests.
- A user cannot access protected application areas after logging out.
- The user is redirected to the login page when attempting to access a protected application area after logging out.

---

### REQ-005 — Project Creation

The system shall allow authenticated users to create a project.

#### AC-005.1 — Successful Project Creation

- An authenticated user can create a project by providing a valid project name.
- The user becomes the Project Owner of the new project.

#### AC-005.2 — Invalid Project Name

- Project creation is rejected when the project name is empty or contains only whitespace.
- The user is informed that a valid project name is required.

#### AC-005.3 — Unauthenticated User

- An unauthenticated user cannot create a project.

---

### REQ-006 — Project Access

The system shall allow authenticated users to view projects they are authorized to access and prevent unauthorized access to projects.

#### US-006.1 — Access Projects

As an authenticated user, I want to access projects I am authorized to access so that I can work with the projects available to me.

#### AC-006.1 — View Project List

- The system returns the projects available to the authenticated user.

#### AC-006.2 — Project List Authorization

- The project list does not include projects the authenticated user is not authorized to access.

#### AC-006.3 — Open Project

- The system returns the details of a requested project when the authenticated user is authorized to access it.

#### AC-006.4 — Unauthorized Project Access

- The system denies access to a requested project when the authenticated user is not authorized to access it.

---

### REQ-007 — Project Name Editing

The system shall allow a Project Owner to change the project's name.

### US-007 — Edit a Project Name

As a Project Owner, I want to change a project's name so that I can keep project information accurate.

#### AC-007.1 — Successful Project Name Editing

- A Project Owner can change the name of a project they own.
- The new project name is saved and displayed after the change.

#### AC-007.2 — Unauthorized Project Name Editing

- A user cannot edit a project they do not own.

---

### REQ-008 — Project Deletion

The system shall allow a Project Owner to delete a project.

### US-008 — Delete a Project

As a Project Owner, I want to delete a project so that I can remove projects that are no longer needed.

#### AC-008.1 — Successful Project Deletion

- A Project Owner can delete a project they own.
- A confirmation is required before the project is deleted.
- A deleted project is no longer accessible.

#### AC-008.2 — Unauthorized Project Deletion

- A user cannot delete a project they do not own.

---

## REQ-009 — Project Member Management

The system shall allow a Project Owner to add and remove project members and allow project members to view project membership information.

### US-009 — Manage Project Members

As a Project Owner, I want to add and remove project members so that I can control who has access to the project.

#### AC-009.1 — Add Member

- A Project Owner can add an existing user to a project.
- The added user can access the project after being added.

#### AC-009.2 — Remove Member

- A Project Owner can remove a member from a project.
- A removed member can no longer access the project.
- Bugs assigned to a removed member within the project become unassigned.
- Automatically unassigned bugs retain their existing status and all other bug fields except Last Updated.
- Automatically unassigned bugs have their Last Updated timestamp updated.
- Removing a member does not affect bug assignments in other projects.

#### AC-009.3 — Invalid Member

- A Project Owner cannot add a user who does not have an account.
- The system rejects the request when the specified user does not exist.

#### AC-009.4 — Duplicate Member

- A Project Owner cannot add the same user to a project more than once.
- The system rejects an attempt to add a user who is already a member of the project.

#### AC-009.5 — View Project Members

- A project member can view the members of a project they have access to.
- The project member list displays each member's email address and project role.
- Project members are displayed in the following order: Project Owner, QA Analyst, Developer.
- Members within the same role are displayed alphabetically by email address.

---

## REQ-010 — Project Roles and Permissions

The system shall support role-based access control for project members. A project member's assigned project role shall determine the actions they are authorized to perform within the project.

### US-010 — Use Project Roles and Permissions

As a project user, I want my project role to determine what I can do within a project so that project functionality is controlled according to my responsibilities.

#### AC-010.1 — Project Owner Role

- The system supports the `Project Owner` project role.
- The user who creates a project is assigned the `Project Owner` role.

#### AC-010.2 — QA Analyst Role

- The system supports the `QA Analyst` project role.
- A QA Analyst can access projects they are a member of.

#### AC-010.3 — Developer Role

- The system supports the `Developer` project role.
- A Developer can access projects they are a member of.

#### AC-010.4 — Unauthorized Project Member Management

- A user who is not the Project Owner cannot add project members.
- A user who is not the Project Owner cannot remove project members.

#### AC-010.5 — Unauthorized Project Actions

- A user who is not the Project Owner cannot edit the project name.
- A user who is not the Project Owner cannot delete the project.

---

## Increment 2 — Bug Management

### REQ-011 — Bug Creation

The system shall allow authorized project members to create a bug report within a project.

### US-011 — Create a Bug Report

As an authorized project member, I want to create a bug report with the information available to me so that I can record a software defect for further triage.

### Acceptance Criteria

#### AC-011.1 — Successful Bug Creation

- An authorized project member can create a bug report within a project they have access to.
- A bug report can be created by providing a title.
- The title is required when creating a bug report.
- A newly created bug report has the status `Triage`.
- The system records the project and user who created the bug report.
- The system records the bug's creation date and time.
- The system records the bug's Last Updated date and time.
- The newly created bug report can be viewed within the project.

#### AC-011.2 — Missing Bug Title

- Bug creation is rejected when no title is provided.
- The user is informed that a bug title is required.

#### AC-011.3 — Unauthorized Bug Creation

- A user who is not a member of the project cannot create a bug report within that project.
- The system rejects the request.

#### AC-011.4 — Optional Bug Information

- Description, Environment, Steps to Reproduce, Expected Result, Actual Result, Affected Version, Severity, Priority, Assignee, and Fix Version are optional when creating a bug report.
- Environment is free-text information describing the context in which the bug occurred, such as operating system, browser and version, device type, or relevant user/account context.
- Affected Version identifies the application version in which the bug was observed or reproduced. It does not necessarily identify the version in which the defect was first introduced.
- Optional bug information can be provided when the bug is created or added or updated later.

---

### REQ-012 — Bug Access

The system shall allow authorized project members to view and open bug reports within projects they have access to.

### US-012 — Access Bug Reports

As an authorized project member, I want to view and open bug reports in projects I have access to so that I can review project defects.

### Acceptance Criteria

#### AC-012.1 — View Bug List

- An authorized project member can view the bug reports within a project they have access to.
- The bug list displays the Bug ID, Title, Status, and Last Updated date for each bug report.
- Severity, Priority, and Assignee are displayed where available.

#### AC-012.2 — Open Bug Report

- An authorized project member can open a bug report within a project they have access to.
- The bug report details are displayed, including all available bug information.

#### AC-012.3 — Unauthorized Bug Access

- A user who is not a member of the project cannot view or open its bug reports.
- The system denies unauthorized access to the bug reports.

#### AC-012.4 — Sort Bug Reports

- An authorized project member can sort the bug list by all columns.
- The default bug list order is most recently updated first.
- Selecting a different column starts ascending; selecting the active column toggles direction. The active column and direction are indicated.
- Bug ID sorts numerically, Title and the displayed Assignee value sort alphabetically without case sensitivity, and Last Updated sorts chronologically.
- Severity is ordered from highest to lowest impact: Blocker, Major, Moderate, Minor.
- Priority is ordered from highest to lowest urgency: Urgent, High, Medium, Low.
- Ascending Severity and Priority use low-to-high rank; descending uses high-to-low rank.
- Ascending Status follows Triage, Open, Development, Testing, Closed; descending reverses that order.
- Missing optional values, including Unassigned, are displayed last in both directions.
- Sorting preserves displayed data and bug links without updating bug records. The active sort is retained when the list refreshes on the current page.

---

### REQ-013 — Bug Editing

The system shall allow authorized project members to update bug report information for bugs within projects they have access to.

### US-013 — Edit Bug Reports

As an authorized project member, I want to edit bug report information so that I can keep defect information accurate and up to date.

### Acceptance Criteria

#### AC-013.1 — Edit Bug Report

- An authorized project member can edit a bug report within a project they have access to.
- A project member can add or update available bug information.
- Updated bug information is saved and displayed after the change.
- Editing a bug updates its Last Updated date and time.

#### AC-013.2 — Optional Bug Information

- A project member can add or update Title, Description, Environment, Steps to Reproduce, Expected Result, Actual Result, Affected Version, Severity, Priority, and Fix Version after the bug has been created.

#### AC-013.3 — Unauthorized Bug Editing

- A user who is not a member of the project cannot edit a bug report within that project.
- The system rejects an unauthorized modification of the bug report.

---

### REQ-014 — Bug Deletion

The system shall allow a Project Owner or QA Analyst to delete bug reports within projects they have access to.

### US-014 — Delete Bug Reports

As a Project Owner or QA Analyst, I want to delete bug reports so that obsolete or invalid reports can be removed from the project.

### Acceptance Criteria

#### AC-014.1 — Successful Bug Deletion

- A Project Owner or QA Analyst can delete a bug report within a project they have access to.
- A confirmation is required before the bug report is deleted.
- A deleted bug report is no longer accessible.

#### AC-014.2 — Unauthorized Bug Deletion

- A Developer cannot delete a bug report.
- A user who is not a member of the project cannot delete a bug report.
- The system rejects an unauthorized attempt to delete a bug report.

---

### REQ-015 — Bug Assignment

The system shall allow a Project Owner, QA Analyst, or Developer to assign, reassign, or unassign a bug report to or from a QA Analyst or Developer who is a member of the project.

### US-015 — Assign Bugs

As a project member, I want to assign, reassign, or unassign bugs to QA Analysts or Developers so that responsibility for investigating or fixing defects is clear.

### Acceptance Criteria

#### AC-015.1 — Assign and Unassign Bugs

- A Project Owner, QA Analyst, or Developer can assign a bug report to a QA Analyst or Developer who is a member of the project.
- The assigned user is displayed on the bug report.
- A bug report can have only one assignee at a time.
- A bug report can be unassigned when permitted by the bug lifecycle.
- Automatic unassignment on member removal follows AC-009.2, including preserving the current status; normal assignment and lifecycle-transition restrictions still apply to subsequent requests.
- Assigning or unassigning a bug updates the bug's Last Updated date and time.

#### AC-015.2 — Invalid Assignment

- A bug cannot be assigned to a Project Owner.
- A bug cannot be assigned to a QA Analyst or Developer who is not a member of the project.

#### AC-015.3 — Unauthorized Bug Assignment

- A user who is not a member of the project cannot assign, reassign, or unassign a bug report.
- The system rejects an unauthorized attempt to modify the bug assignee.

#### AC-015.4 — Change Bug Assignee

- A Project Owner, QA Analyst, or Developer can change the assignee of an existing bug report.
- A bug can be reassigned to another QA Analyst or Developer who is a member of the project.
- Reassigning a bug updates the bug's Last Updated date and time.

---

### REQ-016 — Bug Classification

The system shall allow authorized project members to set and update a bug report's severity and priority.

### US-016 — Classify Bugs

As an authorized project member, I want to set and update a bug's severity and priority so that defects can be assessed consistently and addressed appropriately.

### Acceptance Criteria

#### AC-016.1 — Set Bug Severity

- An authorized project member can set the severity of a bug report.
- The supported severity values are `Blocker`, `Major`, `Moderate`, and `Minor`.
- `Blocker`: Core functionality is unusable or meaningful use is prevented. No reasonable workaround exists.
- `Major`: Significant functionality is broken or the defect has substantial user/data impact. A workaround may exist, but the impact is significant.
- `Moderate`: Noticeable functional defect with limited impact or a reasonable/easy workaround. The affected functionality still remains usable.
- `Minor`: Cosmetic issue or low-impact functional defect. Normal use is only slightly affected.
- The selected severity is saved and displayed on the bug report.

#### AC-016.2 — Set Bug Priority

- An authorized project member can set the priority of a bug report.
- The supported priority values are `Urgent`, `High`, `Medium`, and `Low`.
- `Urgent` indicates that the bug requires immediate attention.
- `High` indicates that the bug should be addressed very soon.
- `Medium` indicates normal planned priority.
- `Low` indicates that the bug can reasonably wait.
- The selected priority is saved and displayed on the bug report.

#### AC-016.3 — Update Bug Classification

- An authorized project member can update the severity and priority of an existing bug report.
- Updated severity and priority values are saved and displayed on the bug report.
- Changing the severity or priority updates the bug's Last Updated date and time.

#### AC-016.4 — Unauthorized Bug Classification

- A user who is not a member of the project cannot set or update the severity or priority of a bug report.
- The system rejects an unauthorized attempt to modify bug classification.

---

### REQ-017 — Bug Lifecycle

The system shall manage bug reports through the defined bug lifecycle and record the resolution when a bug is closed.

### US-017 — Manage Bug Status

As a project member with the appropriate permissions, I want bugs to progress through a defined lifecycle so that their current state and next responsibility are clear.

### Acceptance Criteria

#### AC-017.1 — Bug Status

- A bug report has one of the following statuses: `Triage`, `Open`, `Development`, `Testing`, or `Closed`.
- A newly created bug report has the status `Triage`.
- A Project Owner can perform lifecycle actions available to a QA Analyst or Developer, while the same assignee and transition requirements still apply.

#### AC-017.2 — Triage to Open

- A Project Owner or QA Analyst can move a bug from `Triage` to `Open`.
- A bug must have a QA Analyst or Developer assigned to enter `Open`. Subsequent member removal may leave it unassigned under AC-009.2 without changing its status.

#### AC-017.3 — Open to Development

- An assigned Developer or Project Owner can move a bug from `Open` to `Development`.
- A Developer must be assigned to the bug before it can be moved to `Development`.

#### AC-017.4 — Development to Testing

- An assigned Developer or Project Owner can move a bug from `Development` to `Testing` when the fix is ready for verification.
- A QA Analyst who is a member of the project must be selected as part of the transition to `Testing`.
- The selected QA Analyst becomes the assignee of the bug.

#### AC-017.5 — Testing Outcome

- An assigned QA Analyst or Project Owner can select `Passed` or `Failed` as the testing outcome.
- When testing is `Passed`, the bug status changes to `Closed` and the resolution is automatically set to `Fixed`.
- When testing is `Failed`, the bug status changes to `Development`.
- When testing is `Failed`, a Developer who is a member of the project must be assigned to the bug.
- The assigned Developer becomes the bug's assignee when testing fails.

#### AC-017.6 — Close Without Fixing

- An assigned Developer or Project Owner can close a bug from `Development` without sending it through `Testing`.
- When a bug is closed without being fixed, a resolution must be selected.
- Supported non-fix resolutions are `Won't Fix`, `Duplicate`, `Cannot Reproduce`, and `Not a Bug`.
- The `Fixed` resolution is assigned only when testing is `Passed`.

#### AC-017.7 — Closed Bugs

- A bug in `Closed` status has no normal forward lifecycle transition.
- A Project Owner can move a `Closed` bug back to `Triage` to correct or reconsider its closure.
- Moving a bug from `Closed` to `Triage` clears its resolution and preserves its existing assignee.
- No other project role can move a bug out of `Closed`.
- A `Closed` bug cannot transition directly to `Open`, `Development`, or `Testing`.
- After returning to `Triage`, the normal lifecycle and assignment requirements apply again.

#### AC-017.8 — Invalid Status Transitions

- A bug cannot transition between statuses in a way that is not permitted by the defined bug lifecycle.
- The system rejects an invalid status transition.

#### AC-017.9 — Status Update Timestamp

- Changing the bug status updates the bug's Last Updated date and time.

---

## Increment 3 — AI-Assisted Bug Triage

### REQ-018 — Request AI-Assisted Triage

The system shall allow an authorized Project Owner or QA Analyst to request AI-assisted triage while creating a new bug or while editing an existing bug whose current status is `Triage`.

### US-018 — Request AI Triage

As a Project Owner or QA Analyst, I want to request AI suggestions while creating or editing a bug so that I can improve the bug report before saving it.

### Acceptance Criteria

#### AC-018.1 — Access AI Triage

- A Project Owner or QA Analyst who is a member of the project can request AI-assisted triage while creating a new bug in that project.
- A Project Owner or QA Analyst who is a member of the bug's project can request AI-assisted triage while editing an existing bug whose current status is `Triage`.
- Developers cannot request or use AI-assisted triage.
- For an existing bug, the authorized user does not need to be the bug's creator or assignee.
- AI-assisted triage is not available while editing an existing bug whose current status is outside `Triage`.
- Eligibility is based on the bug's current status. If a previously closed bug is reopened and returned to `Triage`, AI-assisted triage becomes available again.

#### AC-018.2 — Explicit Request

- Opening New Bug or entering Edit Bug does not automatically request AI suggestions.
- The user explicitly requests AI suggestions using the `AI Assist` control.
- While an AI request is in progress, the interface shows a loading state.
- Repeated activation while an AI request is already in progress does not start another simultaneous request from the same form.

#### AC-018.3 — Use Current Form Information

- When AI assistance is requested from New Bug, the request uses the information currently entered in the New Bug form.
- When AI assistance is requested from Edit Bug, the request uses the information currently present in the Edit Bug form, including unsaved changes made before the request.
- `AI Assist` can be requested from New Bug even if no bug fields have been entered; a blank Title does not block the request. The AI may return suggestions only where the available form or permitted project context provides a reasonable basis, as defined in AC-019.2.

#### AC-018.4 — Request Outcome

- A completed AI request results in validated suggestions or a notice that no usable suggestions are available; a failed request produces a clear error.

---

### REQ-019 — Validated AI Suggestions

The system shall provide structured and validated AI suggestions for eligible bug fields using the information in the current bug form and permitted context from the same project.

### US-019 — Receive Usable AI Suggestions

As a Project Owner or QA Analyst, I want AI suggestions that match the application's bug fields and relevant project context so that I can efficiently improve a bug report while remaining in control of the final values.

### Acceptance Criteria

#### AC-019.1 — Supported Suggestion Fields

- AI-assisted triage can provide suggestions for the following bug fields:
  - Title
  - Affected Version
  - Environment
  - Description
  - Steps to Reproduce
  - Expected Result
  - Actual Result
  - Severity
  - Priority
  - Assignee
- AI-assisted triage does not provide suggestions for Fix Version, Status, Resolution, Created, or Updated.
- AI suggestions do not introduce additional bug fields or classification schemes that do not exist in the application.

#### AC-019.2 — Use Bug and Project Context

- The current New Bug or Edit Bug form information is the primary context for suggestions.
- The system may also provide relevant information from existing bugs in the same project to support useful suggestions such as recurring Environment, Affected Version, or Assignee values.
- Existing user-entered values may be improved, normalized, summarized, expanded, or restructured where appropriate.
- Historical project information may support a suggestion but does not make that suggestion authoritative or verified for the current bug.
- Where neither the current form nor permitted same-project context provides a reasonable basis for a factual suggestion, no suggestion is required for that field; missing facts must not be fabricated merely to fill it.

#### AC-019.3 — Validate Suggested Values

- Each AI suggestion is validated against the requirements for its corresponding bug field before being presented to the user.
- Each supported field has at most one usable suggestion in a suggestion set.
- Suggested Severity must use one of the Severity values supported by the application.
- Suggested Priority must use one of the Priority values supported by the application.
- A suggested Assignee must identify a current member of the relevant project who can be assigned under the existing assignment rules.
- Suggested Title, Environment, Description, Steps to Reproduce, Expected Result, Actual Result, and Affected Version must be text values.
- A suggested Title must contain non-whitespace text; an empty or whitespace-only Title is treated as no valid suggestion.
- Ambiguous or conflicting suggestions for the same field are excluded for that field.
- Unsupported fields, invalid values, and suggestions that cannot be mapped unambiguously to an existing bug field are not offered to the user.

#### AC-019.4 — Partial and Empty Suggestions

- A valid AI response may contain suggestions for only a subset of the supported fields.
- A missing, null, empty, or whitespace-only suggested value is treated as no suggestion for that field and does not clear an existing form value.
- An invalid suggestion for one field does not prevent otherwise valid suggestions from being presented.
- A response that cannot be interpreted as structured field suggestions is treated as an error.
- If a structurally valid response has no valid suggestions after validation, the user is informed that no usable suggestions are available.

---

### REQ-020 — Review and Use AI Suggestions

The system shall allow an authorized Project Owner or QA Analyst to review AI suggestions and choose which suggestions to use in the current New Bug or Edit Bug form before creating or saving the bug.

### US-020 — Control AI Suggestions

As a Project Owner or QA Analyst, I want to review and selectively use AI suggestions so that I remain in control of the values that are ultimately saved in the bug report.

### Acceptance Criteria

#### AC-020.1 — Review Suggestions

- Each validated AI suggestion is clearly associated with its corresponding bug field and the value currently present in that form field.
- Suggestions are presented in the same relative order as their corresponding fields in the New Bug or Edit Bug form.
- Viewing a suggestion does not change the corresponding form value.
- Each pending suggestion provides `Use` and `Dismiss` actions.
- `Use All` and `Dismiss All` are available when one or more pending suggestions remain.

#### AC-020.2 — Use an Individual Suggestion

- Choosing `Use` copies the suggested value into the corresponding form field.
- If the form field already contains a value, choosing `Use` replaces that value in the form with the suggested value.
- After a suggestion is used, the user can further edit the resulting form value using the normal New Bug or Edit Bug controls.
- The used suggestion is no longer pending.

#### AC-020.3 — Dismiss an Individual Suggestion

- Choosing `Dismiss` removes the suggestion from the pending review without changing the corresponding form field.
- A dismissed suggestion is excluded from subsequent `Use All` actions in the same AI suggestion set.

#### AC-020.4 — Use All Pending Suggestions

- `Use All` copies the values of all remaining pending suggestions into their corresponding form fields.
- Existing form values for those fields are replaced by the suggested values.
- Suggestions previously dismissed or already used individually are not reapplied.
- After `Use All`, no suggestions from the current suggestion set remain pending.
- After `Use All`, the user can further edit any resulting form value before choosing `Create` or `Save`.

#### AC-020.5 — Dismiss All Pending Suggestions

- `Dismiss All` removes all remaining pending suggestions without changing their corresponding form fields.
- Values already copied into form fields through previous `Use` actions remain in the form and are not reverted.

#### AC-020.6 — Repeat AI Assist Requests

- A new `AI Assist` request can be made after all suggestions from the current suggestion set have been used or dismissed.
- A new request may provide suggestions for any supported field, including a field that was suggested, used, or dismissed in an earlier request.
- A new suggestion for a previously suggested field is not required to differ from an earlier suggestion when the available context does not support a different result.
- A new `AI Assist` request does not replace unresolved suggestions from the current suggestion set.

#### AC-020.7 — Persist Changes Through Existing Form Actions

- In New Bug, AI-assisted values become authoritative bug data only when the user successfully chooses `Create`.
- In Edit Bug, AI-assisted values become authoritative bug data only when the user successfully chooses `Save`.
- Choosing `Cancel`, leaving the form without saving, or reloading the page does not persist unsaved AI-assisted values.
- AI-assisted values are subject to the same validation rules as manually entered values when the bug is created or saved.

#### AC-020.8 — Pending Suggestion Lifetime

- Pending AI suggestions exist only within the current New Bug or Edit Bug form session.
- Pending suggestions are discarded when the form is cancelled, left, or reloaded.
- Results or errors from an AI request associated with a form session that has been cancelled, left, or reloaded do not populate a later form session.
- A response from an earlier AI request does not replace the results of a later request.

---

### REQ-021 — Identify AI Suggestions

The system shall clearly identify AI-generated suggestions while they are pending review.

### US-021 — Distinguish AI Suggestions

As a Project Owner or QA Analyst, I want AI-generated suggestions to be clearly identified so that I can distinguish them from the values currently entered in the bug form.

### Acceptance Criteria

#### AC-021.1 — Identify Pending AI Suggestions

- Pending AI suggestions are displayed in a clearly labelled `AI Suggestions` area.
- Suggested values remain separate from the corresponding editable form fields until the user chooses `Use` or `Use All`.

---

### REQ-022 — AI Authorization and Data Protection

The system shall enforce AI-specific authorization and protect project and application data when AI-assisted triage is used.

### US-022 — Use AI Assistance Within Authorized Boundaries

As a project member, I want AI-assisted triage to respect existing project permissions and data boundaries so that AI requests cannot expose unrelated information or directly modify application data.

### Acceptance Criteria

#### AC-022.1 — Enforce AI Authorization

- AI-assisted triage authorization follows the role, project-membership, and eligibility rules defined in REQ-018.
- Authorization is enforced by the backend and does not rely only on hiding or disabling frontend controls.
- The backend checks the user's current authorization and, for Edit Bug, the bug's current status when each `AI Assist` request is made; an unauthorized or ineligible request is rejected before the AI service is invoked.

#### AC-022.2 — Restrict AI Context

- AI context may include the current New Bug or Edit Bug form information and permitted information from the same project.
- Information from bugs belonging to another project must not be included in the AI context.
- When project-member information is provided to support an Assignee suggestion, only members of the relevant project are included.
- Content supplied to the AI model must not include authentication tokens, user credentials, AI service credentials, or other application secrets.

#### AC-022.3 — Limit AI Capabilities

- The AI service can return suggestions but cannot directly perform application actions or modify application data.
- Instructions contained in bug content or AI output cannot grant additional permissions or trigger application actions.
- AI output is treated as untrusted application data and is validated before being presented as a usable suggestion, as defined in REQ-019.
- AI-generated text must not execute scripts, markup, commands, or other executable content.

---

### REQ-023 — AI Failure Handling

The system shall handle AI service failures without changing the user's bug form data or preventing normal bug management.

### US-023 — Continue Working When AI Assistance Fails

As a Project Owner or QA Analyst, I want to continue creating or editing a bug when AI assistance fails so that AI availability does not block my work.

### Acceptance Criteria

#### AC-023.1 — Handle AI Request Failure

- If the AI service is unavailable, the request fails, or the request times out, the loading state ends and the user is shown a clear error.
- A failed AI request does not change, clear, or overwrite any value currently entered in the New Bug or Edit Bug form.
- A failed AI request does not create, save, or otherwise modify a bug.

#### AC-023.2 — Continue Without AI

- After a failed request or an outcome with no usable suggestions, the user can continue creating or editing the bug manually.
- After either outcome, the user can explicitly retry `AI Assist`.

---
