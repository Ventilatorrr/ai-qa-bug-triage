Feature: Project management

  # TC-387 | AC-005.1
  Scenario: Successfully create a project
    Given I am an authenticated user
    When I create a project with a valid project name
    Then the project should be created
    And I should become the Project Owner of the project

  # TC-388 | AC-007.2, AC-008.2, AC-010.5
  Scenario: Non-owner cannot modify a project
    Given a QA Analyst is a non-owner member of an existing project
    When the QA Analyst attempts to rename or delete the project
    Then project modification is forbidden
    And the project's existing data remains unchanged
