# 🚀 Deployment Guide

This guide covers various deployment options for the Organization Management Service.

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Monitoring & Logging](#monitoring--logging)

## 💻 Local Development

### Prerequisites

- Python 3.9+
- MongoDB 4.4+
- Git

### Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd OrganizationManagement-Service
   chmod +x scripts/start.sh
   ./scripts/start.sh
   ```

2. **Manual setup:**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your settings
   
   # Start MongoDB (if not running)
   mongod --dbpath /path/to/your/db
   
   # Run the application
   uvicorn app.main:app --reload
   ```

3. **Access the application:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Start services:**
   ```bash
   docker-compose up --build
   ```

2. **Run in background:**
   ```bash
   docker-compose up -d --build
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f app
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

### Using Docker Only

1. **Build the image:**
   ```bash
   docker build -t org-management-service .
   ```

2. **Run with external MongoDB:**
   ```bash
   docker run -d \
     --name org-service \
     -p 8000:8000 \
     -e MONGODB_URL=mongodb://your-mongo-host:27017 \
     -e JWT_SECRET_KEY=your-secret-key \
     org-management-service
   ```

## 🌐 Production Deployment

### AWS Deployment

#### Using AWS ECS with Fargate

1. **Create ECR repository:**
   ```bash
   aws ecr create-repository --repository-name org-management-service
   ```

2. **Build and push image:**
   ```bash
   # Get login token
   aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com
   
   # Build and tag
   docker build -t org-management-service .
   docker tag org-management-service:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/org-management-service:latest
   
   # Push
   docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/org-management-service:latest
   ```

3. **Create ECS task definition:**
   ```json
   {
     "family": "org-management-service",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "org-service",
         "image": "<account-id>.dkr.ecr.us-west-2.amazonaws.com/org-management-service:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "MONGODB_URL",
             "value": "mongodb://your-atlas-cluster"
           },
           {
             "name": "JWT_SECRET_KEY",
             "value": "your-production-secret"
           },
           {
             "name": "ENVIRONMENT",
             "value": "production"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/org-management-service",
             "awslogs-region": "us-west-2",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

#### Using MongoDB Atlas

1. **Create MongoDB Atlas cluster**
2. **Get connection string**
3. **Update environment variables:**
   ```bash
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/org_master_db?retryWrites=true&w=majority
   ```

### Google Cloud Platform

#### Using Cloud Run

1. **Build and push to Container Registry:**
   ```bash
   # Configure Docker for GCP
   gcloud auth configure-docker
   
   # Build and tag
   docker build -t gcr.io/your-project-id/org-management-service .
   
   # Push
   docker push gcr.io/your-project-id/org-management-service
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy org-management-service \
     --image gcr.io/your-project-id/org-management-service \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars MONGODB_URL=your-mongo-url,JWT_SECRET_KEY=your-secret
   ```

### DigitalOcean App Platform

1. **Create `app.yaml`:**
   ```yaml
   name: org-management-service
   services:
   - name: api
     source_dir: /
     github:
       repo: your-username/OrganizationManagement-Service
       branch: main
     run_command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     envs:
     - key: MONGODB_URL
       value: your-mongodb-url
     - key: JWT_SECRET_KEY
       value: your-secret-key
     - key: ENVIRONMENT
       value: production
     http_port: 8000
   ```

2. **Deploy:**
   ```bash
   doctl apps create --spec app.yaml
   ```

## ⚙️ Environment Configuration

### Production Environment Variables

```bash
# Database
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/org_master_db
DATABASE_NAME=org_master_db

# Security
JWT_SECRET_KEY=your-super-secure-production-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=["https://yourdomain.com","https://app.yourdomain.com"]

# Optional: Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Security Considerations

1. **JWT Secret Key:**
   - Use a strong, random key (minimum 32 characters)
   - Store in environment variables or secret management service
   - Rotate regularly

2. **MongoDB Security:**
   - Use MongoDB Atlas or secure self-hosted instance
   - Enable authentication and authorization
   - Use connection string with credentials
   - Enable SSL/TLS

3. **CORS Configuration:**
   - Specify exact origins in production
   - Avoid using wildcards (`*`)

4. **HTTPS:**
   - Always use HTTPS in production
   - Configure SSL certificates
   - Use reverse proxy (nginx, CloudFlare)

### Reverse Proxy Configuration (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

## 📊 Monitoring & Logging

### Health Checks

The service provides several health check endpoints:

- `/health` - Comprehensive health status
- `/ping` - Basic connectivity test
- `/version` - Version information

### Logging Configuration

```python
# In production, configure structured logging
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_entry)

# Configure logger
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

### Monitoring with Prometheus

Add metrics endpoint:

```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Log Aggregation

For production deployments, consider:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Fluentd** with cloud logging services
- **AWS CloudWatch** for AWS deployments
- **Google Cloud Logging** for GCP deployments

### Performance Monitoring

1. **Application Performance Monitoring (APM):**
   - New Relic
   - DataDog
   - Sentry

2. **Database Monitoring:**
   - MongoDB Atlas monitoring
   - Custom MongoDB metrics

3. **Infrastructure Monitoring:**
   - Prometheus + Grafana
   - Cloud provider monitoring tools

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to production
      run: |
        # Add your deployment commands here
        echo "Deploying to production..."
```

This deployment guide provides comprehensive instructions for deploying the Organization Management Service in various environments, from local development to production cloud platforms.