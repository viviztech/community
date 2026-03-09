# Free Tier Deployment Guide for ACTIV Membership Portal

This guide covers free deployment options for demo/purpose for the ACTIV Membership Portal.

## Option 1: Render.com (Recommended for Simplicity)

### Backend (Django)
1. Create a [Render.com](https://render.com) account (free tier)
2. Create a new Web Service:
   - GitHub repository: `https://github.com/viviztech/community`
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn activ_project.wsgi:application`
   - Environment variables:
     - `DJANGO_SETTINGS_MODULE=activ_project.settings`
     - `SECRET_KEY=your-secret-key`
     - `ALLOWED_HOSTS=*.onrender.com`
     - `DATABASE_URL=postgres://...` (Render provides PostgreSQL)

3. Create a PostgreSQL database (free tier) and link to the service

### Frontend (React)
1. Create a new Static Site on Render:
   - GitHub repository: `https://github.com/viviztech/community`
   - Root directory: `frontend`
   - Build command: `npm install && npm run build`
   - Publish directory: `frontend/build`

### Total Cost: $0/month (within free limits)

---

## Option 2: Railway.app (Easiest for Full-Stack)

### Steps:
1. Create a [Railway.app](https://railway.app) account
2. Connect GitHub repository
3. Add PostgreSQL plugin (free tier)
4. Deploy backend as a Python service
5. Deploy frontend (static site)

### Environment Variables (Railway):
```env
DJANGO_SETTINGS_MODULE=activ_project.settings
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=*.railway.app
DATABASE_URL=postgresql://user:pass@host:5432/db
DEBUG=True
```

### Total Cost: $0/month (with $5 credit/month free)

---

## Option 3: Fly.io (Edge Deployment)

### Steps:
1. Install [Fly CLI](https://fly.io/docs/flyctl/)
2. Run: `fly launch`
3. Select Django as the app type
4. Configure environment variables

### Total Cost: $0/month (includes shared CPU, 3GB volume)

---

## Option 4: Cyclic.sh (Full-Stack Node.js Wrapper)

Since Cyclic expects Node.js, wrap the Django backend:

1. Create `server.js` in root:
```javascript
const { spawn } = require('child_process');
const express = require('express');
const path = require('path');

const app = express();
app.use(express.static('frontend/build'));

// Proxy API requests to Django
app.use('/api', async (req, res) => {
  // Handle API proxying
});

const server = spawn('python', ['manage.py', 'runserver', '0.0.0.0:8000'], {
  cwd: './backend',
  stdio: 'inherit'
});

server.on('error', console.error);

app.listen(process.env.PORT || 3000);
```

### Total Cost: Free for hobby projects

---

## Option 5: Vercel + Railway (Hybrid)

### Frontend (Vercel - Free)
1. Connect GitHub repo to Vercel
2. Root directory: `frontend`
3. Build command: `npm run build`
4. Output directory: `build`
5. Environment: `REACT_APP_API_URL=https://your-railway-app.railway.app`

### Backend (Railway - Free)
1. Deploy Django to Railway with PostgreSQL
2. Configure CORS to allow Vercel frontend domain

### Total Cost: $0/month

---

## Database Options (Free Tier)

| Service | Free Tier | Type |
|---------|-----------|------|
| **Supabase** | 500MB DB + API | PostgreSQL |
| **Neon** | 10 branches, 10GB storage | PostgreSQL |
| **Render PostgreSQL** | 90 days, then $7/mo | PostgreSQL |
| **ElephantSQL** | 20MB (tiny) | PostgreSQL |

**Recommendation**: Use Supabase for free PostgreSQL with generous limits.

---

## Quick Start: Render + Supabase

### 1. Setup Supabase Database
1. Create free [Supabase](https://supabase.com) project
2. Get connection string from Settings → Database
3. Run migrations on Supabase SQL editor

### 2. Deploy Backend to Render
```bash
# Render configuration
Repository: https://github.com/viviztech/community
Root Directory: backend
Build: pip install -r requirements.txt
Start: gunicorn activ_project.wsgi:application
Env Vars:
  - DJANGO_SETTINGS_MODULE=activ_project.settings
  - SECRET_KEY=your-secret-key
  - ALLOWED_HOSTS=*.onrender.com
  - DATABASE_URL=postgresql://...
  - CORS_ALLOWED_ORIGINS=https://*.vercel.app
```

### 3. Deploy Frontend to Vercel
```bash
# Vercel configuration
Repository: https://github.com/viviztech/community
Root Directory: frontend
Build: npm run build
Output: build
Env Vars:
  - REACT_APP_API_URL=https://your-render-app.onrender.com
```

---

## Testing Credentials

After deployment, use:
- **Super Admin**: `admin@activ.org.in` / `Admin@123`
- **API Base URL**: `https://your-render-app.onrender.com/api/v1/`
- **Login**: `POST /api/v1/auth/login/`

---

## Environment Template

Create `.env.example` for deployment:

```env
# Required
DJANGO_SECRET_KEY=your-secure-random-key
DJANGO_SETTINGS_MODULE=activ_project.settings

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# CORS
ALLOWED_HOSTS=localhost,127.0.0.1,*.onrender.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://*.vercel.app

# Twilio (Optional - for SMS)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## Monitoring & Logs

- **Render**: Dashboard → Your Service → Logs
- **Vercel**: Dashboard → Your Project → Function Logs
- **Supabase**: Dashboard → Logs Explorer

---

## Performance Tips (Free Tier)

1. **Enable caching**: Use Redis (Render free tier available)
2. **Compress assets**: Configure WhiteNoise for static files
3. **Database indexing**: Add indexes for frequently queried fields
4. **Connection pooling**: Use `django-db-connections` or pgbouncer

---

## Estimated Monthly Costs (Free Tier)

| Component | Free Limit | Cost |
|-----------|------------|------|
| Render Web Service | 750 hours/month | $0 |
| Supabase Database | 500MB | $0 |
| Vercel Frontend | 100GB bandwidth | $0 |
| Domain (optional) | .tk, .ml free | $0 |
| **Total** | | **$0** |
