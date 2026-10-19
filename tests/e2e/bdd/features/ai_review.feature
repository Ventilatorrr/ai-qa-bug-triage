Feature: Review AI suggestions before saving a bug report

  # TC-390 | AC-018.1, AC-018.2, AC-020.1, AC-020.2, AC-020.3, AC-020.7
  Scenario: Review and apply AI suggestions
    Given a QA Analyst is editing a Triage bug report with deterministic AI suggestions available
    When the QA Analyst requests AI assistance
    Then the suggestions are available for review without changing the report
    When the QA Analyst uses the Title suggestion and dismisses the Description suggestion
    Then only the accepted suggestion changes the form and the report remains unsaved
    When the QA Analyst saves the bug report
    Then the saved report contains the accepted title and the original description
