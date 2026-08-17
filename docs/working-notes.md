## Product and Requirements Decisions

### Bug Lifecycle

The current bug lifecycle is:

Triage → In Progress → Testing → Closed

If testing fails:

Testing → In Progress

Newly created bugs automatically enter Triage.

### Bug Report Fields

The planned bug report fields are:

- Title
- Description
- Steps to Reproduce
- Expected Result
- Actual Result
- Affected Version
- Severity
- Priority
- Status
- Assignee
- Fix Version

Fix Version should only become available when the bug enters Testing.

### Scope Decisions

- Comments are currently out of scope for the MVP.
- Private Testing is not used as a status.
- A separate Open status is not currently used.
- A full version/release management system is out of scope.
- The application is not intended to replicate Jira.
- The application is not intended to be a commercial SaaS product.

### Roles

Current working model:

- QA Analyst — user role
- Developer — user role
- Project Owner — project-level role

The exact permissions for each role will be defined through requirements and acceptance criteria.

### AI

AI provides suggestions rather than making final QA decisions.

Planned AI-assisted suggestions include:

- Bug classification
- Severity
- Priority
- Description
- Reproduction steps

AI-generated suggestions must be reviewed by a QA Analyst before being applied.

The AI should only have access to explicitly authorized tools and should not be able to perform unauthorized actions on system data.

### Requirements Evolution

Requirements are considered living documentation.

If a missing requirement or new feature is identified:

1. Evaluate whether it is necessary.
2. Update the requirements.
3. Define or update acceptance criteria.
4. Update BDD scenarios and tests as necessary.
5. Implement the change.

Changes should be deliberate and traceable rather than added directly to the implementation.

- Can multiple projects have the same name?
- A Project Owner cannot remove themselves.