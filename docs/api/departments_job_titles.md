# Departments & Job Titles API

Complete API documentation for department and job title management endpoints.

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

The Department and Job Title system provides organizational structure management:
- **Departments**: Organizational units (e.g., Sales, HR, IT)
- **Job Titles**: Positions within departments (e.g., Sales Manager, HR Assistant)
- One department can have multiple job titles
- Users are linked to departments and job titles via ForeignKey relationships

---

## Table of Contents

1. [List All Departments](#list-all-departments)
2. [Get Department by ID](#get-department-by-id)
3. [Create Department](#create-department)
4. [Update Department](#update-department)
5. [Delete Department](#delete-department)
6. [List All Job Titles](#list-all-job-titles)
7. [Get Job Title by ID](#get-job-title-by-id)
8. [Create Job Title](#create-job-title)
9. [Update Job Title](#update-job-title)
10. [Delete Job Title](#delete-job-title)

---

## Departments

### List All Departments

Get all departments with their associated job titles.

#### Endpoint

```
GET /api/auth/departments/
```

#### Authentication

Required (All authenticated users)

#### Query Parameters

- `search` (string, optional): Search by name or description
- `ordering` (string, optional): Order by field (prefix with `-` for descending)
  - Examples: `name`, `-created_at`

#### Request Example

```bash
GET /api/auth/departments/
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "List retrieved successfully",
  "data": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "Sales",
      "description": "Sales and marketing department",
      "is_active": true,
      "job_titles": [
        {
          "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
          "title": "Sales Manager",
          "description": "Manages sales team",
          "is_active": true
        },
        {
          "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
          "title": "Sales Representative",
          "description": "Handles customer accounts",
          "is_active": true
        }
      ]
    },
    {
      "id": "d4e5f6a7-b8c9-0123-def1-234567890123",
      "name": "Human Resources",
      "description": "HR and recruitment",
      "is_active": true,
      "job_titles": [
        {
          "id": "e5f6a7b8-c9d0-1234-ef12-345678901234",
          "title": "HR Manager",
          "description": "Oversees HR operations",
          "is_active": true
        },
        {
          "id": "f6a7b8c9-d0e1-2345-f123-456789012345",
          "title": "HR Assistant",
          "description": "Supports HR activities",
          "is_active": true
        }
      ]
    }
  ]
}
```

#### Usage Examples

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/auth/departments/" \
  -H "Authorization: Bearer <access_token>"
```

**JavaScript (Axios):**
```javascript
const response = await axios.get('/api/auth/departments/', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});

const departments = response.data.data;
departments.forEach(dept => {
  console.log(`${dept.name}: ${dept.job_titles.length} job titles`);
});
```

**JavaScript (Fetch):**
```javascript
const response = await fetch('http://localhost:8000/api/auth/departments/', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});

const result = await response.json();
if (result.success) {
  const departments = result.data;
}
```

---

### Get Department by ID

Retrieve a specific department with detailed information.

#### Endpoint

```
GET /api/auth/departments/{id}/
```

#### Authentication

Required (All authenticated users)

#### Path Parameters

- `id` (UUID): Department ID

#### Request Example

```bash
GET /api/auth/departments/a1b2c3d4-e5f6-7890-abcd-ef1234567890/
Authorization: Bearer <access_token>
```

#### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Retrieved successfully",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Sales",
    "description": "Sales and marketing department",
    "is_active": true,
    "job_titles": [
      {
        "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "title": "Sales Manager",
        "department": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "department_name": "Sales",
        "description": "Manages sales team",
        "is_active": true,
        "created_at": "2025-12-01T10:00:00Z",
        "updated_at": "2025-12-01T10:00:00Z"
      }
    ],
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

### Create Department

Create a new department. **Admin only**.

#### Endpoint

```
POST /api/auth/departments/
```

#### Authentication

Required (Admin only)

#### Request Body

```json
{
  "name": "Engineering",
  "description": "Software development and IT operations",
  "is_active": true
}
```

**Required Fields:**
- `name` (string, max 150 chars): Unique department name

**Optional Fields:**
- `description` (string): Department description
- `is_active` (boolean, default: true): Active status

#### Request Example

```bash
POST /api/auth/departments/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Engineering",
  "description": "Software development and IT operations"
}
```

#### Response

**Success (201 Created):**
```json
{
  "success": true,
  "status_code": 201,
  "message": "Created successfully",
  "data": {
    "id": "12345678-abcd-ef12-3456-7890abcdef12",
    "name": "Engineering",
    "description": "Software development and IT operations",
    "is_active": true,
    "job_titles": [],
    "created_at": "2025-12-04T12:30:00Z",
    "updated_at": "2025-12-04T12:30:00Z"
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
    "name": ["This field is required."]
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

#### Usage Examples

**JavaScript:**
```javascript
const createDepartment = async (departmentData) => {
  const response = await axios.post('/api/auth/departments/', departmentData, {
    headers: { 'Authorization': `Bearer ${adminToken}` }
  });
  return response.data.data;
};

const newDept = await createDepartment({
  name: 'Engineering',
  description: 'Software development and IT operations'
});
```

---

### Update Department

Update an existing department. **Admin only**.

#### Endpoints

```
PUT /api/auth/departments/{id}/     # Full update
PATCH /api/auth/departments/{id}/   # Partial update
```

#### Authentication

Required (Admin only)

#### Path Parameters

- `id` (UUID): Department ID

#### Request Body

**PUT (all fields required):**
```json
{
  "name": "Engineering & IT",
  "description": "Software development, IT operations, and infrastructure",
  "is_active": true
}
```

**PATCH (only fields to update):**
```json
{
  "description": "Updated description"
}
```

#### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Updated successfully",
  "data": {
    "id": "12345678-abcd-ef12-3456-7890abcdef12",
    "name": "Engineering & IT",
    "description": "Software development, IT operations, and infrastructure",
    "is_active": true,
    "job_titles": [],
    "created_at": "2025-12-04T12:30:00Z",
    "updated_at": "2025-12-04T14:15:00Z"
  }
}
```

---

### Delete Department

Delete a department. **Admin only**.

⚠️ **Warning**: Deleting a department will also delete all associated job titles due to CASCADE relationship.

#### Endpoint

```
DELETE /api/auth/departments/{id}/
```

#### Authentication

Required (Admin only)

#### Path Parameters

- `id` (UUID): Department ID

#### Request Example

```bash
DELETE /api/auth/departments/12345678-abcd-ef12-3456-7890abcdef12/
Authorization: Bearer <admin_token>
```

#### Response

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

---

## Job Titles

### List All Job Titles

Get all job titles with department information.

#### Endpoint

```
GET /api/auth/job-titles/
```

#### Authentication

Required (All authenticated users)

#### Query Parameters

- `department` (UUID, optional): Filter by department ID
- `search` (string, optional): Search by title or description
- `ordering` (string, optional): Order by field (prefix with `-` for descending)
  - Examples: `title`, `-created_at`, `department`

#### Request Examples

**All job titles:**
```bash
GET /api/auth/job-titles/
Authorization: Bearer <access_token>
```

**Job titles for specific department:**
```bash
GET /api/auth/job-titles/?department=a1b2c3d4-e5f6-7890-abcd-ef1234567890
Authorization: Bearer <access_token>
```

#### Response

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
      "department": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "department_name": "Sales",
      "description": "Manages sales team and strategies",
      "is_active": true,
      "created_at": "2025-12-01T10:00:00Z",
      "updated_at": "2025-12-01T10:00:00Z"
    },
    {
      "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "title": "Sales Representative",
      "department": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "department_name": "Sales",
      "description": "Handles customer accounts and sales",
      "is_active": true,
      "created_at": "2025-12-01T10:05:00Z",
      "updated_at": "2025-12-01T10:05:00Z"
    }
  ]
}
```

#### Usage Examples

**JavaScript - Get all job titles for a department:**
```javascript
const getJobTitlesByDepartment = async (departmentId) => {
  const response = await axios.get('/api/auth/job-titles/', {
    params: { department: departmentId },
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  return response.data.data;
};

const salesJobTitles = await getJobTitlesByDepartment('a1b2c3d4-e5f6-7890-abcd-ef1234567890');
```

---

### Get Job Title by ID

Retrieve a specific job title.

#### Endpoint

```
GET /api/auth/job-titles/{id}/
```

#### Authentication

Required (All authenticated users)

#### Path Parameters

- `id` (UUID): Job Title ID

#### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Retrieved successfully",
  "data": {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "title": "Sales Manager",
    "department": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "department_name": "Sales",
    "description": "Manages sales team and strategies",
    "is_active": true,
    "created_at": "2025-12-01T10:00:00Z",
    "updated_at": "2025-12-01T10:00:00Z"
  }
}
```

---

### Create Job Title

Create a new job title under a department. **Admin only**.

#### Endpoint

```
POST /api/auth/job-titles/
```

#### Authentication

Required (Admin only)

#### Request Body

```json
{
  "title": "Senior Software Engineer",
  "department": "12345678-abcd-ef12-3456-7890abcdef12",
  "description": "Develops and maintains software systems",
  "is_active": true
}
```

**Required Fields:**
- `title` (string, max 150 chars): Job title name
- `department` (UUID): Department ID

**Optional Fields:**
- `description` (string): Job title description
- `is_active` (boolean, default: true): Active status

**Unique Constraint**: The combination of `department` and `title` must be unique.

#### Request Example

```bash
POST /api/auth/job-titles/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "title": "Senior Software Engineer",
  "department": "12345678-abcd-ef12-3456-7890abcdef12",
  "description": "Develops and maintains software systems"
}
```

#### Response

**Success (201 Created):**
```json
{
  "success": true,
  "status_code": 201,
  "message": "Created successfully",
  "data": {
    "id": "98765432-dcba-21fe-5432-10fedcba9876",
    "title": "Senior Software Engineer",
    "department": "12345678-abcd-ef12-3456-7890abcdef12",
    "department_name": "Engineering",
    "description": "Develops and maintains software systems",
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
    "non_field_errors": ["The fields department, title must make a unique set."]
  }
}
```

#### Usage Examples

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
  department: '12345678-abcd-ef12-3456-7890abcdef12',
  description: 'Develops and maintains software systems'
});
```

---

### Update Job Title

Update an existing job title. **Admin only**.

#### Endpoints

```
PUT /api/auth/job-titles/{id}/     # Full update
PATCH /api/auth/job-titles/{id}/   # Partial update
```

#### Authentication

Required (Admin only)

#### Path Parameters

- `id` (UUID): Job Title ID

#### Request Body

**PUT (all fields required):**
```json
{
  "title": "Lead Software Engineer",
  "department": "12345678-abcd-ef12-3456-7890abcdef12",
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

#### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Updated successfully",
  "data": {
    "id": "98765432-dcba-21fe-5432-10fedcba9876",
    "title": "Lead Software Engineer",
    "department": "12345678-abcd-ef12-3456-7890abcdef12",
    "department_name": "Engineering",
    "description": "Leads development team and architecture decisions",
    "is_active": true,
    "created_at": "2025-12-04T14:20:00Z",
    "updated_at": "2025-12-04T15:30:00Z"
  }
}
```

---

### Delete Job Title

Delete a job title. **Admin only**.

⚠️ **Warning**: Users assigned to this job title will have their `job_title` field set to NULL (SET_NULL).

#### Endpoint

```
DELETE /api/auth/job-titles/{id}/
```

#### Authentication

Required (Admin only)

#### Path Parameters

- `id` (UUID): Job Title ID

#### Request Example

```bash
DELETE /api/auth/job-titles/98765432-dcba-21fe-5432-10fedcba9876/
Authorization: Bearer <admin_token>
```

#### Response

**Success (204 No Content):**
```json
{
  "success": true,
  "status_code": 204,
  "message": "Deleted successfully"
}
```

---

## Complete Workflow Example

### Scenario: Setting up Sales Department with Job Titles

**Step 1: Create Department**
```javascript
const dept = await axios.post('/api/auth/departments/', {
  name: 'Sales',
  description: 'Sales and marketing operations'
}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
});

const departmentId = dept.data.data.id;
```

**Step 2: Create Job Titles**
```javascript
const jobTitles = [
  { title: 'Sales Manager', description: 'Manages sales team' },
  { title: 'Sales Representative', description: 'Handles customer accounts' },
  { title: 'Sales Intern', description: 'Entry-level sales position' }
];

for (const jt of jobTitles) {
  await axios.post('/api/auth/job-titles/', {
    ...jt,
    department: departmentId
  }, {
    headers: { 'Authorization': `Bearer ${adminToken}` }
  });
}
```

**Step 3: Assign Users**
```javascript
// When creating or updating a user
await axios.patch(`/api/auth/users/${userId}/`, {
  department: departmentId,
  job_title: salesManagerJobTitleId
}, {
  headers: { 'Authorization': `Bearer ${adminToken}` }
});
```

**Step 4: Fetch Department with Job Titles**
```javascript
const response = await axios.get(`/api/auth/departments/${departmentId}/`, {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});

// Response includes nested job_titles array
const department = response.data.data;
console.log(`${department.name} has ${department.job_titles.length} job titles`);
```

---

## Frontend Integration Examples

### React Component - Department Selector

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function DepartmentJobTitleSelector({ onSelect }) {
  const [departments, setDepartments] = useState([]);
  const [selectedDept, setSelectedDept] = useState('');
  const [jobTitles, setJobTitles] = useState([]);
  const [selectedJobTitle, setSelectedJobTitle] = useState('');

  useEffect(() => {
    // Fetch all departments
    const fetchDepartments = async () => {
      const response = await axios.get('/api/auth/departments/');
      setDepartments(response.data.data);
    };
    fetchDepartments();
  }, []);

  useEffect(() => {
    // When department changes, get its job titles
    if (selectedDept) {
      const dept = departments.find(d => d.id === selectedDept);
      setJobTitles(dept?.job_titles || []);
      setSelectedJobTitle('');
    }
  }, [selectedDept, departments]);

  useEffect(() => {
    // Notify parent component
    if (selectedDept && selectedJobTitle) {
      onSelect({ department: selectedDept, jobTitle: selectedJobTitle });
    }
  }, [selectedDept, selectedJobTitle]);

  return (
    <div>
      <select value={selectedDept} onChange={e => setSelectedDept(e.target.value)}>
        <option value="">Select Department</option>
        {departments.map(dept => (
          <option key={dept.id} value={dept.id}>{dept.name}</option>
        ))}
      </select>

      {selectedDept && (
        <select value={selectedJobTitle} onChange={e => setSelectedJobTitle(e.target.value)}>
          <option value="">Select Job Title</option>
          {jobTitles.map(jt => (
            <option key={jt.id} value={jt.id}>{jt.title}</option>
          ))}
        </select>
      )}
    </div>
  );
}
```

---

## Error Handling

### Common Errors

| Status | Scenario | Solution |
|--------|----------|----------|
| 400 | Duplicate department name | Use unique name |
| 400 | Duplicate job title in same department | Use different title or department |
| 403 | Non-admin trying to create/update/delete | Login as admin |
| 404 | Department/Job Title not found | Verify ID exists |
| 500 | Database constraint violation | Check foreign key relationships |

---

## Best Practices

1. **Always fetch departments first** to get the complete structure with job titles
2. **Use department filtering** when fetching job titles for better performance
3. **Handle cascading deletes** - warn users before deleting departments
4. **Validate department exists** before creating job titles
5. **Use PATCH for partial updates** to avoid overwriting unchanged fields
6. **Cache department/job title data** in frontend to reduce API calls

---

## Database Schema

### Department Table (`departments`)
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| name | VARCHAR(150) | UNIQUE, NOT NULL |
| description | TEXT | NULLABLE |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | AUTO |
| updated_at | TIMESTAMP | AUTO |

### Job Title Table (`job_titles`)
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| title | VARCHAR(150) | NOT NULL |
| department_id | UUID | FOREIGN KEY (departments.id) ON DELETE CASCADE |
| description | TEXT | NULLABLE |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | AUTO |
| updated_at | TIMESTAMP | AUTO |
| | | UNIQUE (department_id, title) |

### User Table Updates
| Column | Type | Constraints |
|--------|------|-------------|
| department_id | UUID | FOREIGN KEY (departments.id) ON DELETE SET NULL |
| job_title_id | UUID | FOREIGN KEY (job_titles.id) ON DELETE SET NULL |

---

## Additional Resources

- [User Management API](./users.md)
- [Authentication API](./authentication.md)
- [Response Handlers Guide](../response_handlers.md)
