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

* A new user can register using a unique email address and a valid password.
* A user account is created after successful registration.

#### AC-001.2 — Duplicate Email

* Registration is rejected when the email address is already associated with an existing account.
* The user receives a `409 Conflict` response.
* The user is informed that the email address is already registered.

#### AC-001.3 — Invalid Email

* Registration is rejected when an invalid email address is provided.
* The user receives a `422 Unprocessable Content` response.
* The user is informed that the email address is invalid.

#### AC-001.4 — Invalid Password

* Registration is rejected when the password does not meet the required password policy.
* The password must contain at least 8 characters.
* The password must contain at least one uppercase letter.
* The password must contain at least one lowercase letter.
* The password must contain at least one number.
* The user receives a `422 Unprocessable Content` response.
* The user is informed which password requirement has not been met.

#### AC-001.5 — Password Security

* User passwords are not stored as plain text.
* User passwords are stored using a secure password hash.

---

### REQ-002 — User Login

The system shall allow registered users to log in using valid account credentials.

#### US-002.1 — Log In

As a registered user, I want to log in so that I can access the system.

#### AC-002.1 — Successful Login

* A registered user can log in using valid credentials.
* The user receives an access token after a successful login.
* The user is redirected to the Projects page after a successful login.

#### AC-002.2 — Invalid Credentials

* Login is rejected when an incorrect email or password is provided.
* The user is informed that the credentials are invalid.

---

### REQ-003 — Protected Access

The system shall restrict protected application functionality to authenticated users.

#### US-003.1 — Access Protected Areas

As an authenticated user, I want to access protected areas of the application so that I can use functionality available to my account.

#### AC-003.1 — Authenticated Access

* An authenticated user can access areas of the application that require authentication.

#### AC-003.2 — Unauthenticated Access

* An unauthenticated user cannot access areas of the application that require authentication.
* The user is redirected to the login page.

#### AC-003.3 — Invalid Authentication

* A request containing an invalid or expired authentication token cannot access a protected area.
* The user receives a `401 Unauthorized` response.

---

### REQ-004 — User Logout

The system shall allow authenticated users to log out of their account.

#### US-004.1 — Log Out

As an authenticated user, I want to log out so that I can end my session securely.

#### AC-004.1 — Successful Logout

* An authenticated user can log out of their account.
* The user's authentication token is removed from the browser.
* The user is redirected to the login page.

#### AC-004.2 — Protected Access After Logout

* After logging out, the browser no longer sends the user's authentication token with protected requests.
* A user cannot access protected application areas after logging out.
* The user is redirected to the login page when attempting to access a protected application area after logging out.

---

### REQ-005 — Project Creation

The system shall allow authenticated users to create a project.

#### AC-005.1 — Successful Project Creation

* An authenticated user can create a project by providing a valid project name.

#### AC-005.1 — Successful Project Creation

* An authenticated user can create a project by providing a valid project name.
* The user becomes the Project Owner of the new project.

#### AC-005.2 — Invalid Project Name

* Project creation is rejected when the project name is empty.
* The user is informed that a valid project name is required.

#### AC-005.3 — Unauthenticated User

* An unauthenticated user cannot create a project.

---

### REQ-006 — Project Access

The system shall allow authenticated users to view projects they are authorized to access and prevent unauthorized access to projects.

#### US-006.1 — Access Projects

As an authenticated user, I want to access projects I am authorized to access so that I can work with the projects available to me.

#### AC-006.1 — View Project List

* The system returns the projects available to the authenticated user.

#### AC-006.2 — Project List Authorization

* The project list does not include projects the authenticated user is not authorized to access.

#### AC-006.3 — Open Project

* The system returns the details of a requested project when the authenticated user is authorized to access it.

#### AC-006.4 — Unauthorized Project Access

* The system denies access to a requested project when the authenticated user is not authorized to access it.

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

* A Project Owner can delete a project they own.
* A confirmation is required before the project is deleted.
* A deleted project is no longer accessible.

