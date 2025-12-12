# 🚀 Quick Start Guide

Get the Organization Management Service running in under 5 minutes!

## 📋 Prerequisites

- Python 3.9+
- MongoDB 4.4+ (or MongoDB Atlas)
- Git

## ⚡ Quick Setup

### 1. Clone and Setup
```bash
git clone <your-repository-url>
cd OrganizationManagement-Service
```

### 2. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your MongoDB URL (default works for local MongoDB)
# MONGODB_URL=mongodb://localhost:27017
```

### 4. Start MongoDB
```bash
# Option 1: Local MongoDB
mongod

# Option 2: Docker MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:6.0
```

### 5. Run the Application
```bash
uvicorn app.main:app --reload
```

### 6. Test the API
```bash
# Run integration tests
python test_integration.py

# Open API documentation
open http://localhost:8000/docs
```

## 🎯 Quick API Test

### Create Organization
```bash
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "test_org",
    "email": "admin@test.com",
    "password": "TestPass123!"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "TestPass123!"
  }'
```

### Access Dashboard (use token from login)
```bash
curl -X GET "http://localhost:8000/analytics/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🐳 Docker Quick Start

```bash
# Start with Docker Compose
docker-compose up --build

# API will be available at http://localhost:8000
```

## 📚 Next Steps

- Visit http://localhost:8000/docs for interactive API documentation
- Check out `docs/API_EXAMPLES.md` for comprehensive usage examples
- Review `DEPLOYMENT_CHECKLIST.md` for production deployment
- Explore `FEATURES_SHOWCASE.md` to see all advanced features

## 🆘 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   ```bash
   # Check if MongoDB is running
   mongod --version
   
   # Start MongoDB
   mongod
   ```

2. **Port Already in Use**
   ```bash
   # Use different port
   uvicorn app.main:app --port 8001
   ```

3. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 🎉 Success!

If everything is working, you should see:
- ✅ All integration tests passing
- ✅ API documentation at http://localhost:8000/docs
- ✅ Health check at http://localhost:8000/health returns "healthy"

**You're ready to build amazing multi-tenant applications!** 🚀