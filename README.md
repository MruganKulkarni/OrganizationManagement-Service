# Organization Management Service

A multi-tenant organization management system built with FastAPI and MongoDB. This service handles organization lifecycle management with dynamic database collections and secure authentication.

## Overview

This project implements a complete backend service for managing organizations in a multi-tenant architecture. Each organization gets its own dedicated MongoDB collection, and the system maintains a master database for global metadata and user management.

## Key Features

- Dynamic MongoDB collection creation for each organization
- JWT-based authentication with bcrypt password hashing
- Automatic data migration when organizations are updated
- Real-time analytics and monitoring dashboard
- Comprehensive audit logging
- Production-ready Docker configuration
- Complete API documentation with Swagger UI

## Technology Stack

- **Backend Framework**: FastAPI (Python 3.9+)
- **Database**: MongoDB with dynamic collections
- **Authentication**: JWT tokens with bcrypt hashing
- **Validation**: Pydantic models
- **Documentation**: OpenAPI/Swagger auto-generation
- **Deployment**: Docker and Docker Compose

## API Endpoints

### Organization Management
- `POST /org/create` - Create new organization
- `GET /org/get` - Get organization details
- `PUT /org/update` - Update organization with data migration
- `DELETE /org/delete` - Delete organization and cleanup data

### Authentication
- `POST /admin/login` - Admin login with JWT token response

### Analytics & Monitoring
- `GET /analytics/dashboard` - Organization dashboard metrics
- `GET /analytics/system` - System-wide statistics
- `GET /health` - Health check endpoint

## Getting Started

### Prerequisites
- Python 3.9 or higher
- MongoDB 4.4 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/MruganKulkarni/OrganizationManagement-Service.git
cd OrganizationManagement-Service
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment configuration:
```bash
cp .env.example .env
# Edit .env file with your MongoDB connection string
```

5. Start the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### Docker Setup

For containerized deployment:

```bash
docker-compose up --build
```

## Configuration

The application uses environment variables for configuration. Key settings include:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=org_master_db
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRE_MINUTES=30
ENVIRONMENT=development
```

## Database Architecture

The system uses a master database approach:

- **Master Database**: Stores organization metadata, admin users, and audit logs
- **Dynamic Collections**: Each organization gets a dedicated collection (`org_organizationname`)
- **Automatic Migration**: Data is automatically migrated when organization names change

## Testing

Run the test suite:

```bash
# Integration tests
python test_integration.py

# Full API workflow tests
python test_comprehensive.py
```

## Example Usage

Create an organization:
```bash
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "my_company",
    "email": "admin@mycompany.com",
    "password": "SecurePassword123!"
  }'
```

Login as admin:
```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@mycompany.com",
    "password": "SecurePassword123!"
  }'
```

## Documentation

- `docs/API_EXAMPLES.md` - Comprehensive API usage examples
- `docs/DEPLOYMENT.md` - Production deployment guide
- `DEPLOYMENT_CHECKLIST.md` - Production readiness checklist
- `QUICK_START.md` - Quick setup guide

## Security Features

- Password strength validation with detailed feedback
- JWT token authentication with configurable expiration
- Request rate limiting and security headers
- Input validation and sanitization
- Complete audit trail logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.