#### AC-008.2 — Unauthorized Project Deletion

* A user cannot delete a project they do not own.

---

## REQ-009 — Project Member Management

The system shall allow a Project Owner to add and remove project members and allow project members to view project membership information.

### US-009 — Manage Project Members

As a Project Owner, I want to add and remove project members so that I can control who has access to the project.

#### AC-009.1 — Add Member

* A Project Owner can add an existing user to a project.
* The added user can access the project after being added.

#### AC-009.2 — Remove Member

* A Project Owner can remove a member from a project.
* A removed member can no longer access the project.

#### AC-009.3 — Invalid Member

* A Project Owner cannot add a user who does not have an account.
* The system rejects the request when the specified user does not exist.

#### AC-009.4 — Duplicate Member

* A Project Owner cannot add the same user to a project more than once.
* The system rejects an attempt to add a user who is already a member of the project.

#### AC-009.5 — View Project Members

* A project member can view the members of a project they have access to.
* The project member list displays each member's email address and project role.
* Project members are displayed in the following order: Project Owner, QA Analyst, Developer.
* Members within the same role are displayed alphabetically by email address.

---

## REQ-010 — Project Roles and Permissions

The system shall support role-based access control for project members. A project member's assigned project role shall determine the actions they are authorized to perform within the project.

### US-010 — Use Project Roles and Permissions

As a project user, I want my project role to determine what I can do within a project so that project functionality is controlled according to my responsibilities.

#### AC-010.1 — Project Owner Role

* The system supports the `Project Owner` project role.
* The user who creates a project is assigned the `Project Owner` role.

#### AC-010.2 — QA Analyst Role

* The system supports the `QA Analyst` project role.
* A QA Analyst can access projects they are a member of.

#### AC-010.3 — Developer Role

* The system supports the `Developer` project role.
* A Developer can access projects they are a member of.

#### AC-010.4 — Unauthorized Project Member Management

* A user who is not the Project Owner cannot add project members.
* A user who is not the Project Owner cannot remove project members.

#### AC-010.5 — Unauthorized Project Actions

* A user who is not the Project Owner cannot edit the project name.
* A user who is not the Project Owner cannot delete the project.

---

## Increment 2 — Bug Management

### REQ-011 — Bug Creation

The system shall allow authorized project members to create a bug report within a project.

### US-011 — Create a Bug Report

As an authorized project member, I want to create a bug report with the information available to me so that I can record a software defect for further triage.

### Acceptance Criteria

#### AC-011.1 — Successful Bug Creation

* An authorized project member can create a bug report within a project they have access to.
* A bug report can be created by providing a title.
* The title is required when creating a bug report.
* A newly created bug report has the status `Triage`.
* The system records the project and user who created the bug report.
* The system records the bug's creation date and time.
* The system records the bug's Last Updated date and time.
* The newly created bug report can be viewed within the project.

#### AC-011.2 — Missing Bug Title

* Bug creation is rejected when no title is provided.
* The user is informed that a bug title is required.

#### AC-011.3 — Unauthorized Bug Creation

* A user who is not a member of the project cannot create a bug report within that project.
* The system denies the request.

#### AC-011.4 — Optional Bug Information

* Description, Steps to Reproduce, Expected Result, Actual Result, Affected Version, Severity, Priority, Assignee, and Fix Version are optional when creating a bug report.
* Optional bug information can be provided when the bug is created or added or updated later.

---

### REQ-012 — Bug Access

The system shall allow authorized project members to view and open bug reports within projects they have access to.

### US-012 — Access Bug Reports

As an authorized project member, I want to view and open bug reports in projects I have access to so that I can review project defects.

### Acceptance Criteria

#### AC-012.1 — View Bug List

* An authorized project member can view the bug reports within a project they have access to.
* The bug list displays the Bug ID, Title, Status, and Last Updated date for each bug report.
* Severity, Priority, and Assignee are displayed where available.

