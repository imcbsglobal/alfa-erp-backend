<!-- docs/api/job_titles.md -->
# Job Titles & Departments API

This document contains API documentation for Job Titles and Department management endpoints.

All endpoints below are mounted under `/api/auth/...` and require authentication using a Bearer token (JWT).
Only admin users (role `ADMIN` or `SUPERADMIN`) may create or update Job Titles and Departments.

---

## Create Department

Create a new department (admin only).

### Endpoint

```
POST /api/auth/departments/
```

### Authentication

Required — Admin users only. Add the Authorization header:

```
Authorization: Bearer <access_token>
```

### Request

Content-Type: application/json

Example payload:

```json
{
  "name": "Sales",
  "description": "Handles all outbound and inbound sales",
  "is_active": true
}
```

Fields:
- `name` (string, required): Unique department name (max 150 characters).
- `description` (string, optional): A textual description for the department.
- `is_active` (boolean, optional): Whether the department is active (default true).

### Response

Success (201 Created)
```json
{
  "success": true,
  "status_code": 201,
  "message": "Department created successfully",
  "data": {
    "id": "uuid-dept-123",
    "name": "Sales",
    "description": "Handles all outbound and inbound sales",
    "is_active": true,
    "created_at": "2025-12-12T10:00:00Z",
    "updated_at": "2025-12-12T10:00:00Z",
    "job_titles": []
  }
}
```

Errors:
- 400 Bad Request: validation errors (e.g., missing `name` or `name` already exists)
- 401 Unauthorized: missing or invalid JWT
- 403 Forbidden: user not an admin

### Example (cURL)

```bash
curl -X POST "http://localhost:8000/api/auth/departments/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Sales", "description":"Outbound sales team"}'
```

---

## Create Job Title

Create a new job title and attach it to a department (admin only).
Job Titles are unique per department — you cannot create duplicate titles under the same department.

### Endpoint

```
POST /api/auth/job-titles/
```

### Authentication

Required — Admin users only. Add the Authorization header:

```
Authorization: Bearer <access_token>
```

### Request

Content-Type: application/json

Example payload:

```json
{
  "title": "Sales Executive",
  "department_id": "uuid-dept-123",
  "description": "Sales executive working with outbound leads",
  "is_active": true
}
```

Fields:
- `title` (string, required): Job title name.
- `department_id` (UUID, required): Primary key of an existing Department to associate this title with.
- `description` (string, optional): A textual description of the job title.
- `is_active` (boolean, optional): Whether the job title is active.

### Response

Success (201 Created)
```json
{
  "success": true,
  "status_code": 201,
  "message": "Job title created successfully",
  "data": {
    "id": "uuid-job-456",
    "title": "Sales Executive",
    "description": "Sales executive working with outbound leads",
    "is_active": true,
    "department_id": "uuid-dept-123",
    "department": "Sales",
    "created_at": "2025-12-12T10:00:00Z",
    "updated_at": "2025-12-12T10:00:00Z"
  }
}
```

Errors:
- 400 Bad Request: validation errors (missing `title`, invalid `department_id` or duplicate title for the same department)
- 401 Unauthorized: missing or invalid JWT
- 403 Forbidden: user not an admin

### Example (cURL)

```bash
curl -X POST "http://localhost:8000/api/auth/job-titles/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Sales Executive","department_id":"uuid-dept-123","description":"Outbound leads"}'
```

---

## Notes / Best Practices
- Always create Departments first (`POST /api/auth/departments/`) and use the returned `id` as `department_id` when creating job titles.
- The API returns both `department` (name) and `department_id` (uuid) for convenience. Frontend code should use `department_id` when submitting changes.
- Job title uniqueness: the pair `(department_id, title)` is unique.
- When creating a User, supply `department_id` as the department foreign key if available (the backend also supports `department` name for backward compatibility).

---

If you’d like, I can also:
- Add update & delete endpoints docs for departments and job titles
- Add example responses for validation errors and common error codes
- Add a short frontend guide showing the `department_id` usage and a snippet to map `department_id` -> department name in UI
