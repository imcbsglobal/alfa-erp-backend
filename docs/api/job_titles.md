# Job Titles & Departments API Documentation

Complete API documentation for managing Job Titles and Departments in the ALFA ERP system.

## Overview

**Note:** Departments are now a first-class model. Job Titles belong to a `Department` (via `department_id`). Use the `/api/auth/departments/` endpoints to manage departments and pass `department_id` when creating or updating job titles.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://alfa-erp-backend.onrender.com`

**Authentication Required:** All endpoints require JWT authentication.

**Authorization Header:**
```
Authorization: Bearer <access_token>
```

---

## Department Management

### List All Departments

Get a list of all departments with their associated job titles.

**Endpoint:**
```
GET /api/auth/departments/
```

**Authentication:** Required (Any authenticated user)

**Response (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "List retrieved successfully",
  "data": {
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "dept-uuid-123",
        "name": "Sales",
        "description": "Sales and Marketing Department",
        "is_active": true,
        "job_titles": [
          {
            "id": "job-uuid-456",
            "title": "Sales Executive",
            "description": "Handles client relationships",
            "is_active": true,
            "department_id": "dept-uuid-123",
            "department": "Sales",
            "created_at": "2025-01-15T10:00:00Z",
            "updated_at": "2025-01-15T10:00:00Z"
          },
          {
            "id": "job-uuid-789",
            "title": "Sales Manager",
            "description": "Manages sales team",
            "is_active": true,
            "department_id": "dept-uuid-123",
            "department": "Sales",
            "created_at": "2025-01-16T10:00:00Z",
            "updated_at": "2025-01-16T10:00:00Z"
          }
        ],
        "created_at": "2025-01-10T08:00:00Z",
        "updated_at": "2025-01-10T08:00:00Z"
      },
      {
        "id": "dept-uuid-456",
        "name": "IT",
        "description": "Information Technology Department",
        "is_active": true,
        "job_titles": [],
        "created_at": "2025-01-11T09:00:00Z",
        "updated_at": "2025-01-11T09:00:00Z"
      }
    ]
  }
}
```

**Usage Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/auth/departments/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const result = await response.json();
if (result.success) {
  const departments = result.data.results;
  console.log('Total departments:', result.data.count);
}
```

---

### Get Department by ID

Retrieve a specific department with its job titles.

**Endpoint:**
```
GET /api/auth/departments/{id}/
```

**Authentication:** Required

**Path Parameters:**
- `id` (UUID, required): Department UUID

**Response (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Detail retrieved successfully",
  "data": {
    "id": "dept-uuid-123",
    "name": "Sales",
    "description": "Sales and Marketing Department",
    "is_active": true,
    "job_titles": [
      {
        "id": "job-uuid-456",
        "title": "Sales Executive",
        "description": "Handles client relationships",
        "is_active": true,
        "department_id": "dept-uuid-123",
        "department": "Sales",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
      }
    ],
    "created_at": "2025-01-10T08:00:00Z",
    "updated_at": "2025-01-10T08:00:00Z"
  }
}
```

---

### Create Department

Create a new department (Admin only).

**Endpoint:**
```
POST /api/auth/departments/
```

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "name": "Human Resources",
  "description": "HR and Employee Management",
  "is_active": true
}
```

**Field Requirements:**
- `name` (string, required): Department name (unique, max 150 chars)
- `description` (string, optional): Department description
- `is_active` (boolean, optional): Whether the department is active (default: true)

**Response (201 Created):**
```json
{
  "success": true,
  "status_code": 201,
  "message": "Created successfully",
  "data": {
    "id": "dept-uuid-new",
    "name": "Human Resources",
    "description": "HR and Employee Management",
    "is_active": true,
    "job_titles": [],
    "created_at": "2025-12-12T10:30:00Z",
    "updated_at": "2025-12-12T10:30:00Z"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Validation error",
  "errors": {
    "name": ["Department with this name already exists."]
  }
}
```