#### AC-012.2 — Open Bug Report

* An authorized project member can open a bug report within a project they have access to.
* The bug report details are displayed, including all available bug information.

#### AC-012.3 — Unauthorized Bug Access

* A user who is not a member of the project cannot view or open its bug reports.
* The system denies unauthorized access to the bug reports.

#### AC-012.4 — Sort Bug Reports

* An authorized project member can sort the bug list by all columns.
* The default bug list order is most recently updated first.
* Severity is ordered from highest to lowest impact: Blocker, Major, Minor.
* Priority is ordered from highest to lowest: High, Medium, Low.
* Missing optional values are displayed last when sorting.

---

### REQ-013 — Bug Editing

The system shall allow authorized project members to update bug report information for bugs within projects they have access to.

### US-013 — Edit Bug Reports

As an authorized project member, I want to edit bug report information so that I can keep defect information accurate and up to date.

### Acceptance Criteria

#### AC-013.1 — Edit Bug Report

* An authorized project member can edit a bug report within a project they have access to.
* A project member can add or update available bug information.
* Updated bug information is saved and displayed after the change.
* Editing a bug updates its Last Updated date and time.

#### AC-013.2 — Optional Bug Information

* A project member can add or update Description, Steps to Reproduce, Expected Result, Actual Result, Affected Version, Severity, Priority, and Fix Version after the bug has been created.

#### AC-013.3 — Unauthorized Bug Editing

* A user who is not a member of the project cannot edit a bug report within that project.
* The system rejects an unauthorized modification of the bug report.

---

### REQ-014 — Bug Deletion

The system shall allow a Project Owner or QA Analyst to delete bug reports within projects they have access to.

### US-014 — Delete Bug Reports

As a Project Owner or QA Analyst, I want to delete bug reports so that obsolete or invalid reports can be removed from the project.

### Acceptance Criteria

#### AC-014.1 — Successful Bug Deletion

* A Project Owner or QA Analyst can delete a bug report within a project they have access to.
* A confirmation is required before the bug report is deleted.
* A deleted bug report is no longer accessible.

#### AC-014.2 — Unauthorized Bug Deletion

* A Developer cannot delete a bug report.
* A user who is not a member of the project cannot delete a bug report.
* The system rejects an unauthorized attempt to delete a bug report.

---

### REQ-015 — Bug Assignment

The system shall allow a Project Owner or QA Analyst to assign a bug report to a QA Analyst or Developer who is a member of the project.

### US-015 — Assign Bugs

As a Project Owner or QA Analyst, I want to assign bugs to QA Analysts or Developers so that responsibility for investigating or fixing defects is clear.

### Acceptance Criteria

#### AC-015.1 — Successful Bug Assignment

* A Project Owner or QA Analyst can assign a bug report to a QA Analyst or Developer who is a member of the project.
* The assigned user is displayed on the bug report.

#### AC-015.2 — Invalid Assignment

* A bug cannot be assigned to a Project Owner.
* A bug cannot be assigned to a QA Analyst or Developer who is not a member of the project.

#### AC-015.3 — Unauthorized Bug Assignment

* A Developer cannot assign a bug report.
* A user who is not a member of the project cannot assign a bug report.
* The system rejects an unauthorized attempt to assign a bug report.

#### AC-015.4 — Change Bug Assignee

* A Project Owner or QA Analyst can change the assignee of an existing bug report.
* A bug can be reassigned to another QA Analyst or Developer who is a member of the project.
* A bug can be unassigned.
* Changing the assignee updates the bug's Last Updated date and time.

---

### REQ-016 — Bug Classification

The system shall allow authorized project members to set and update a bug report's severity and priority.

### US-016 — Classify Bugs

As an authorized project member, I want to set and update a bug's severity and priority so that defects can be assessed consistently and addressed appropriately.

### Acceptance Criteria

#### AC-016.1 — Set Bug Severity

