Feature: Project members manage a bug report through its lifecycle

  # TC-389 | AC-011.1, AC-017.2, AC-017.3, AC-017.4, AC-017.5
  Scenario: QA Analyst manages a bug lifecycle
    Given a QA Analyst has access to a project with a Developer
    When the QA Analyst creates a valid bug report
    Then the new bug report is in Triage
    When the QA Analyst assigns the bug to the Developer and moves it to Open
    And the Developer moves the bug through Development and hands it to the QA Analyst for Testing
    And the QA Analyst passes testing
    Then the bug report is Closed with resolution Fixed
    And the lifecycle result is persisted correctly
