# Authentication Architecture

## Goals
- Secure authentication
- Multi-tenant support
- Stateless API

## Authentication Flow
(Register → Login → Refresh → Logout)

### Implemented baseline
- Registration creates a user, hashes the password, and issues access/refresh tokens.
- Login validates credentials and returns a new token pair.
- Refresh exchanges a valid refresh token for a new access token.
- Logout validates the supplied refresh token and returns a success response.
- Protected routes use bearer-token authentication through the current-user dependency.

## Token Strategy
- Access Token: short-lived bearer token for API access.
- Refresh Token: longer-lived token used to obtain a new access token.

## Authorization
- Organization Owner
- Admin
- Member

### Organization-aware access
- Users are associated with organizations through membership records.
- Organization-scoped endpoints check membership records before allowing access.
- The current implementation uses a simple membership check for organization access.

## Persistence Model
- users
- organizations
- organization_memberships

## Security Considerations
- Password hashing via a strong password hashing scheme.
- HttpOnly cookies (planned for browser-based sessions).
- CORS
- CSRF (planned once cookie-based sessions are introduced)
- Rate limiting (future)

## Sequence Diagram.

User
 │
 │ POST /auth/register
 ▼
API
 │
 │ Validate Request
 ▼
Auth Service
 │
 │ Hash Password
 ▼
Database
 │
 │ Create User
 ▼
API
 │
 │ Return Success
 ▼
User

## Entity Relationship Diagram

+----------------+
|     users      |
+----------------+
| id             |
| email          |
| username       |
| password_hash  |
| is_verified    |
| created_at     |
| updated_at     |
+----------------+
        ▲
        │
        │
+-------------------------+
| organization_members    |
+-------------------------+
| id                      |
| organization_id         |
| user_id                |
| role                   |
| created_at             |
+-------------------------+
        │
        ▼
+----------------+
| organizations  |
+----------------+
| id             |
| name           |
| slug           |
| owner_id       |
| created_at     |
| updated_at     |
+----------------+