* An authorized project member can set the severity of a bug report.
* The supported severity values are `Blocker`, `Major`, and `Minor`.
* The selected severity is saved and displayed on the bug report.

#### AC-016.2 — Set Bug Priority

* An authorized project member can set the priority of a bug report.
* The supported priority values are `High`, `Medium`, and `Low`.
* The selected priority is saved and displayed on the bug report.

#### AC-016.3 — Update Bug Classification

- An authorized project member can update the severity and priority of an existing bug report.
- Updated severity and priority values are saved and displayed on the bug report.
- Changing the severity or priority updates the bug's Last Updated date and time.

#### AC-016.4 — Unauthorized Bug Classification

* A user who is not a member of the project cannot set or update the severity or priority of a bug report.
* The system rejects an unauthorized attempt to modify bug classification.

---

## Increment 2 — Bug Management

### REQ-011 — Bug Creation

The system shall allow authorized project members to create a bug report within a project.

### US-011 — Create a Bug Report

As an authorized project member, I want to create a bug report with the information available to me so that I can record a software defect for further triage.

### Acceptance Criteriai

#### AC-011.1 — Successful Bug Creation

* An authorized project member can create a bug report within a project they have access to.
* A bug report can be created by providing a title.
* The title is required when creating a bug report.
* A newly created bug report has the status `Triage`.
* The system records the project and user who created the bug report.
* The system records the bug's creation date and time.
* The system records the bug's Last Updated date and time.
* The newly created bug report can be viewed within the project.

#### AC-011.2 — Missing Bug Title

* Bug creation is rejected when no title is provided.
* The user is informed that a bug title is required.

#### AC-011.3 — Unauthorized Bug Creation

* A user who is not a member of the project cannot create a bug report within that project.
* The system rejects the request.

#### AC-011.4 — Optional Bug Information

* Description, Steps to Reproduce, Expected Result, Actual Result, Affected Version, Severity, Priority, Assignee, and Fix Version are optional when creating a bug report.
* Optional bug information can be provided when the bug is created or added or updated later.

---

### REQ-012 — Bug Access

The system shall allow authorized project members to view and open bug reports within projects they have access to.

### US-012 — Access Bug Reports

As an authorized project member, I want to view and open bug reports in projects I have access to so that I can review project defects.

### Acceptance Criteria

#### AC-012.1 — View Bug List

* An authorized project member can view the bug reports within a project they have access to.
* The bug list displays the Bug ID, Title, Status, and Last Updated date for each bug report.
* Severity, Priority, and Assignee are displayed where available.

#### AC-012.2 — Open Bug Report

* An authorized project member can open a bug report within a project they have access to.
* The bug report details are displayed, including all available bug information.

#### AC-012.3 — Unauthorized Bug Access

* A user who is not a member of the project cannot view or open its bug reports.
* The system denies unauthorized access to the bug reports.

#### AC-012.4 — Sort Bug Reports

* An authorized project member can sort the bug list by all columns.
* The default bug list order is most recently updated first.
* Severity is ordered from highest to lowest impact: Blocker, Major, Minor.
* Priority is ordered from highest to lowest: High, Medium, Low.
* Missing optional values are displayed last when sorting.

---

### REQ-013 — Bug Editing

The system shall allow authorized project members to update bug report information for bugs within projects they have access to.

### US-013 — Edit Bug Reports

As an authorized project member, I want to edit bug report information so that I can keep defect information accurate and up to date.

### Acceptance Criteria

#### AC-013.1 — Edit Bug Report

* An authorized project member can edit a bug report within a project they have access to.
* A project member can add or update available bug information.
* Updated bug information is saved and displayed after the change.
* Editing a bug updates its Last Updated date and time.

#### AC-013.2 — Optional Bug Information

* A project member can add or update Title, Description, Steps to Reproduce, Expected Result, Actual Result, Affected Version, Severity, Priority, and Fix Version after the bug has been created.

#### AC-013.3 — Unauthorized Bug Editing

