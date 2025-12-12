# Organization Management Service

A multi-tenant organization management system built with FastAPI and MongoDB. This service provides REST APIs for creating and managing organizations with secure authentication and dynamic data isolation.

Deployed at : https://organization-management-service-ngc.vercel.app/docs

## Key Features

### Core Functionality
- Multi-tenant architecture with dynamic MongoDB collections
- JWT-based authentication with bcrypt password hashing
- Complete CRUD operations for organization management
- Input validation and comprehensive error handling
- Interactive API documentation with Swagger UI
- Health monitoring and system statistics
- Audit logging for all operations
- Rate limiting and CORS support

### Advanced Capabilities
- **True Data Isolation**: Each organization gets its own MongoDB collection, ensuring complete data separation
- **Intelligent Data Migration**: Automatic data migration when organizations are updated, with zero downtime
- **Production-Ready Security**: Multi-layer security middleware with rate limiting, CORS, and security headers
- **Comprehensive Analytics**: Real-time dashboard metrics and system-wide statistics
- **Enterprise Error Handling**: Detailed error responses with proper HTTP status codes and rollback mechanisms
- **Conflict Resolution**: Advanced upsert operations to handle duplicate key scenarios gracefully
- **Scalable Architecture**: Microservices-ready design with clean separation of concerns

## What Makes This Project Stand Out

### Technical Excellence
- **Dynamic Collection Management**: Unlike typical multi-tenant systems that use shared tables with tenant IDs, this system creates dedicated MongoDB collections for each organization, providing true data isolation and improved performance.

- **Intelligent Migration System**: When organizations update their names, the system automatically migrates data from the old collection to a new one, preserving data integrity and ensuring zero downtime.

- **Advanced Security Stack**: Implements enterprise-grade security with JWT token management, bcrypt password hashing, request rate limiting, CORS configuration, and comprehensive audit logging.

- **Professional Error Handling**: Every endpoint includes detailed error responses, input validation with specific feedback, and graceful failure handling with automatic rollback capabilities.

### Production Readiness
- **Comprehensive Testing Suite**: Multiple testing approaches including integration tests, workflow verification, and error scenario testing
- **Monitoring and Observability**: Built-in health checks, system statistics, and performance monitoring
- **Flexible Configuration**: Environment-based configuration management with secure credential handling
- **Docker Integration**: Production-ready containerization with Docker Compose support

### Developer Experience
- **Interactive Documentation**: Custom-styled Swagger UI with comprehensive endpoint documentation and real-world examples
- **Cross-Platform Support**: Detailed setup instructions for both macOS and Windows environments
- **Modular Architecture**: Clean code organization with separation of concerns, making it easy to extend and maintain
- **Automated Verification**: Scripts to verify system functionality and test all features automatically

## Technology Stack

- Backend: FastAPI (Python 3.8+)
- Database: MongoDB
- Authentication: JWT tokens with bcrypt
- Documentation: Swagger/OpenAPI
- Validation: Pydantic models
- Testing: Pytest
- Containerization: Docker

## Prerequisites

### System Requirements
- Python 3.8 or higher
- MongoDB 4.4 or higher
- Git

### For macOS Users
```bash
# Install Python (if not already installed)
brew install python

# Install MongoDB
brew tap mongodb/brew
brew install mongodb-community
```

### For Windows Users
1. Download and install Python from https://python.org/downloads/
2. Download and install MongoDB from https://www.mongodb.com/try/download/community
3. Install Git from https://git-scm.com/download/win

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/MruganKulkarni/OrganizationManagement-Service.git
cd OrganizationManagement-Service
```

### Step 2: Create Virtual Environment

**For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=org_master_db
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRE_MINUTES=30
ENVIRONMENT=development
```

### Step 5: Start MongoDB

**For macOS:**
```bash
# If installed via Homebrew:
brew services start mongodb-community

# If installed manually or brew command doesn't work:
mongod

# Alternative: specify data directory
mongod --dbpath /usr/local/var/mongodb
```

**For Windows:**
```bash
# Start MongoDB service from Services panel or command line
net start MongoDB

# Alternative: run MongoDB directly
mongod
```

**Using Docker (All platforms):**
```bash
docker run -d --name mongodb -p 27017:27017 mongo:6.0
```

**Note:** If `brew services start mongodb-community` doesn't work, it likely means MongoDB wasn't installed via Homebrew. Use the `mongod` command instead.

### Step 6: Run the Application

**For macOS/Linux:**
```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**For Windows:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Access the Application
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- API Info: http://localhost:8000/info

## API Endpoints

### Organization Management
- `POST /org/create` - Create new organization
- `GET /org/get` - Retrieve organization details
- `PUT /org/update` - Update organization
- `DELETE /org/delete` - Delete organization
- `GET /org/stats` - Get system statistics

### Authentication
- `POST /admin/login` - Admin login
- `GET /admin/profile` - Get admin profile
- `POST /admin/logout` - Admin logout

### Health Monitoring
- `GET /health` - System health status
- `GET /ping` - Basic connectivity test
- `GET /version` - API version information

## Usage Guide

### Testing with Swagger UI

1. Open http://localhost:8000/docs in your browser
2. Test the health endpoint first: `GET /health`
3. Create an organization using `POST /org/create`:
   ```json
   {
     "organization_name": "mycompany",
     "email": "admin@mycompany.com",
     "password": "SecurePass123!"
   }
   ```
4. Login using `POST /admin/login` with the same credentials
5. Copy the access token from the response
6. Click "Authorize" button and enter: `Bearer YOUR_ACCESS_TOKEN`
7. Test protected endpoints like `GET /admin/profile`

### Command Line Examples

**Create Organization:**
```bash
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "testcompany",
    "email": "admin@testcompany.com",
    "password": "SecurePass123!"
  }'
