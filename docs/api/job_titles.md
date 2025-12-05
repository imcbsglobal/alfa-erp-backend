# Job Titles API

Complete API documentation for job title management endpoints.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://alfa-erp-backend.onrender.com`

**Authentication Required:** All endpoints require JWT authentication.

**Authorization Header:**
```
Authorization: Bearer <access_token>
```

---

## Overview

Job Titles represent user positions in the organization (e.g., Manager, Developer, Sales Representative). They are independent entities that can be assigned to users.

**Note:** Department is stored as a simple text field in the User model, not as a separate model.

---

## Table of Contents

1. [List All Job Titles](#list-all-job-titles)
2. [Get Job Title by ID](#get-job-title-by-id)
3. [Create Job Title](#create-job-title)
4. [Update Job Title](#update-job-title)
5. [Delete Job Title](#delete-job-title)

---

## List All Job Titles

Get all job titles in the system.

### Endpoint

```
GET /api/auth/job-titles/
```

### Authentication

Required (All authenticated users)

### Query Parameters

- `search` (string, optional): Search by title or description
- `ordering` (string, optional): Order by field (prefix with `-` for descending)
  - Examples: `title`, `-created_at`

### Request Example

```bash
GET /api/auth/job-titles/
Authorization: Bearer <access_token>
```

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "List retrieved successfully",
  "data": [
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "title": "Sales Manager",
      "description": "Manages sales team and strategies",
      "is_active": true,
      "created_at": "2025-12-01T10:00:00Z",
      "updated_at": "2025-12-01T10:00:00Z"
    },
    {
      "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "title": "Software Developer",
      "description": "Develops and maintains software applications",
      "is_active": true,
      "created_at": "2025-12-01T10:05:00Z",
      "updated_at": "2025-12-01T10:05:00Z"
    },
    {
      "id": "d4e5f6a7-b8c9-0123-def1-234567890123",
      "title": "HR Manager",
      "description": "Oversees HR operations and employee relations",
      "is_active": true,
      "created_at": "2025-12-01T10:10:00Z",
      "updated_at": "2025-12-01T10:10:00Z"
    }
  ]
}
```

### Usage Examples

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/auth/job-titles/" \
  -H "Authorization: Bearer <access_token>"
```

**JavaScript (Axios):**
```javascript
const response = await axios.get('/api/auth/job-titles/', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});

const jobTitles = response.data.data;
console.log(`Found ${jobTitles.length} job titles`);
```

**JavaScript (Fetch):**
```javascript
const response = await fetch('http://localhost:8000/api/auth/job-titles/', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});

const result = await response.json();
if (result.success) {
  const jobTitles = result.data;
}
```

---

## Get Job Title by ID

Retrieve a specific job title.

### Endpoint

```
GET /api/auth/job-titles/{id}/
```

### Authentication

Required (All authenticated users)

### Path Parameters

- `id` (UUID): Job Title ID

### Request Example

```bash
GET /api/auth/job-titles/b2c3d4e5-f6a7-8901-bcde-f12345678901/
Authorization: Bearer <access_token>
```

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Retrieved successfully",
  "data": {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "title": "Sales Manager",
    "description": "Manages sales team and strategies",
    "is_active": true,
    "created_at": "2025-12-01T10:00:00Z",
    "updated_at": "2025-12-01T10:00:00Z"
  }
}
```

**Error (404 Not Found):**
```json
{
  "success": false,
  "status_code": 404,
  "message": "Not found"
}
```

---

## Create Job Title

Create a new job title. **Admin only**.

### Endpoint

```
POST /api/auth/job-titles/
```

### Authentication

Required (Admin only)

### Request Body

```json
{
  "title": "Senior Software Engineer",
  "description": "Develops and maintains complex software systems",
  "is_active": true
}
```

**Required Fields:**
- `title` (string, max 150 chars): Job title name (must be unique)

**Optional Fields:**
- `description` (string): Job title description
- `is_active` (boolean, default: true): Active status

### Request Example

```bash
POST /api/auth/job-titles/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "title": "Senior Software Engineer",
  "description": "Develops and maintains complex software systems"
}
```

### Response

**Success (201 Created):**
```json
{
  "success": true,
  "status_code": 201,
  "message": "Created successfully",
  "data": {
    "id": "98765432-dcba-21fe-5432-10fedcba9876",
    "title": "Senior Software Engineer",
    "description": "Develops and maintains complex software systems",
    "is_active": true,
    "created_at": "2025-12-04T14:20:00Z",
    "updated_at": "2025-12-04T14:20:00Z"
  }
}
```

**Error (400 Bad Request - Duplicate):**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Validation failed",
  "errors": {
    "title": ["job title with this title already exists."]
  }
}
```

**Error (403 Forbidden):**
```json
{
  "success": false,
  "status_code": 403,
  "message": "You do not have permission to perform this action"
}
```

### Usage Examples

**JavaScript:**
```javascript
const createJobTitle = async (jobTitleData) => {
  const response = await axios.post('/api/auth/job-titles/', jobTitleData, {
    headers: { 'Authorization': `Bearer ${adminToken}` }
  });
  return response.data.data;
};

const newJobTitle = await createJobTitle({
  title: 'Senior Software Engineer',
  description: 'Develops and maintains complex software systems'
});
```

---

## Update Job Title

Update an existing job title. **Admin only**.

### Endpoints

```
PUT /api/auth/job-titles/{id}/     # Full update
PATCH /api/auth/job-titles/{id}/   # Partial update
```

### Authentication

Required (Admin only)

### Path Parameters

- `id` (UUID): Job Title ID

### Request Body

**PUT (all fields required):**
```json
{
  "title": "Lead Software Engineer",
  "description": "Leads development team and architecture decisions",
  "is_active": true
}
```

**PATCH (only fields to update):**
```json
{
  "description": "Updated job description"
}
```

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Updated successfully",
  "data": {
    "id": "98765432-dcba-21fe-5432-10fedcba9876",
    "title": "Lead Software Engineer",
    "description": "Leads development team and architecture decisions",
    "is_active": true,
    "created_at": "2025-12-04T14:20:00Z",
    "updated_at": "2025-12-04T15:30:00Z"
  }
}
```

**Error (400 Bad Request):**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Validation failed",
  "errors": {
    "title": ["This field is required."]
  }
}
```