* A user who is not a member of the project cannot edit a bug report within that project.
* The system rejects an unauthorized modification of the bug report.

---

### REQ-014 — Bug Deletion

The system shall allow a Project Owner or QA Analyst to delete bug reports within projects they have access to.

### US-014 — Delete Bug Reports

As a Project Owner or QA Analyst, I want to delete bug reports so that obsolete or invalid reports can be removed from the project.

### Acceptance Criteria

#### AC-014.1 — Successful Bug Deletion

* A Project Owner or QA Analyst can delete a bug report within a project they have access to.
* A confirmation is required before the bug report is deleted.
* A deleted bug report is no longer accessible.

#### AC-014.2 — Unauthorized Bug Deletion

* A Developer cannot delete a bug report.
* A user who is not a member of the project cannot delete a bug report.
* The system rejects an unauthorized attempt to delete a bug report.

---

### REQ-015 — Bug Assignment

The system shall allow a Project Owner or QA Analyst to assign a bug report to a QA Analyst or Developer who is a member of the project.

### US-015 — Assign Bugs

As a Project Owner or QA Analyst, I want to assign bugs to QA Analysts or Developers so that responsibility for investigating or fixing defects is clear.

### Acceptance Criteria

#### AC-015.1 — Successful Bug Assignment

* A Project Owner or QA Analyst can assign a bug report to a QA Analyst or Developer who is a member of the project.
* The assigned user is displayed on the bug report.
* Assigning a bug updates the bug's Last Updated date and time.

#### AC-015.2 — Invalid Assignment

* A bug cannot be assigned to a Project Owner.
* A bug cannot be assigned to a QA Analyst or Developer who is not a member of the project.

#### AC-015.3 — Unauthorized Bug Assignment

* A Developer cannot assign a bug report.
* A user who is not a member of the project cannot assign a bug report.
* The system rejects an unauthorized attempt to assign a bug report.

#### AC-015.4 — Change Bug Assignee

* A Project Owner or QA Analyst can change the assignee of an existing bug report.
* A bug can be reassigned to another QA Analyst or Developer who is a member of the project.
* A bug can be unassigned.
* Assigning, reassigning, or unassigning a bug updates the bug's Last Updated date and time.

---

### REQ-016 — Bug Classification

The system shall allow authorized project members to set and update a bug report's severity and priority.

### US-016 — Classify Bugs

As an authorized project member, I want to set and update a bug's severity and priority so that defects can be assessed consistently and addressed appropriately.

### Acceptance Criteria

#### AC-016.1 — Set Bug Severity

* An authorized project member can set the severity of a bug report.
* The supported severity values are `Blocker`, `Major`, and `Minor`.
* The selected severity is saved and displayed on the bug report.

#### AC-016.2 — Set Bug Priority

* An authorized project member can set the priority of a bug report.
* The supported priority values are `High`, `Medium`, and `Low`.
* The selected priority is saved and displayed on the bug report.

#### AC-016.3 — Update Bug Classification

* An authorized project member can update the severity and priority of an existing bug report.
* Updated severity and priority values are saved and displayed on the bug report.
* Changing the severity or priority updates the bug's Last Updated date and time.

#### AC-016.4 — Unauthorized Bug Classification

* A user who is not a member of the project cannot set or update the severity or priority of a bug report.
* The system rejects an unauthorized attempt to modify bug classification.

---

## Increment 2 — Bug Management

### REQ-011 — Bug Creation

The system shall allow authorized project members to create a bug report within a project.

### US-011 — Create a Bug Report

As an authorized project member, I want to create a bug report with the information available to me so that I can record a software defect for further triage.

### Acceptance Criteria

#### AC-011.1 — Successful Bug Creation

* An authorized project member can create a bug report within a project they have access to.
* A bug report can be created by providing a title.
* The title is required when creating a bug report.
* A newly created bug report has the status `Triage`.
* The system records the project and user who created the bug report.
* The system records the bug's creation date and time.
* The system records the bug's Last Updated date and time.
* The newly created bug report can be viewed within the project.

