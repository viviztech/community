# ACTIV Membership Portal

A full-stack membership management system built with Django (Backend) and React (Frontend), designed for managing community memberships, events, payments, and approvals.

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Nginx     │────▶│   Backend   │
│   (React)   │     │ (Proxy)     │     │  (Django)   │
└─────────────┘     └─────────────┘     └─────────────┘
                                                  │
                    ┌─────────────┐               │
                    │    Redis    │◀──────────────┤
                    │  (Cache)    │               │
                    └─────────────┘               ▼
                                      ┌─────────────────────┐
                    ┌─────────────┐   │   PostgreSQL DB     │
                    │   Celery    │──▶│   (Primary Data)    │
                    │  (Workers)  │   └─────────────────────┘
                    └─────────────┘
```

## ✨ Features

- **User Authentication** - JWT + Social Login (Google, Facebook)
- **Member Management** - Registration, profiles, search
- **Membership Tiers** - Multiple membership levels with payments
- **Approval Workflow** - Multi-level approval system
- **Event Management** - Create and manage community events
- **Payment Integration** - Secure payment processing
- **Notifications** - Email, SMS, WhatsApp notifications
- **AI Services** - Smart recommendations and analytics
- **Admin Dashboard** - Full control panel

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm start
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api-docs

## 🐳 Docker Deployment (Recommended)

### Development

```bash
docker-compose up --build
```

### Production (AWS EC2)

#### 1. Launch EC2 Instance

- Instance Type: t3.medium or larger
- OS: Ubuntu 22.04 LTS
- Storage: 30+ GB SSD

#### 2. Install Docker

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and back in
```

#### 3. Deploy

```bash
# Clone the repository
git clone https://github.com/viviztech/community.git
cd community

# Copy environment template
cp .env.production.example .env

# Edit .env with your settings
nano .env

# Build and start containers
docker-compose up -d --build
```

#### 4. Environment Variables

Edit `.env` file:

```env
# Required
SECRET_KEY=your-super-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure-password
POSTGRES_DB=activ

# Frontend
REACT_APP_API_URL=https://your-domain.com/api/v1
```

## ☁️ Cloud Deployment Options

| Platform | Backend | Database | Frontend | Cost |
|----------|---------|----------|----------|------|
| **AWS EC2** | ✅ Docker | ✅ Docker | ✅ Docker | ~$25/mo |
| **Render** | ✅ | ✅ PostgreSQL | ✅ Static | Free |
| **Railway** | ✅ | ✅ PostgreSQL | ✅ Static | Free |
| **Vercel** | ❌ | ❌ | ✅ Static | Free |
| **Fly.io** | ✅ | ✅ | ✅ | Free |

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guides.

## 📁 Project Structure

```
community/
├── backend/                 # Django backend
│   ├── activ_project/       # Django project settings
│   ├── apps/                # Django apps
│   │   ├── accounts/        # User authentication
│   │   ├── members/         # Member management
│   │   ├── memberships/     # Membership tiers
│   │   ├── approvals/       # Approval workflow
│   │   ├── events/          # Event management
│   │   ├── payments/        # Payment processing
│   │   ├── notifications/   # Notification system
│   │   └── ai_services/     # AI/ML features
│   ├── manage.py
│   └── requirements.txt
├── frontend/                # React frontend
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── components/     # Reusable components
│   │   └── store/          # Redux store
│   └── package.json
├── docker-compose.yml       # Docker orchestration
├── nginx.conf              # Nginx configuration
└── README.md
```

## 🔧 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/v1/auth/login/` | User login |
| `/api/v1/auth/register/` | User registration |
| `/api/v1/members/` | Member list |
| `/api/v1/memberships/` | Membership tiers |
| `/api/v1/events/` | Events |
| `/api/v1/payments/` | Payments |
| `/api/v1/approvals/` | Approvals |

Full API documentation available at `/api-docs/` when running.

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest --cov

# Frontend tests
cd frontend
npm test
```

## 🔐 Default Credentials

After initial setup:

- **Email**: admin@activ.org.in
- **Password**: Admin@123

## 📄 License

Proprietary - All rights reserved

## 🆘 Support

- Email: support@activ.org.in
- Documentation: https://docs.activ.org.in
