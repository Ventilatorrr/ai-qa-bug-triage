Feature: Project creation

# REQ-005 — Project Creation

# AC-005.1 — Successful Project Creation
Scenario: Successfully create a project
Given I am an authenticated user
When I create a project with a valid project name
Then the project should be created
And I should become the Project Owner of the project

# AC-005.2 — Invalid Project Name
Scenario: Create a project with an empty name
Given I am an authenticated user
When I create a project without providing a project name
Then project creation should be rejected
And I should be informed that a valid project name is required

# AC-005.3 — Unauthenticated User
Scenario: Unauthenticated user attempts to create a project
Given I am not authenticated
When I attempt to create a project with a valid project name
Then project creation should be rejected