#### AC-011.2 — Missing Bug Title

* Bug creation is rejected when no title is provided.
* The user is informed that a bug title is required.

#### AC-011.3 — Unauthorized Bug Creation

* A user who is not a member of the project cannot create a bug report within that project.
* The system rejects the request.

#### AC-011.4 — Optional Bug Information

* Description, Steps to Reproduce, Expected Result, Actual Result, Affected Version, Severity, Priority, Assignee, and Fix Version are optional when creating a bug report.
* Optional bug information can be provided when the bug is created or added or updated later.

---

### REQ-012 — Bug Access

The system shall allow authorized project members to view and open bug reports within projects they have access to.

### US-012 — Access Bug Reports

As an authorized project member, I want to view and open bug reports in projects I have access to so that I can review project defects.

### Acceptance Criteria

#### AC-012.1 — View Bug List

* An authorized project member can view the bug reports within a project they have access to.
* The bug list displays the Bug ID, Title, Status, and Last Updated date for each bug report.
* Severity, Priority, and Assignee are displayed where available.

#### AC-012.2 — Open Bug Report

* An authorized project member can open a bug report within a project they have access to.
* The bug report details are displayed, including all available bug information.

#### AC-012.3 — Unauthorized Bug Access

* A user who is not a member of the project cannot view or open its bug reports.
* The system denies unauthorized access to the bug reports.

#### AC-012.4 — Sort Bug Reports

* An authorized project member can sort the bug list by all columns.
* The default bug list order is most recently updated first.
* Severity is ordered from highest to lowest impact: Blocker, Major, Minor.
* Priority is ordered from highest to lowest: High, Medium, Low.
* Missing optional values are displayed last when sorting.

---

### REQ-013 — Bug Editing

The system shall allow authorized project members to update bug report information for bugs within projects they have access to.

### US-013 — Edit Bug Reports

As an authorized project member, I want to edit bug report information so that I can keep defect information accurate and up to date.

### Acceptance Criteria

#### AC-013.1 — Edit Bug Report

* An authorized project member can edit a bug report within a project they have access to.
* A project member can add or update available bug information.
* Updated bug information is saved and displayed after the change.
* Editing a bug updates its Last Updated date and time.

#### AC-013.2 — Optional Bug Information

* A project member can add or update Title, Description, Steps to Reproduce, Expected Result, Actual Result, Affected Version, Severity, Priority, and Fix Version after the bug has been created.

#### AC-013.3 — Unauthorized Bug Editing

* A user who is not a member of the project cannot edit a bug report within that project.
* The system rejects an unauthorized modification of the bug report.

---

### REQ-014 — Bug Deletion

The system shall allow a Project Owner or QA Analyst to delete bug reports within projects they have access to.

### US-014 — Delete Bug Reports

As a Project Owner or QA Analyst, I want to delete bug reports so that obsolete or invalid reports can be removed from the project.

### Acceptance Criteria

#### AC-014.1 — Successful Bug Deletion

* A Project Owner or QA Analyst can delete a bug report within a project they have access to.
* A confirmation is required before the bug report is deleted.
* A deleted bug report is no longer accessible.

#### AC-014.2 — Unauthorized Bug Deletion

* A Developer cannot delete a bug report.
* A user who is not a member of the project cannot delete a bug report.
* The system rejects an unauthorized attempt to delete a bug report.

---

### REQ-015 — Bug Assignment

The system shall allow a Project Owner or QA Analyst to assign, reassign, or unassign a bug report to or from a QA Analyst or Developer who is a member of the project.

### US-015 — Assign Bugs

As a Project Owner or QA Analyst, I want to assign, reassign, or unassign bugs to QA Analysts or Developers so that responsibility for investigating or fixing defects is clear.

### Acceptance Criteria

#### AC-015.1 — Assign and Unassign Bugs

