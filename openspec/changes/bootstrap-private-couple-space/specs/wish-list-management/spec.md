## ADDED Requirements

### Requirement: Personal and shared wish tracking
An authenticated member SHALL be able to create wishes with a title, optional
note, optional target date, and visibility of `personal` or `shared`. Personal
wishes MUST be visible only to their owner, while shared wishes MUST be visible
to both members.

#### Scenario: Member creates a shared wish
- **WHEN** a member saves a valid shared wish
- **THEN** both members can view the wish in the workspace

#### Scenario: Member views the partner's personal wish list
- **WHEN** a member requests wishes marked personal and owned by the partner
- **THEN** the system returns none of those wishes

### Requirement: Wish progress lifecycle
The system MUST support `active`, `in_progress`, `fulfilled`, and `archived`
wish statuses. The owner of a personal wish controls it; either member can
update a shared wish.

#### Scenario: Member fulfills a shared wish
- **WHEN** either member marks an active shared wish as fulfilled
- **THEN** the wish status changes to `fulfilled` with an update timestamp

#### Scenario: Member updates the partner's personal wish
- **WHEN** a member attempts to modify a personal wish owned by the partner
- **THEN** the system denies the mutation
