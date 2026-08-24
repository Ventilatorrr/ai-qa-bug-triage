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

#### US-005.1 — Create a Project

As an authenticated user, I want to create a project so that I can manage bugs within it.

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