### Usage Examples

**JavaScript - Partial Update:**
```javascript
const updateJobTitle = async (jobTitleId, updates) => {
  const response = await axios.patch(
    `/api/auth/job-titles/${jobTitleId}/`,
    updates,
    { headers: { 'Authorization': `Bearer ${adminToken}` } }
  );
  return response.data.data;
};

await updateJobTitle('98765432-dcba-21fe-5432-10fedcba9876', {
  description: 'Updated description'
});
```

---

## Delete Job Title

Delete a job title. **Admin only**.

⚠️ **Warning**: Users assigned to this job title will have their `job_title` field set to NULL (SET_NULL).

### Endpoint

```
DELETE /api/auth/job-titles/{id}/
```

### Authentication

Required (Admin only)

### Path Parameters

- `id` (UUID): Job Title ID

### Request Example

```bash
DELETE /api/auth/job-titles/98765432-dcba-21fe-5432-10fedcba9876/
Authorization: Bearer <admin_token>
```

### Response

**Success (204 No Content):**
```json
{
  "success": true,
  "status_code": 204,
  "message": "Deleted successfully"
}
```

**Error (404 Not Found):**
```json
{
  "success": false,
  "status_code": 404,
  "message": "Not found"
}
```

**Error (403 Forbidden):**
```json
{
  "success": false,
  "status_code": 403,
  "message": "You do not have permission to perform this action"
}
```

---

## Complete Workflow Example

### Scenario: Setting up Job Titles and Assigning to Users

**Step 1: Create Job Titles**
```javascript
const jobTitles = [
  { title: 'Manager', description: 'Team manager and leader' },
  { title: 'Senior Developer', description: 'Experienced developer' },
  { title: 'Junior Developer', description: 'Entry-level developer' },
  { title: 'HR Specialist', description: 'HR operations specialist' }
];

const createdTitles = [];
for (const jt of jobTitles) {
  const response = await axios.post('/api/auth/job-titles/', jt, {
    headers: { 'Authorization': `Bearer ${adminToken}` }
  });
  createdTitles.push(response.data.data);
}
```

**Step 2: Assign to User**
```javascript
// When creating or updating a user
await axios.patch(`/api/auth/users/${userId}/`, {
  department: 'Engineering',  // Simple text field
  job_title: seniorDevJobTitleId  // UUID reference
}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
});
```

**Step 3: Fetch All Job Titles for Dropdown**
```javascript
const response = await axios.get('/api/auth/job-titles/', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});

const jobTitleOptions = response.data.data.map(jt => ({
  value: jt.id,
  label: jt.title
}));
```

---

## Frontend Integration Examples

### React Component - Job Title Selector

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function JobTitleSelector({ value, onChange }) {
  const [jobTitles, setJobTitles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobTitles = async () => {
      try {
        const response = await axios.get('/api/auth/job-titles/');
        setJobTitles(response.data.data);
      } catch (error) {
        console.error('Failed to fetch job titles:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchJobTitles();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <select value={value} onChange={e => onChange(e.target.value)}>
      <option value="">Select Job Title</option>
      {jobTitles.map(jt => (
        <option key={jt.id} value={jt.id}>
          {jt.title}
        </option>
      ))}
    </select>
  );
}

// Usage in User Form
function UserForm() {
  const [formData, setFormData] = useState({
    email: '',
    department: '',  // Free text input
    job_title: ''    // UUID from selector
  });

  return (
    <form>
      <input
        type="text"
        placeholder="Department (e.g., Sales, HR, IT)"
        value={formData.department}
        onChange={e => setFormData({...formData, department: e.target.value})}
      />
      
      <JobTitleSelector
        value={formData.job_title}
        onChange={jobTitleId => setFormData({...formData, job_title: jobTitleId})}
      />
    </form>
  );
}
```

---

## Error Handling

### Common Errors

| Status | Scenario | Solution |
|--------|----------|----------|
| 400 | Duplicate job title | Use unique title |
| 403 | Non-admin trying to create/update/delete | Login as admin |
| 404 | Job Title not found | Verify ID exists |

---

## Best Practices

1. **Cache job titles** in frontend to reduce API calls
2. **Use PATCH for partial updates** to avoid overwriting unchanged fields
3. **Validate uniqueness** before submitting new job titles
4. **Handle SET_NULL** - users can exist without job titles
5. **Department is free text** - consider providing suggestions but allow custom input

---

## Database Schema

### Job Title Table (`job_titles`)
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| title | VARCHAR(150) | UNIQUE, NOT NULL |
| description | TEXT | NULLABLE |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | AUTO |
| updated_at | TIMESTAMP | AUTO |

### User Table Reference
| Column | Type | Constraints |
|--------|------|-------------|
| department | VARCHAR(100) | NULLABLE (Simple text field) |
| job_title_id | UUID | FOREIGN KEY (job_titles.id) ON DELETE SET NULL |

---

## Additional Resources

- [User Management API](./users.md)
- [Authentication API](./authentication.md)
- [Response Handlers Guide](../response_handlers.md)
