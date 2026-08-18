Feature: User authentication

  Scenario: Successful user registration
    Given I am on the registration page
    When I register with a unique email address and a valid password
    Then my user account should be created

  Scenario: Registration with an already registered email
    Given I am on the registration page
    And an account already exists with the email address
    When I register with the same email address
    Then registration should be rejected
    And I should be informed that the email address is already registered

  Scenario: Registration with an invalid email
    Given I am on the registration page
    When I register with an invalid email address
    Then registration should be rejected
    And I should be informed that the email address is invalid

  Scenario: Registration with an invalid password
    Given I am on the registration page
    When I register with a password that does not meet the password requirements
    Then registration should be rejected
    And I should be informed of the password requirements

  Scenario: Successful login
    Given I have a registered account
    And I am on the login page
    When I log in with valid credentials
    Then I should have access to authenticated areas of the application

  Scenario: Login with invalid credentials
    Given I am on the login page
    When I log in with invalid credentials
    Then login should be rejected
    And I should be informed that the credentials are invalid

  Scenario: Unauthenticated user attempts to access a protected area
    Given I am not authenticated
    When I attempt to access a protected area of the application
    Then I should be prevented from accessing it
    And I should be redirected to the login page

  Scenario: Successful logout
    Given I am logged in
    When I log out
    Then my authenticated session should be terminated
    And I should be redirected to the login page
