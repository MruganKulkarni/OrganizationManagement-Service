# 🏢 Organization Management Service

A modern, scalable multi-tenant organization management system built with FastAPI and MongoDB. This service provides dynamic collection creation, secure authentication, and comprehensive organization lifecycle management.

## ✨ What Makes This Special

- **Dynamic Multi-Tenancy**: Automatically creates dedicated MongoDB collections for each organization
- **Smart Data Migration**: Seamless organization updates with automatic data synchronization
- **Advanced Security**: JWT authentication with bcrypt password hashing and role-based access
- **Real-time Monitoring**: Built-in health checks and organization metrics
- **Developer-Friendly**: Comprehensive API documentation with Swagger UI
- **Production-Ready**: Docker support, environment configuration, and logging

## 🚀 Features

### Core Functionality
- ✅ Create organizations with dynamic collection provisioning
- ✅ Secure admin authentication with JWT tokens
- ✅ Organization CRUD operations with validation
- ✅ Automatic data migration during updates
- ✅ Role-based access control

### Standout Features
- 🔍 **Organization Analytics**: Track creation dates, user counts, and activity
- 📊 **Health Monitoring**: Real-time system health and database connectivity
- 🔐 **Enhanced Security**: Password strength validation and secure token management
- 📝 **Audit Logging**: Complete audit trail for all organization operations
- 🎯 **Smart Validation**: Intelligent organization name validation and sanitization
- 🔄 **Graceful Updates**: Zero-downtime organization updates with data preservation

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.9+)
- **Database**: MongoDB with dynamic collections
- **Authentication**: JWT with bcrypt password hashing
- **Validation**: Pydantic models with custom validators
- **Documentation**: Auto-generated OpenAPI/Swagger
- **Containerization**: Docker & Docker Compose

## 📋 API Endpoints

### Organization Management
- `POST /org/create` - Create new organization
- `GET /org/get` - Retrieve organization details
- `PUT /org/update` - Update organization (with data migration)
- `DELETE /org/delete` - Delete organization and cleanup

### Authentication
- `POST /admin/login` - Admin authentication with JWT

### Monitoring
- `GET /health` - System health check
- `GET /org/stats` - Organization statistics

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.9+
- MongoDB 4.4+
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/OrganizationManagement-Service.git
   cd OrganizationManagement-Service
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB connection details
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

### Using Docker

```bash
docker-compose up --build
```

## 📖 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuration

Create a `.env` file with the following variables:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=org_master_db
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 🏗️ Architecture

### Master Database Structure
```
org_master_db/
├── organizations/          # Organization metadata
├── admin_users/           # Admin user credentials
└── audit_logs/           # System audit trail
```

### Dynamic Collections
Each organization gets its own collection: `org_{organization_name}`

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📊 Example Usage

### Create Organization
```bash
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "acme_corp",
    "email": "admin@acme.com",
    "password": "SecurePass123!"
  }'
```

### Admin Login
```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acme.com",
    "password": "SecurePass123!"
  }'
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- MongoDB for flexible document storage
- The Python community for excellent libraries

---

**Built with ❤️ for scalable multi-tenant applications**