* A Project Owner or QA Analyst can assign a bug report to a QA Analyst or Developer who is a member of the project.
* The assigned user is displayed on the bug report.
* A bug report can have only one assignee at a time.
* A bug report can be unassigned.
* Assigning or unassigning a bug updates the bug's Last Updated date and time.

#### AC-015.2 — Invalid Assignment

* A bug cannot be assigned to a Project Owner.
* A bug cannot be assigned to a QA Analyst or Developer who is not a member of the project.

#### AC-015.3 — Unauthorized Bug Assignment

* A Developer cannot assign a bug report.
* A user who is not a member of the project cannot assign a bug report.
* The system rejects an unauthorized attempt to assign a bug report.

#### AC-015.4 — Change Bug Assignee

* A Project Owner or QA Analyst can change the assignee of an existing bug report.
* A bug can be reassigned to another QA Analyst or Developer who is a member of the project.
* Reassigning a bug updates the bug's Last Updated date and time.

---

### REQ-016 — Bug Classification

The system shall allow authorized project members to set and update a bug report's severity and priority.

### US-016 — Classify Bugs

As an authorized project member, I want to set and update a bug's severity and priority so that defects can be assessed consistently and addressed appropriately.

### Acceptance Criteria

#### AC-016.1 — Set Bug Severity

* An authorized project member can set the severity of a bug report.
* The supported severity values are `Blocker`, `Major`, and `Minor`.
* The selected severity is saved and displayed on the bug report.

#### AC-016.2 — Set Bug Priority

* An authorized project member can set the priority of a bug report.
* The supported priority values are `High`, `Medium`, and `Low`.
* The selected priority is saved and displayed on the bug report.

#### AC-016.3 — Update Bug Classification

* An authorized project member can update the severity and priority of an existing bug report.
* Updated severity and priority values are saved and displayed on the bug report.
* Changing the severity or priority updates the bug's Last Updated date and time.

#### AC-016.4 — Unauthorized Bug Classification

* A user who is not a member of the project cannot set or update the severity or priority of a bug report.
* The system rejects an unauthorized attempt to modify bug classification.

---

### REQ-017 — Bug Lifecycle

The system shall manage bug reports through the defined bug lifecycle.

### US-017 — Manage Bug Status

As a QA Analyst or Developer, I want bugs to progress through a defined lifecycle so that their current state and next responsibility are clear.

### Acceptance Criteria

#### AC-017.1 — Bug Status

* A bug report has one of the following statuses: `Triage`, `Open`, `Development`, `Testing`, or `Closed`.
* A newly created bug report has the status `Triage`.

#### AC-017.2 — Triage to Open

* A Project Owner or QA Analyst can move a bug from `Triage` to `Open`.
* A bug can be moved to `Open` only after it has been reviewed by a Project Owner or QA Analyst.
* A bug in `Open` status can be unassigned or assigned to a QA Analyst or Developer.

#### AC-017.3 — Open to Development

* A Project Owner or QA Analyst can move a bug from `Open` to `Development`.
* A Developer must be assigned to the bug before it can be moved to `Development`.

#### AC-017.4 — Development to Testing

* A Developer can move a bug from `Development` to `Testing` when the fix is ready for verification.
* A QA Analyst must be assigned to the bug before it can be moved to `Testing`.

#### AC-017.5 — Testing Outcome

* A QA Analyst can mark testing as `Passed` or `Failed`.
* When testing is `Passed`, the bug status changes to `Closed`.
* When testing is `Failed`, the bug status changes to `Development`.
* When testing is `Failed`, a Developer must be assigned to the bug before it can continue in `Development`.

#### AC-017.6 — Closed Bugs

* A bug in `Closed` status cannot be moved to another status through the normal bug workflow.

#### AC-017.7 — Invalid Status Transitions

* A bug cannot transition between statuses in a way that is not permitted by the defined bug lifecycle.
* The system rejects an invalid status transition.

#### AC-017.8 — Status Update Timestamp

* Changing the bug status updates the bug's Last Updated date and time.

---

