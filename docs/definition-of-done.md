# Definition of Done

The Definition of Done (DoD) applies to every product increment. An increment is considered done only when all applicable criteria below have been satisfied.

## Development

- All functionality defined by the applicable requirements and acceptance criteria has been implemented.
- Code follows the project's agreed coding standards and practices.
- Code changes are reviewed before being merged into the main branch.
- Changes are committed to version control.

## Functional Testing

- All acceptance criteria have been verified.
- Relevant automated tests have been implemented or updated.
- Relevant regression tests have been executed successfully.
- No unresolved Major or Blocker defects remain.

## Integration and API Testing

- Relevant API functionality has been tested.
- Integration between relevant application components has been tested.
- Database interactions have been verified where applicable.
- Data validation and error handling have been tested.

## UI, Usability and Accessibility

- Relevant UI functionality has been tested.
- The interface behaves correctly in the browsers and screen sizes within the tested scope; untested browsers or devices are recorded with the evidence.
- Relevant usability checks have been completed.
- Relevant accessibility checks have been completed.

## Security

- Authentication and authorization behaviour has been tested where applicable.
- Users cannot access or modify data outside their authorized scope.
- Relevant input validation and security controls have been tested.
- No known critical security vulnerabilities remain unresolved.

## AI-Assisted Behaviour

- AI functionality has been tested against defined expected behaviours and scenarios.
- AI suggestions can be reviewed, edited, used or dismissed by authorized users before anything is saved.
- AI failures, invalid responses, and unavailable AI services are handled appropriately.
- AI context is limited to data from the user's authorized project, and AI requests carry no application-managed secrets.
- AI output cannot perform actions or modify stored data; only the user's normal Create or Save action persists values.
- AI usage is bounded, and AI failures are logged without request content or credentials.

## CI/CD

- The relevant automated test suite passes in CI.
- The application can be built and run from a clean environment.
- No critical build or deployment issues remain unresolved.

## Documentation and Traceability

- Relevant documentation has been updated.
- Requirements, user stories, and acceptance criteria remain traceable to the implemented functionality and tests.
- Known limitations or unresolved lower-severity defects are documented.
