## ADDED Requirements

### Requirement: Single private couple workspace
The system SHALL maintain one active workspace containing exactly two active
members and SHALL associate all product records with that workspace.

#### Scenario: Approved second member is provisioned
- **WHEN** the second approved account is added to the active workspace
- **THEN** the workspace contains both members and can host shared records

#### Scenario: A third member is provisioned in production
- **WHEN** an attempt is made to add a third active member to the workspace
- **THEN** the system rejects the attempt without changing membership

### Requirement: Couple-scoped data authorization
Every protected resource query and mutation MUST be scoped to the authenticated
member's workspace. Personal records MUST additionally be scoped to their
owner unless a requirement explicitly grants the partner access.

#### Scenario: Member reads a shared record
- **WHEN** either member requests a shared record in their workspace
- **THEN** the system returns the record

#### Scenario: Member requests a personal record owned by the partner
- **WHEN** a member requests the partner's personal Todo or wish
- **THEN** the system denies access and does not disclose the record

#### Scenario: Client supplies another workspace identifier
- **WHEN** a protected request includes a workspace identifier not belonging to
  the authenticated member
- **THEN** the system ignores or rejects the identifier and returns no data
