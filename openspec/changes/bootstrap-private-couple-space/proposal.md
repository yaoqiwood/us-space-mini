## Why

The couple needs one private place in WeChat to coordinate daily life without
mixing personal and shared information across several unrelated tools. The
initial system must establish a secure two-person workspace before feature work
can be implemented and tested consistently.

## What Changes

- Add a private, two-member-only account model with WeChat identity binding and
  an account-password first-login path; public registration is not provided.
- Add a couple workspace that scopes every record to the two linked members.
- Add personal and shared Todo items, including assignment, due date, status,
  and completion history.
- Add personal and shared wish list entries with progress states.
- Add kitchen meal requests so either partner can request a dish from the
  other partner and the recipient can accept, update, complete, or decline it.
- Add one-tap check-ins and opt-in WeChat subscription notifications, with
  in-app unread records as the delivery fallback.
- Establish the native WeChat Mini Program, FastAPI, and MySQL 8 application
  foundation required to operate the above capabilities.

## Capabilities

### New Capabilities
- `private-access`: Restricted access, credential sign-in, WeChat binding, and
  authenticated session management for the two allowed users.
- `couple-workspace`: Establishing and enforcing the single two-member
  workspace that owns all private and shared records.
- `todo-management`: Creating and managing personal and shared actionable
  items.
- `wish-list-management`: Creating and tracking personal and shared wishes.
- `kitchen-meal-requests`: Sending and processing one partner's request for a
  meal prepared by the other partner.
- `check-in-notifications`: One-tap reports, in-app delivery, and opt-in
  WeChat subscription-message delivery.

### Modified Capabilities

None.

## Impact

Adds a native TypeScript WeChat Mini Program and a FastAPI/MySQL 8 backend,
including schema migrations, authenticated REST endpoints, WeChat `wx.login`,
server-side `code2Session`, and subscription-message APIs. It requires secure
environment configuration for WeChat credentials, JWT signing keys, and MySQL
connection details.
