## ADDED Requirements

### Requirement: One-tap check-ins and in-app delivery
An authenticated member SHALL be able to submit a check-in using an approved
preset or a bounded custom message. A check-in MUST be immutable and MUST create
an unread in-app notification for the other workspace member.

#### Scenario: Member sends a preset check-in
- **WHEN** a member submits the `arrived_home` preset
- **THEN** the system records the check-in and creates an unread notification
  for the partner

#### Scenario: Member submits an invalid check-in type or oversized message
- **WHEN** a check-in does not match an approved preset and exceeds the custom
  message constraints
- **THEN** the system rejects it without creating a notification

### Requirement: Opt-in WeChat subscription delivery
The client MUST request subscription permission only from a member-initiated
action. The backend SHALL retain the per-user, per-template permission result
and SHALL attempt WeChat subscription delivery only to a consenting recipient.

#### Scenario: Recipient explicitly accepts a notification template
- **WHEN** the recipient initiates the subscription request and accepts the
  configured template
- **THEN** the client records the acceptance with the backend for that user and
  template

#### Scenario: Check-in is sent to a consenting recipient
- **WHEN** a check-in creates an in-app notification for a recipient with
  current template consent
- **THEN** the backend queues one WeChat subscription-message delivery attempt
  while retaining the in-app notification

#### Scenario: Recipient has not granted or has denied template consent
- **WHEN** a check-in or meal request is created for that recipient
- **THEN** the system does not call WeChat delivery and keeps the in-app
  notification as the delivery path

### Requirement: Notification read state and delivery diagnostics
The recipient SHALL be able to list and mark their in-app notifications as
read. The backend MUST retain the outcome of each attempted external delivery
without changing the originating check-in or meal-request state on failure.

#### Scenario: Recipient opens an unread notification
- **WHEN** the recipient marks their own notification as read
- **THEN** the notification read timestamp is stored

#### Scenario: WeChat delivery fails
- **WHEN** WeChat returns a delivery failure for a queued notification
- **THEN** the failure is recorded for diagnostics and the in-app notification
  remains available
