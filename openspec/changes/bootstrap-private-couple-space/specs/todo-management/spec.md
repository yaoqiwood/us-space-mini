## ADDED Requirements

### Requirement: Personal and shared Todo creation
An authenticated member SHALL be able to create a Todo with a title, optional
description and due time, and visibility of `personal` or `shared`. Personal
Todos MUST be owned by their creator; shared Todos MAY be assigned to either
member.

#### Scenario: Member creates a personal Todo
- **WHEN** a member submits a valid personal Todo
- **THEN** the system stores it as owned by that member and does not show it to
  the partner

#### Scenario: Member creates a shared Todo for the partner
- **WHEN** a member submits a valid shared Todo assigned to the partner
- **THEN** the system stores it in the workspace and shows it to both members

#### Scenario: Member assigns a Todo outside the workspace
- **WHEN** a Todo request names an assignee who is not an active workspace
  member
- **THEN** the system rejects the request

### Requirement: Todo lifecycle and visibility
The system MUST support `open`, `completed`, and `cancelled` Todo states and
MUST record the actor and timestamp when a Todo is completed. Members SHALL see
shared Todos and their own personal Todos only.

#### Scenario: Member completes an open shared Todo
- **WHEN** either member marks an open shared Todo as completed
- **THEN** the Todo status becomes `completed` with the completing member and
  completion time recorded

#### Scenario: Member attempts to change the partner's personal Todo
- **WHEN** a member updates or completes a personal Todo owned by the partner
- **THEN** the system denies the mutation
