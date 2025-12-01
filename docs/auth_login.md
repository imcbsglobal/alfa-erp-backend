# Authentication — Login

This document describes the Login API used to obtain JWT tokens and user information (including roles and avatar URL).

## Endpoint

- Path: `/api/auth/login/`
- Method: `POST`
- Authentication: Not required

## Purpose

- Authenticate a user using their `email` and `password`.
- Return JWT `access` and `refresh` tokens.
- Return user profile information for the frontend to use for UI and navigation logic.

## Request

- Content-Type: `application/json`

- Body Example:

```json
{
  "email": "admin@gmail.com",
  "password": "admin@123"
}
```

Notes:
- `email` is used as the username field (custom `User.USERNAME_FIELD` is `email`).
- There is no public sign-up; accounts are created by admin only.

## Response

- Success (HTTP 200): JSON with tokens and user data

Example:

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>",
  "user": {
    "id": 1,
    "email": "admin@gmail.com",
    "first_name": "Admin",
    "last_name": "User",
    "full_name": "Admin User",
    "avatar": "http://localhost:8000/media/avatars/2025/12/01/abc123.jpg",
    "is_staff": true,
    "is_superuser": true,
    "roles": ["Admin", "Manager"]
  }
}
```

Fields:
- `access` (string): short-lived JWT access token (default 1 hour). Use in `Authorization` header as: `Authorization: Bearer <access>`.
- `refresh` (string): refresh token to obtain new access token.
- `user` (object): information about the authenticated user.
  - `roles` is built from the user groups in Django and is returned as a list of strings.
  - `avatar` is the absolute URL to the user's avatar or `null` if none.

## Errors

- `401 Unauthorized` — Wrong credentials or inactive user.
- `400 Bad Request` — Missing `email` or `password` field.

Example error response (invalid credentials):

```json
{
  "detail": "No active account found with the given credentials"
}
```

## Refresh endpoint

- Path: `/api/auth/token/refresh/`
- Method: `POST`
- Body: `{ "refresh": "<refresh_token>" }`
- Response: `{ "access": "<new_access_token>" }`

## Client usage examples

cURL:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmail.com", "password":"admin@123"}'
```

HTTPie:

```bash
http POST http://localhost:8000/api/auth/login/ email=admin@gmail.com password=admin@123
```

Fetch example (front-end JavaScript):

```javascript
const resp = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'admin@gmail.com', password: 'admin@123' }),
});
const data = await resp.json();

// store tokens in secure storage (http-only cookies if possible), and use access token to
// authorize requests to protected APIs. Use `user.roles` for UI logic.
```

## Notes & Troubleshooting

- Ensure migrations are applied and the `accounts.User` table exists.
- `avatar` URLs require `MEDIA_URL`/`MEDIA_ROOT` to be configured and media served. In development, `runserver` will serve media when configured.
- Tokens expire; refresh tokens can be used to get a new access token.
- Backend enforces admin-only user creation; self-registration is disabled.
- `roles` come from Django `Group` names; make sure groups are created and users assigned.

## Related endpoints

- `POST /api/auth/token/refresh/` — Refresh access token
- `POST /api/auth/users/` — Admin-only create user (UserViewSet; permission `IsAdminUser`)
- `GET /api/auth/users/me/` — Get current user profile (authenticated users)
- `POST /api/auth/users/<id>/activate/` — Admin-only activate user
- `POST /api/auth/users/<id>/deactivate/` — Admin-only deactivate user

---

If you want, I can create a Swagger/OpenAPI spec or add example requests to a Postman collection. Would you prefer Swagger (drf-yasg) or a static Markdown file like this one to be exported to (or used by) the frontend team?