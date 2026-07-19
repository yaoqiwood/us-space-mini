## 1. Project and deployment foundation

- [x] 1.1 Create the native TypeScript WeChat Mini Program project structure and configure development, review, and production API base URLs.
- [x] 1.2 Create the FastAPI application structure, health endpoint, configuration loading, structured logging, and dependency definitions.
- [x] 1.3 Add Python dependencies for FastAPI, SQLAlchemy 2, Alembic, MySQL, JWT handling, Argon2id, and HTTP requests to WeChat APIs.
- [x] 1.4 Provision MySQL 8 configuration, HTTPS deployment configuration, secret environment variables, and Mini Program request-domain documentation.
- [x] 1.5 Add automated test configuration for backend API and domain tests.

## 2. Identity and workspace data model

- [x] 2.1 Define SQLAlchemy models and Alembic migrations for users, password credentials, WeChat OpenID bindings, refresh sessions, couples, and couple memberships.
- [x] 2.2 Enforce the one-active-couple, two-active-member production invariant during account and membership provisioning.
- [x] 2.3 Implement Argon2id credential provisioning and a separate review-data seed path that never exposes production accounts.
- [x] 2.4 Implement the server-side WeChat `code2Session` client with retry-safe error handling and no session-key exposure.
- [x] 2.5 Implement `POST /v1/auth/wechat`, `POST /v1/auth/bind`, token refresh, logout, and authenticated-current-user endpoints.
- [x] 2.6 Add FastAPI authentication and membership dependencies that scope all protected queries to the current member and couple.
- [x] 2.7 Test valid sessions, invalid credentials, OpenID binding conflicts, session expiry, and unauthenticated API rejection.

## 3. Shared data and notification foundation

- [x] 3.1 Define migrations and models for in-app notifications, per-user template consent, and external delivery attempts.
- [x] 3.2 Implement recipient-owned notification listing and read-state endpoints with couple-bound authorization.
- [x] 3.3 Implement the WeChat subscription-message client and a background delivery worker that records all delivery outcomes.
- [x] 3.4 Implement the Mini Program subscription-preference control using a user-triggered `wx.requestSubscribeMessage` call and send its result to the backend.
- [x] 3.5 Test notification ownership, consent denial, consent acceptance, and external delivery failure fallback.

## 4. Todo and wish capabilities

- [ ] 4.1 Define migrations and models for Todos, visibility, optional assignee, status, completion actor, and completion timestamp.
- [ ] 4.2 Implement couple-scoped Todo create, list, detail, update, complete, and cancel endpoints with personal-record authorization.
- [ ] 4.3 Add backend tests for personal visibility, shared visibility, valid completion, and partner personal-Todo denial.
- [ ] 4.4 Build native Mini Program Todo views for personal and shared lists, creation, editing, assignment, and status changes.
- [ ] 4.5 Define migrations and models for wishes, visibility, ownership, target date, and progress status.
- [ ] 4.6 Implement couple-scoped wish create, list, detail, update, and status endpoints with personal-record authorization.
- [ ] 4.7 Add backend tests for personal-wish privacy and shared-wish progress updates.
- [ ] 4.8 Build native Mini Program wish-list views for personal and shared wishes and their lifecycle actions.

## 5. Kitchen meal requests and check-ins

- [ ] 5.1 Define migrations and models for directed meal requests, requester, recipient, dish fields, desired time, and lifecycle timestamps.
- [ ] 5.2 Implement meal-request creation and strictly validated recipient/requester state-transition endpoints.
- [ ] 5.3 Create an in-app notification and background notification job atomically with each new meal request.
- [ ] 5.4 Add backend tests for invalid recipients, unauthorized transitions, cancellation, and terminal-state rejection.
- [ ] 5.5 Build native Mini Program meal-request creation, incoming request, and status-update views.
- [ ] 5.6 Define a bounded check-in preset catalog and a migration/model for immutable check-in events.
- [ ] 5.7 Implement check-in submission so it atomically creates the partner's in-app notification and eligible delivery job.
- [ ] 5.8 Add backend tests for check-in validation, recipient authorization, no-consent behavior, and push-failure retention.
- [ ] 5.9 Build the native Mini Program one-tap check-in surface, custom-message validation, and notification inbox.

## 6. App integration and release readiness

- [ ] 6.1 Implement Mini Program app startup, WeChat silent-login exchange, secure token storage, refresh handling, and first-bind account-password screen.
- [ ] 6.2 Add navigation and empty, loading, error, and unauthorized states for every private feature page.
- [ ] 6.3 Add a privacy guide and in-app privacy link whose declarations match the implemented Mini Program APIs and backend processing.
- [ ] 6.4 Prepare non-sensitive review credentials and a review checklist that demonstrates every declared feature.
- [ ] 6.5 Add end-to-end tests for both member accounts covering shared data, personal-data isolation, meal requests, check-ins, and notification fallback.
- [ ] 6.6 Perform real-device testing with both members, configure approved WeChat subscription templates, and verify notification consent behavior.
