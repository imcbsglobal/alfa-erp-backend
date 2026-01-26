# Deployment Update - December 27, 2025

### Frontend Changes (alfa-erp-frontend)

### 1. Backend Deployment

```bash
# SSH into the server
ssh root@88.222.212.14

# Navigate to backend directory
cd /var/www/alfa-erp-backend/

# Pull latest changes from repository
git pull

# Restart Gunicorn service to apply changes
sudo systemctl restart gunicorn-alfa.service
```

**Results:**
- Successfully pulled X objects
- Updated from commit `fd59123` to `4f77f79`
- 61 files changed: 1,439 insertions(+), 757 deletions(-)
- Service restarted successfully



### 2. Frontend Deployment

```bash
# Navigate to frontend directory
cd /var/www/alfa-erp-frontend/

# Pull latest changes
git pull

# Build production bundle
npm run build
```

**Results:**
- Successfully pulled 37 objects
- Updated from commit `1fc3f9b` to `49a12dd`
- 13 files changed: 1,944 insertions(+), 150 deletions(-)
- Build completed in 5.06s
- Bundle sizes:
  - CSS: 43.00 kB (gzipped: 7.43 kB)
  - JS: 706.78 kB (gzipped: 178.51 kB)


### 1. Backend Deployment - for production

```bash
# SSH into the server
ssh root@88.222.212.14

# Navigate to backend directory
cd /var/www/alfa-erp-backend-prod/

# Pull latest changes from repository
git pull

# Restart Gunicorn service to apply changes
sudo systemctl restart gunicorn-alfa-prod