**Usage Example (JavaScript):**
```javascript
const createDepartment = async (data) => {
  const response = await fetch('http://localhost:8000/api/auth/departments/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  return await response.json();
};

// Usage
const newDept = await createDepartment({
  name: "Human Resources",
  description: "HR and Employee Management",
  is_active: true
});
```

---

### Update Department

Update an existing department (Admin only).

**Endpoint:**
```
PUT /api/auth/departments/{id}/
PATCH /api/auth/departments/{id}/
```

**Authentication:** Required (Admin only)

**Path Parameters:**
- `id` (UUID, required): Department UUID

**Request Body (PUT - all fields required):**
```json
{
  "name": "Sales & Marketing",
  "description": "Updated description",
  "is_active": true
}
```

**Request Body (PATCH - partial update):**
```json
{
  "name": "Sales & Marketing"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Updated successfully",
  "data": {
    "id": "dept-uuid-123",
    "name": "Sales & Marketing",
    "description": "Updated description",
    "is_active": true,
    "job_titles": [...],
    "created_at": "2025-01-10T08:00:00Z",
    "updated_at": "2025-12-12T11:00:00Z"
  }
}
```

---

### Delete Department

Delete a department (Admin only). Note: This will also affect associated job titles depending on CASCADE settings.

**Endpoint:**
```
DELETE /api/auth/departments/{id}/
```

**Authentication:** Required (Admin only)

**Path Parameters:**
- `id` (UUID, required): Department UUID

**Response (204 No Content):**
```json
{
  "success": true,
  "status_code": 204,
  "message": "Deleted successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Cannot delete department with associated job titles"
}
```

---

## Job Title Management

### List All Job Titles

Get a list of all job titles with their associated departments.

**Endpoint:**
```
GET /api/auth/job-titles/
```

**Authentication:** Required (Any authenticated user)

**Query Parameters:**
- `department` (UUID, optional): Filter by department ID

**Response (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "List retrieved successfully",
  "data": {
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "job-uuid-456",
        "title": "Sales Executive",
        "description": "Handles client relationships and sales",
        "is_active": true,
        "department_id": "dept-uuid-123",
        "department": "Sales",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
      },
      {
        "id": "job-uuid-789",
        "title": "Software Engineer",
        "description": "Develops and maintains software applications",
        "is_active": true,
        "department_id": "dept-uuid-456",
        "department": "IT",
        "created_at": "2025-01-16T10:00:00Z",
        "updated_at": "2025-01-16T10:00:00Z"
      }
    ]
  }
}
```

**Filter by Department Example:**
```
GET /api/auth/job-titles/?department=dept-uuid-123
```

**Usage Example (JavaScript):**
```javascript
// Get all job titles
const response = await fetch('http://localhost:8000/api/auth/job-titles/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

// Get job titles for a specific department
const salesJobTitles = await fetch(
  'http://localhost:8000/api/auth/job-titles/?department=dept-uuid-123',
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  }
);
```

---

### Get Job Title by ID

Retrieve a specific job title.

**Endpoint:**
```
GET /api/auth/job-titles/{id}/
```

**Authentication:** Required

**Path Parameters:**
- `id` (UUID, required): Job Title UUID

**Response (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Detail retrieved successfully",
  "data": {
    "id": "job-uuid-456",
    "title": "Sales Executive",
    "description": "Handles client relationships and sales",
    "is_active": true,
    "department_id": "dept-uuid-123",
    "department": "Sales",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:00:00Z"
  }
}
```

---

### Create Job Title

Create a new job title (Admin only).

