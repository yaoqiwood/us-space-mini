## ADDED Requirements

### Requirement: Restricted account access
The system SHALL permit access only to active, pre-provisioned accounts and
MUST NOT expose public account registration.

#### Scenario: Unregistered visitor opens the application
- **WHEN** a WeChat identity has no binding and supplies no valid credentials
- **THEN** the system shows the sign-in screen and denies all private APIs

#### Scenario: Inactive or unknown account credentials are submitted
- **WHEN** an account-password sign-in attempt does not match an active
  pre-provisioned account
- **THEN** the system denies the sign-in without creating an account or binding

### Requirement: WeChat identity binding and session issuance
The client SHALL use `wx.login` to obtain a code and the backend MUST exchange
it with WeChat for an OpenID. A bound active account MUST receive an
authenticated session without a password prompt; an unbound OpenID MAY be bound
only after valid account-password verification.

#### Scenario: Bound member launches the Mini Program
- **WHEN** WeChat code exchange resolves to an active bound account
- **THEN** the backend issues an authenticated session and the client enters
  the private workspace

#### Scenario: First successful account-password sign-in
- **WHEN** an unbound OpenID submits valid credentials for an unbound active
  account
- **THEN** the backend binds that OpenID to the account and issues an
  authenticated session

#### Scenario: OpenID is already bound to another account
- **WHEN** valid credentials are submitted while the current OpenID is bound
  to a different account
- **THEN** the backend denies the binding and preserves both existing accounts

### Requirement: Secure credential and session handling
The backend MUST store passwords only as Argon2id hashes, MUST NOT return
WeChat session keys to the client, and MUST require a valid authenticated
session for private APIs.

#### Scenario: Private API is called without a valid session
- **WHEN** a request lacks a valid unexpired access token
- **THEN** the API returns an authentication error and no private data

#### Scenario: A password is persisted
- **WHEN** an administrator provisions or updates an account password
- **THEN** only an Argon2id password hash is stored