```

**Admin Login:**
```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@testcompany.com",
    "password": "SecurePass123!"
  }'
```

**Get Organization:**
```bash
curl -X GET "http://localhost:8000/org/get?organization_name=testcompany"
```

## Testing

### Automated Tests
```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Run integration tests
python test_integration.py

# Run comprehensive tests
python test_comprehensive.py

# Run verification tests
python test_complete_verification.py
```

### Manual Testing
Use the Swagger UI at http://localhost:8000/docs for interactive testing of all endpoints.

## Docker Deployment

### Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Building Docker Image
```bash
# Build the image
docker build -t org-management-service .

# Run the container
docker run -d -p 8000:8000 --name org-service org-management-service
```

## Configuration Options

### Environment Variables
- `MONGODB_URL`: MongoDB connection string (default: mongodb://localhost:27017)
- `DATABASE_NAME`: Database name (default: org_master_db)
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `JWT_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `ENVIRONMENT`: Application environment (development/production)
- `LOG_LEVEL`: Logging level (default: INFO)

### Security Settings
- JWT tokens expire in 30 minutes
- Passwords require uppercase, lowercase, numbers, and special characters
- Rate limiting: 100 requests per minute per IP
- CORS enabled for specified origins

## Architecture Highlights

### Database Design
The system implements a sophisticated multi-tenant architecture:
- **Master Database**: Stores organization metadata, admin users, and audit logs
- **Dynamic Collections**: Each organization gets a dedicated collection (e.g., `org_companyname`)
- **Automatic Indexing**: Collections are automatically optimized with proper indexing
- **Conflict Resolution**: Uses upsert operations to handle concurrent access and prevent duplicate key errors

### Security Implementation
- **JWT Token Management**: Secure token generation with configurable expiration
- **Password Security**: bcrypt hashing with strength validation and detailed feedback
- **Request Security**: Rate limiting (100 requests/minute), CORS configuration, and security headers
- **Audit Trail**: Complete logging of all operations for compliance and monitoring

### Performance Optimization
- **Connection Pooling**: Efficient MongoDB connection management
- **Lazy Loading**: Resources are created only when needed
- **Caching Strategy**: Optimized data retrieval with proper caching mechanisms
- **Scalable Design**: Microservices-ready architecture for horizontal scaling

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── database.py          # MongoDB connection and operations
├── auth.py              # Authentication and JWT handling
├── models.py            # Pydantic data models
├── services.py          # Business logic layer
├── middleware.py        # Custom middleware components
├── utils.py             # Utility functions
└── routers/
    ├── organizations.py # Organization CRUD endpoints
    ├── auth.py          # Authentication endpoints
    ├── health.py        # Health monitoring endpoints
    └── analytics.py     # Analytics and statistics
```

## Technical Implementation Details

### Multi-Tenant Collection Strategy
```python
# Dynamic collection creation with conflict resolution
def create_organization_collection(self, org_name: str):
    collection_name = f"org_{org_name.lower()}"
    collection = self.get_master_db()[collection_name]
    
    # Use upsert to prevent duplicate key errors
    collection.update_one(
        {"_id": "metadata"},
        {"$set": metadata},
        upsert=True
    )
```

### Advanced Authentication Flow
```python
# JWT token validation with proper error handling
def get_current_admin(credentials: HTTPAuthorizationCredentials):
    payload = verify_token(credentials.credentials)
    admin_user = admin_collection.find_one({
        "_id": ObjectId(payload["admin_id"]),
        "is_active": True
    })
    return admin_user
```

### Comprehensive Audit Logging
```python
# Every operation is tracked for compliance
AuditService.log_action(
    action="organization_created",
    organization_name=org_name,
    admin_email=email,
    ip_address=request.client.host,
    details={"collection_name": collection_name}
)
```

## Troubleshooting

### Common Issues

**MongoDB Connection Error:**
- Ensure MongoDB is running
- Check connection string in .env file
- Verify MongoDB port (default: 27017)

**Port Already in Use:**
- Change port in uvicorn command: `--port 8001`
- Kill existing process: `lsof -ti:8000 | xargs kill -9`

**Import Errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Authentication Issues:**
- Check JWT secret key in .env file
- Ensure token is properly formatted: `Bearer <token>`
- Verify token hasn't expired (30 minutes default)

### Platform-Specific Notes

**macOS:**
- Use `python3` instead of `python` if both versions are installed
- MongoDB service: `brew services start/stop mongodb-community`

**Windows:**
- Use `python` command (usually works after proper installation)
- MongoDB service: Use Services panel or `net start MongoDB`
- Path separators: Use backslashes in Windows paths

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit changes: `git commit -m "Description of changes"`
5. Push to branch: `git push origin feature-name`
6. Create a Pull Request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the interactive API documentation at /docs
- Review the test files for usage examples