**Endpoint:**
```
POST /api/auth/job-titles/
```

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "title": "Senior Sales Manager",
  "description": "Leads the sales team and strategizes growth",
  "department_id": "dept-uuid-123",
  "is_active": true
}
```

**Field Requirements:**
- `title` (string, required): Job title name (max 150 chars)
- `description` (string, optional): Job title description
- `department_id` (UUID, optional): Reference to Department (nullable)
- `is_active` (boolean, optional): Whether the job title is active (default: true)

**Note:** Job titles are unique per department (unique_together constraint on department + title).

**Response (201 Created):**
```json
{
  "success": true,
  "status_code": 201,
  "message": "Created successfully",
  "data": {
    "id": "job-uuid-new",
    "title": "Senior Sales Manager",
    "description": "Leads the sales team and strategizes growth",
    "is_active": true,
    "department_id": "dept-uuid-123",
    "department": "Sales",
    "created_at": "2025-12-12T10:45:00Z",
    "updated_at": "2025-12-12T10:45:00Z"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Validation error",
  "errors": {
    "title": ["Job title with this department and title already exists."]
  }
}
```

**Usage Example (JavaScript):**
```javascript
const createJobTitle = async (data) => {
  const response = await fetch('http://localhost:8000/api/auth/job-titles/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  return await response.json();
};

// Usage
const newJobTitle = await createJobTitle({
  title: "Senior Sales Manager",
  description: "Leads the sales team and strategizes growth",
  department_id: "dept-uuid-123",
  is_active: true
});
```

---

### Update Job Title

Update an existing job title (Admin only).

**Endpoint:**
```
PUT /api/auth/job-titles/{id}/
PATCH /api/auth/job-titles/{id}/
```

**Authentication:** Required (Admin only)

**Path Parameters:**
- `id` (UUID, required): Job Title UUID

**Request Body (PUT - all fields required):**
```json
{
  "title": "Senior Sales Manager",
  "description": "Updated description",
  "department_id": "dept-uuid-123",
  "is_active": true
}
```

**Request Body (PATCH - partial update):**
```json
{
  "title": "Lead Sales Manager",
  "department_id": "dept-uuid-456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Updated successfully",
  "data": {
    "id": "job-uuid-456",
    "title": "Lead Sales Manager",
    "description": "Updated description",
    "is_active": true,
    "department_id": "dept-uuid-456",
    "department": "IT",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-12-12T11:30:00Z"
  }
}
```

---

### Delete Job Title

Delete a job title (Admin only).

**Endpoint:**
```
DELETE /api/auth/job-titles/{id}/
```

**Authentication:** Required (Admin only)

**Path Parameters:**
- `id` (UUID, required): Job Title UUID

**Response (204 No Content):**
```json
{
  "success": true,
  "status_code": 204,
  "message": "Deleted successfully"
}
```

---

## Complete Integration Examples

### React/JavaScript Integration

```javascript
// services/auth.js or services/api.js

import api from './api'; // Your axios instance with auth interceptor

// =============== DEPARTMENT APIs ===============

export const getDepartments = async () => {
  return api.get('/auth/departments/');
};

export const getDepartment = async (id) => {
  return api.get(`/auth/departments/${id}/`);
};

export const createDepartment = async (data) => {
  return api.post('/auth/departments/', data);
};

export const updateDepartment = async (id, data) => {
  return api.put(`/auth/departments/${id}/`, data);
};

export const patchDepartment = async (id, data) => {
  return api.patch(`/auth/departments/${id}/`, data);
};

export const deleteDepartment = async (id) => {
  return api.delete(`/auth/departments/${id}/`);
};

// =============== JOB TITLE APIs ===============

export const getJobTitles = async (departmentId = null) => {
  const params = departmentId ? { department: departmentId } : {};
  return api.get('/auth/job-titles/', { params });
};

export const getJobTitle = async (id) => {
  return api.get(`/auth/job-titles/${id}/`);
};

export const createJobTitle = async (data) => {
  return api.post('/auth/job-titles/', data);
};

export const updateJobTitle = async (id, data) => {
  return api.put(`/auth/job-titles/${id}/`, data);
};

export const patchJobTitle = async (id, data) => {
  return api.patch(`/auth/job-titles/${id}/`, data);
};

export const deleteJobTitle = async (id) => {
  return api.delete(`/auth/job-titles/${id}/`);
};
```

### React Component Example

```jsx
import { useState, useEffect } from 'react';
import { 
  getDepartments, 
  createDepartment,
  getJobTitles, 
  createJobTitle 
} from '../services/auth';
import toast from 'react-hot-toast';

export default function JobTitleManagement() {
  const [departments, setDepartments] = useState([]);
  const [jobTitles, setJobTitles] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    department_id: '',
  });

  useEffect(() => {
    loadDepartments();
    loadJobTitles();
  }, []);

  const loadDepartments = async () => {
    try {
      const res = await getDepartments();
      setDepartments(res.data.results || []);
    } catch (err) {
      console.error('Failed to load departments:', err);
      toast.error('Failed to load departments');
    }
  };

  const loadJobTitles = async (deptId = null) => {
    try {
      const res = await getJobTitles(deptId);
      setJobTitles(res.data.results || []);
    } catch (err) {
      console.error('Failed to load job titles:', err);
      toast.error('Failed to load job titles');
    }
  };

  const handleDepartmentFilter = (deptId) => {
    setSelectedDepartment(deptId);
    loadJobTitles(deptId || null);
  };

  const handleCreateJobTitle = async (e) => {
    e.preventDefault();
    try {
      await createJobTitle(formData);
      toast.success('Job title created successfully');
      loadJobTitles();
      setFormData({ title: '', description: '', department_id: '' });
    } catch (err) {
      console.error('Failed to create job title:', err);
      toast.error('Failed to create job title');
    }
  };

  return (
    <div>
      <h1>Job Title Management</h1>
      
      {/* Department Filter */}
      <select 
        value={selectedDepartment} 
        onChange={(e) => handleDepartmentFilter(e.target.value)}
      >
        <option value="">All Departments</option>
        {departments.map(dept => (
          <option key={dept.id} value={dept.id}>
            {dept.name}
          </option>
        ))}
      </select>

      {/* Create Job Title Form */}
      <form onSubmit={handleCreateJobTitle}>
        <input
          type="text"
          placeholder="Job Title"
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          required
        />
        <textarea
          placeholder="Description"
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
        />
        <select
          value={formData.department_id}
          onChange={(e) => setFormData({...formData, department_id: e.target.value})}
        >
          <option value="">Select Department (Optional)</option>
          {departments.map(dept => (
            <option key={dept.id} value={dept.id}>
              {dept.name}
            </option>
          ))}
        </select>
        <button type="submit">Create Job Title</button>
      </form>

      {/* Job Titles List */}
      <ul>
        {jobTitles.map(job => (
          <li key={job.id}>
            <strong>{job.title}</strong> - {job.department || 'No Department'}
            <p>{job.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## Python/Django Integration

### Using Django ORM

```python
from apps.accounts.models import Department, JobTitle, User

# Create a department
department = Department.objects.create(
    name="Engineering",
    description="Software Development and Engineering"
)

# Create a job title under that department
job_title = JobTitle.objects.create(
    title="Senior Software Engineer",
    description="Leads technical projects",
    department=department
)

# Assign job title to a user
user = User.objects.get(email="john@example.com")
user.job_title = job_title
user.department = department
user.save()

# Query job titles by department
sales_jobs = JobTitle.objects.filter(department__name="Sales")

# Get all departments with their job titles
departments_with_jobs = Department.objects.prefetch_related('job_titles').all()
for dept in departments_with_jobs:
    print(f"Department: {dept.name}")
    for job in dept.job_titles.all():
        print(f"  - {job.title}")
```

### Using Django REST Framework Views

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.models import Department, JobTitle
from apps.accounts.serializers import DepartmentSerializer, JobTitleSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_department_job_titles(request, department_id):
    """Get all job titles for a specific department"""
    try:
        department = Department.objects.get(id=department_id)
        job_titles = JobTitle.objects.filter(department=department)
        serializer = JobTitleSerializer(job_titles, many=True)
        return Response({
            'success': True,
            'data': {
                'department': DepartmentSerializer(department).data,
                'job_titles': serializer.data
            }
        })
    except Department.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Department not found'
        }, status=404)
```

---

## Common Use Cases

### 1. Create Department and Add Job Titles

```javascript
// Step 1: Create a department
const dept = await createDepartment({
  name: "Marketing",
  description: "Marketing and Brand Management"
});

const departmentId = dept.data.id;

// Step 2: Create multiple job titles under this department
const jobTitles = [
  { title: "Marketing Manager", department_id: departmentId },
  { title: "Content Strategist", department_id: departmentId },
  { title: "Social Media Specialist", department_id: departmentId }
];

for (const jobData of jobTitles) {
  await createJobTitle(jobData);
}
```

### 2. Move Job Title to Different Department

```javascript
// Move a job title from one department to another
await patchJobTitle('job-uuid-456', {
  department_id: 'new-dept-uuid-789'
});
```

### 3. Filter Users by Department and Job Title

```javascript
// Get all job titles in Sales department
const salesJobs = await getJobTitles('dept-uuid-sales');

// Then use these job titles to filter users
const users = await getUsers({
  department: 'dept-uuid-sales',
  job_title: salesJobs.data.results[0].id
});
```

### 4. Deactivate Department and Associated Job Titles

```javascript
// Deactivate a department (job titles remain but department is marked inactive)
await patchDepartment('dept-uuid-123', {
  is_active: false
});

// Optionally deactivate all job titles in that department
const deptJobTitles = await getJobTitles('dept-uuid-123');
for (const job of deptJobTitles.data.results) {
  await patchJobTitle(job.id, { is_active: false });
}
```

---

## Error Handling

### Common Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden (Non-admin trying to create/update/delete):**
```json
{
  "success": false,
  "status_code": 403,
  "message": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "success": false,
  "status_code": 404,
  "message": "Not found."
}
```

**400 Validation Error:**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Validation error",
  "errors": {
    "name": ["This field is required."],
    "department_id": ["Invalid pk \"invalid-uuid\" - object does not exist."]
  }
}
```

---

## Data Model Reference

### Department Model

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Auto-generated UUID |
| name | VARCHAR(150) | UNIQUE, NOT NULL | Department name |
| description | TEXT | NULLABLE | Department description |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | AUTO | Creation timestamp |
| updated_at | TIMESTAMP | AUTO | Last update timestamp |

### JobTitle Model

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Auto-generated UUID |
| title | VARCHAR(150) | NOT NULL | Job title name |
| description | TEXT | NULLABLE | Job title description |
| department_id | UUID | FK to Department, NULLABLE | Department reference |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | AUTO | Creation timestamp |
| updated_at | TIMESTAMP | AUTO | Last update timestamp |

**Unique Constraint:** `(department_id, title)` - A job title must be unique within a department.

### User-Department-JobTitle Relationship

```
User
├── department (FK to Department) - User's department
└── job_title (FK to JobTitle) - User's job title

Department
└── job_titles (Reverse FK) - All job titles in this department

JobTitle
├── department (FK to Department) - Job title's department
└── users (Reverse FK) - All users with this job title
```

---

## Best Practices

1. **Always Create Departments First**: Before creating job titles, ensure the department exists.

2. **Use UUIDs for References**: When referencing departments or job titles, always use their UUID values, not integer IDs.

3. **Filter Job Titles by Department**: Use the `department` query parameter to get job titles for a specific department.

4. **Handle Cascading Deletes**: Be cautious when deleting departments as it may affect associated job titles (depending on CASCADE settings).

5. **Validate Department Exists**: Before assigning a `department_id` to a job title or user, verify the department exists.

6. **Use Partial Updates**: Use PATCH instead of PUT when you only need to update specific fields.

7. **Check Permissions**: Only admin users can create, update, or delete departments and job titles.

---

## Security Notes

- All endpoints require JWT authentication
- Only users with `is_staff=True` or `role='ADMIN'`/`'SUPERADMIN'` can create, update, or delete
- Regular authenticated users can view departments and job titles
- UUIDs are used to prevent enumeration attacks

---

## Migration Notes

If you're migrating from the old system where `department` was a CharField:

1. The migration creates a `Department` model
2. Existing department string values are converted to Department objects
3. User and JobTitle models now reference Department via FK
4. The API returns both `department` (name string for backward compatibility) and `department_id` (UUID for FK references)

---

## Support

For issues or questions:
- Backend API Issues: Contact backend team
- Frontend Integration: Refer to frontend documentation
- Database Schema: See Django models in `apps/accounts/models.py`
