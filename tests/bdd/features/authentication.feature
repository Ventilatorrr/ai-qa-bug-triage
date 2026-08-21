Feature: User authentication and protected access

# REQ-001 — User Registration

# AC-001.1 — Successful Registration
Scenario: Successfully register an account
Given I am on the registration page
When I register with a unique email address and a valid password
Then my user account should be created

# AC-001.2 — Duplicate Email
Scenario: Register with an already registered email address
Given I am on the registration page
And an account already exists with the email address
When I register with the same email address
Then registration should be rejected
And I should be informed that the email address is already registered

# AC-001.3 — Invalid Email
Scenario: Register with an invalid email address
Given I am on the registration page
When I register with an invalid email address
Then registration should be rejected
And I should be informed that the email address is invalid

# AC-001.4 — Invalid Password: Minimum Length
Scenario: Register with a password that is too short
Given I am on the registration page
When I register with a password containing fewer than 8 characters
Then registration should be rejected
And I should be informed that the password must contain at least 8 characters

# AC-001.5 — Invalid Password: Uppercase Required
Scenario: Register with a password without an uppercase letter
Given I am on the registration page
When I register with a password that does not contain an uppercase letter
Then registration should be rejected
And I should be informed that an uppercase letter is required

# AC-001.6 — Invalid Password: Lowercase Required
Scenario: Register with a password without a lowercase letter
Given I am on the registration page
When I register with a password that does not contain a lowercase letter
Then registration should be rejected
And I should be informed that a lowercase letter is required

# AC-001.7 — Invalid Password: Number Required

Scenario: Register with a password without a number
Given I am on the registration page
When I register with a password that does not contain a number
Then registration should be rejected
And I should be informed that a number is required

# AC-001.8 — Password Security
# Covered by a regular security/database test rather than BDD.

# REQ-002 — User Login

# AC-002.1 — Successful Login
Scenario: Successfully log in
Given I have a registered account
And I am on the login page
When I log in with valid credentials
Then I should receive an access token

# AC-002.2 — Invalid Credentials
Scenario: Log in with invalid credentials
Given I am on the login page
When I log in with invalid credentials
Then login should be rejected
And I should be informed that the credentials are invalid

# REQ-003 — Protected Access

# AC-003.1 — Authenticated Access
Scenario: Authenticated user accesses a protected area
Given I am an authenticated user
When I access a protected area of the application
Then I should be allowed to access it

# AC-003.2 — Unauthenticated Access
Scenario: Unauthenticated user accesses a protected area
Given I am not authenticated
When I attempt to access a protected area of the application
Then I should be prevented from accessing it
And I should be redirected to the login page

# AC-003.3 — Invalid Authentication
Scenario: User accesses a protected area with invalid authentication
Given I have an invalid authentication token
When I access a protected area of the application
Then I should be prevented from accessing it
And I should receive a 401 Unauthorized response

# REQ-004 — User Logout

# AC-004.1 — Successful Logout
Scenario: Successfully log out
Given I am logged in
When I log out
Then my authentication token should be removed from the browser
And I should be redirected to the login page

# AC-004.2 — Protected Access After Logout
Scenario: Attempt to access a protected area after logging out
Given I am logged in
And I have logged out
When I attempt to access a protected area of the application
Then I should be prevented from accessing it
And I should be redirected to the login page
