## Context

This repository starts without application code. The product is a private
couple-space Mini Program used by exactly two people, but it still needs a
normal sign-in surface and an account-password fallback for first-time binding
and Mini Program review. The native Mini Program needs a secure backend to own
the user data, authorization rules, and WeChat API credentials.

The product combines personal records and records shared by the two members.
Every API call must therefore prove both the authenticated member and the
member's relationship to the record's couple. WeChat subscription messages are
best-effort because the recipient controls template permission and can revoke
it at any time.

## Goals / Non-Goals

**Goals:**

- Build a native TypeScript WeChat Mini Program and a FastAPI/MySQL 8 backend.
- Allow two pre-provisioned accounts to sign in, bind their WeChat identity,
  and use the product without repeated password entry.
- Keep personal records private and shared records visible to both members.
- Model Todo, wishes, meal requests, and check-ins with explicit state
  transitions and audit timestamps.
- Deliver actionable events in-app and use WeChat subscription messages only
  when the recipient has granted template permission.

**Non-Goals:**

- Public registration, multi-couple tenancy, social discovery, chat, photos,
  payments, delivery-platform ordering, or location tracking.
- Guaranteed push delivery, background polling, or a substitute for emergency
  communication.
- Collecting a WeChat profile, phone number, contacts, or precise location.

## Decisions

### Native Mini Program and REST backend

Use a native Mini Program written in TypeScript, WXML, and WXSS. Build a
versioned JSON REST API in FastAPI using Pydantic request validation, SQLAlchemy
2, Alembic, and MySQL 8. Store all timestamps in UTC and return ISO 8601 values.

Native development keeps the first release aligned with WeChat APIs such as
`wx.login` and `wx.requestSubscribeMessage`, without introducing a cross-platform
runtime. A server-owned REST API keeps data, credentials, and notification
delivery off the client. A cloud-only backend was considered but rejected
because FastAPI plus MySQL 8 is an explicit product requirement.

### Two-stage authentication and session model

On launch, the client calls `wx.login` and sends its single-use code to
`POST /v1/auth/wechat`. The backend calls WeChat `code2Session`, never exposes
`session_key`, and looks up the returned OpenID. A bound and active account
receives a short-lived signed JWT access token and a renewable server-side
refresh session.

For an unbound OpenID, the login screen accepts only a pre-provisioned username
and password at `POST /v1/auth/bind`. A successful password verification binds
that OpenID once and issues the same session. There is no registration endpoint.
Passwords are stored as Argon2id hashes; credentials, refresh sessions, and
OpenID bindings are unique and revocable. This preserves the requested
account-password sign-in while making daily sign-in frictionless.

The alternative of passwords alone would not support reliable WeChat
subscription delivery or device identity. WeChat-only login would omit the
requested account-password and review-account path.

### Couple-bound ownership and authorization

Use `users`, `couples`, and `couple_members` tables. Production setup creates
one active couple with exactly two active members; the service also enforces
this invariant during provisioning. Each domain row records `couple_id`,
`creator_user_id`, and, where relevant, `owner_user_id` or `recipient_user_id`.

Authentication dependencies load the current user and membership before every
protected endpoint. Queries always filter by the current user's `couple_id`;
personal entities also filter by owner. Client-supplied couple IDs and owner IDs
are ignored or validated against this context. This is preferable to trusting
route parameters because all data shares the same private boundary.

### Domain state models

- Todos use `visibility` (`personal` or `shared`) and `status` (`open`,
  `completed`, `cancelled`). Personal Todos have one owner. Shared Todos can
  have an optional assignee from the couple. Completion records actor and time.
- Wishes use the same visibility and owner rules, with `status` (`active`,
  `in_progress`, `fulfilled`, `archived`).
- Meal requests are directed records with immutable requester and recipient,
  dish name, quantity, optional note and desired time. Allowed transitions are
  `pending -> accepted|declined|cancelled`, `accepted -> preparing|cancelled`,
  and `preparing -> completed|cancelled`. The recipient performs accept,
  decline, prepare, and complete; the requester can cancel before completion.
- Check-ins are immutable events with a preset type or bounded custom message.
  Each creates an in-app notification owned by the partner.

Explicit states make UI and API tests deterministic. Free-form status strings
were rejected because they make authorization and lifecycle validation fragile.

### Notification delivery

When a user taps an in-app notification preference control, the client calls
`wx.requestSubscribeMessage` for a configured template. It sends the result to
the backend, which records consent per user and template. A check-in or meal
request first writes its domain event and in-app notification in the same
database transaction; a background worker then attempts WeChat delivery only
for a currently consenting recipient.

The WeChat send result is retained for diagnostics but does not alter the domain
event. The recipient's in-app notification remains the source of truth if the
template is denied, revoked, unavailable, or delivery fails. A synchronous push
call was rejected because external API latency and failures must not lose the
underlying request.

### Data protection and operational configuration

Keep MySQL credentials, JWT signing keys, WeChat AppID/AppSecret, template IDs,
and review-only credentials in environment configuration or a secret manager.
Use HTTPS endpoints and configure the approved Mini Program request domain
before real-device testing. Set a privacy guide that declares only the actual
identity and notification processing. Review environments use separate seeded
test accounts and non-production data.

## Risks / Trade-offs

- [A recipient denies or revokes a subscription template] -> Persist the event
  and in-app unread notification first; surface subscription status in settings.
- [A review tester binds a real production account] -> Use distinct review
  credentials and an isolated review data configuration; do not expose the two
  real accounts as test credentials.
- [An OpenID binding is attempted for an account already bound elsewhere] ->
  Reject it without changing either binding; require an authenticated recovery
  procedure to replace a device identity.
- [Sensitive couple data leaks through an IDOR bug] -> Centralize membership
  filters, avoid trusting client ownership fields, and test every resource
  family for cross-user denial.
- [The service is private but formally published] -> Provide meaningful
  functionality, a complete review path, accurate privacy guidance, and review
  credentials before submission.

## Migration Plan

1. Provision HTTPS hosting, the MySQL 8 database, environment secrets, and the
   Mini Program server request domain.
2. Deploy database migrations and seed only the two approved accounts in
   production; seed separate review accounts in the review environment.
3. Deploy the backend health endpoint, authentication flow, and core API before
   uploading the Mini Program build.
4. Configure and test approved subscription templates with both real devices.
5. Release first to the two configured experience members. Before public
   submission, verify review credentials, privacy guidance, and all declared
   features.

Database migrations roll back by restoring the prior application version and,
when safe, running a down migration. Domain events are never deleted as part of
notification retry or rollback handling.

## Open Questions

- Which exact Mini Program service category and subscription-message templates
  will be accepted in the WeChat management console?
- Which hosting provider and domain will be used, including ICP filing needs if
  the backend is hosted in mainland China?
- Which check-in presets and meal-request fields should appear in the first UI?
