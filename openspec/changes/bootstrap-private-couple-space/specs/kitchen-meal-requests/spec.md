## ADDED Requirements

### Requirement: Directed kitchen meal requests
An authenticated member SHALL be able to send a meal request to the other
workspace member containing a dish name, optional quantity, optional note, and
optional desired time. The system MUST create the request in `pending` status
and identify immutable requester and recipient members.

#### Scenario: Member requests a meal from the partner
- **WHEN** a member submits a valid request addressed to the other member
- **THEN** the system stores a pending request and creates an in-app
  notification for the recipient

#### Scenario: Member requests a meal from themself or an outsider
- **WHEN** a request recipient is the requester or is not the other workspace
  member
- **THEN** the system rejects the request

### Requirement: Meal request state transitions
The system MUST permit only `pending -> accepted|declined|cancelled`,
`accepted -> preparing|cancelled`, and `preparing -> completed|cancelled`.
Only the recipient can accept, decline, begin preparing, or complete a request;
the requester can cancel a non-completed request.

#### Scenario: Recipient accepts and completes a request
- **WHEN** the recipient changes a pending request to accepted, then preparing,
  then completed
- **THEN** each valid transition is stored with its timestamp

#### Scenario: Requester attempts to mark a request completed
- **WHEN** the requester tries to complete their own meal request
- **THEN** the system denies the transition

#### Scenario: Member applies an invalid transition
- **WHEN** either member tries to move a declined or completed request to a
  different status
- **THEN** the system rejects the update and retains its existing status
