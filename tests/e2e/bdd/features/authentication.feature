Feature: User registration

  # TC-386 | AC-001.1
  Scenario: Successfully register an account
    Given I am on the registration page
    When I register with a unique email address and a valid password
    Then my user account should be created
