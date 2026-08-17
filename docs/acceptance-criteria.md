# Acceptance Criteria

## US-001 — Register an Account

### AC-001.1 — Successful Registration

- A new user can register using a unique email address and a valid password.
- A user account is created after successful registration.

### AC-001.2 — Duplicate Email

- Registration is rejected when the email address is already associated with an existing account.
- The user is informed that the email address is already registered.

### AC-001.3 — Invalid Email

- Registration is rejected when an invalid email address is provided.
- The user is informed that the email address is invalid.

### AC-001.4 — Invalid Password

- Registration is rejected when the password does not meet the defined password requirements.
- The user is informed of the password requirements.

### AC-001.5 — Password Security

- User passwords are not stored as plain text.

## US-002 — Log In

### AC-002.1 — Successful Login

- A registered user can log in using valid credentials.
- The user is granted access to authenticated areas of the application after successful login.

### AC-002.2 — Invalid Credentials

- Login is rejected when an incorrect email or password is provided.
- The user is informed that the credentials are invalid.

### AC-002.3 — Unregistered Account

- Login is rejected when the email address is not associated with an existing account.
- The user is informed that the credentials are invalid.

### AC-002.4 — Unauthenticated Access

- A user who is not authenticated cannot access areas of the application that require authentication.
- The user is redirected to the login page or otherwise informed that authentication is required.

## US-003 — Log Out

### AC-003.1 — Successful Logout

- An authenticated user can log out, terminating their authenticated session.
- The user is redirected to the login page or another appropriate unauthenticated page.

### AC-003.2 — Protected Access After Logout

- A user cannot access protected application areas after logging out.

## US-004 — Create a Project

### AC-004.1 — Successful Project Creation

- An authenticated user can create a project by providing a valid project name.
- The user becomes the Project Owner of the new project.

### AC-004.2 — Invalid Project Name

- Project creation is rejected when the project name is empty.
- The user is informed that a valid project name is required.

### AC-004.3 — Unauthenticated User

- An unauthenticated user cannot create a project.

## US-005 — Manage Projects

### AC-005.1 — View Projects

- A Project Owner can view projects they own.
- An authorized project member can view projects they have access to.

### AC-005.2 — Open Project

- An authorized project member can open a project they have access to.
- The project details and available functionality are displayed.

### AC-005.3 — Edit Project Name

- A Project Owner can change the name of a project they own.
- The new project name is saved and displayed after the change.

### AC-005.4 — Delete Project

- A Project Owner can delete a project they own.
- A deleted project is no longer accessible to project members.
- A confirmation is required before the project is deleted.

### AC-005.5 — Unauthorized Project Management

- A user cannot edit or delete a project they do not own.
- A user without access cannot open the project.

## US-006 — Manage Project Members

### AC-006.1 — Add Member

- A Project Owner can add an existing user to a project.
- The added user can access the project after being added.

### AC-006.2 — Remove Member

- A Project Owner can remove a member from a project.
- A removed member can no longer access the project.

### AC-006.3 — Invalid Member

- A Project Owner cannot add a user who does not have an account.

### AC-006.4 — Unauthorized Member Management

- A user who is not the Project Owner cannot add or remove project members.
