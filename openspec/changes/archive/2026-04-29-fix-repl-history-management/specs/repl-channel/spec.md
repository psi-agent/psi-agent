## REMOVED Requirements

### Requirement: REPL maintains conversation history

**Reason**: Session is the single source of truth for conversation history. Channel should only handle input/output, not state management.

**Migration**: History is now managed exclusively by session. Channel sends only the current user message.

#### Scenario: Add user message to history
- **WHEN** user sends a message
- **THEN** REPL SHALL add the message to conversation history

#### Scenario: Add assistant message to history
- **WHEN** session returns a response
- **THEN** REPL SHALL add the response to conversation history

#### Scenario: Send history with request
- **WHEN** REPL sends a new message to session
- **THEN** REPL SHALL include all previous messages in the request

## ADDED Requirements

### Requirement: REPL sends only current message to session

The REPL SHALL send only the current user message to session, not the entire conversation history.

#### Scenario: Send single message
- **WHEN** user enters a message
- **THEN** REPL SHALL send only that message to session

#### Scenario: Message format
- **WHEN** REPL sends a message to session
- **THEN** the request body SHALL contain a messages array with a single user message

### Requirement: REPL displays session response

The REPL SHALL display the response from session without storing it locally.

#### Scenario: Display response
- **WHEN** session returns a response
- **THEN** REPL SHALL display the response content to stdout

#### Scenario: No local history storage
- **WHEN** REPL receives a response
- **THEN** REPL SHALL NOT store the response in a local history variable
