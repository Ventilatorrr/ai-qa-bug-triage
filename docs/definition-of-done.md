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
- No unresolved critical or high-severity defects remain.

## Integration and API Testing

- Relevant API functionality has been tested.
- Integration between relevant application components has been tested.
- Database interactions have been verified where applicable.
- Data validation and error handling have been tested.

## UI, Usability and Accessibility

- Relevant UI functionality has been tested.
- The interface behaves correctly across the supported browsers and screen sizes.
- Relevant usability checks have been completed.
- Relevant accessibility checks have been completed.

## Security

- Authentication and authorization behaviour has been tested where applicable.
- Users cannot access or modify data outside their authorized scope.
- Relevant input validation and security controls have been tested.
- No known critical security vulnerabilities remain unresolved.

## AI and Agent Behaviour

- AI functionality has been tested against defined expected behaviours and scenarios.
- AI-generated suggestions can be reviewed and overridden by QA analysts.
- AI failures, invalid responses, and unavailable AI services are handled appropriately.
- AI agents can access only explicitly permitted tools and data.
- Attempts to use unauthorized tools or perform unauthorized actions are prevented.
- Agents cannot access or modify data outside their authorized project or user context.
- Relevant AI actions and tool calls are logged sufficiently to support testing and investigation.

## CI/CD

- The relevant automated test suite passes in CI.
- The application can be built and run from a clean environment.
- No critical build or deployment issues remain unresolved.

## Documentation and Traceability

- Relevant documentation has been updated.
- Requirements, user stories, and acceptance criteria remain traceable to the implemented functionality and tests.
- Known limitations or unresolved lower-severity defects are documented.

## Completion

An increment is Done when all applicable DoD criteria have been satisfied.
