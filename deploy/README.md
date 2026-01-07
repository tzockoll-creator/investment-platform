# Deployment Guide

This directory contains deployment configurations for various cloud providers.

## Quick Start with Docker Compose

### Development
```bash
docker-compose up -d
```

### Production
```bash
# Set environment variables
export DOCKER_USERNAME=your-dockerhub-username
export DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Deploy
docker-compose -f deploy/docker-compose.prod.yml up -d
```

## Cloud Deployment Options

### AWS ECS/Fargate

1. **Setup**:
   ```bash
   # Install AWS CLI
   aws configure
   ```

2. **Create ECR repositories**:
   ```bash
   aws ecr create-repository --repository-name investment-platform-backend
   aws ecr create-repository --repository-name investment-platform-frontend
   ```

3. **Push images**:
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Tag and push
   docker tag investment-platform-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/investment-platform-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/investment-platform-backend:latest
   ```

4. **Deploy**:
   ```bash
   # Register task definition
   aws ecs register-task-definition --cli-input-json file://deploy/aws-ecs-task-definition.json

   # Create/update service
   aws ecs create-service --cluster my-cluster --service-name investment-platform --task-definition investment-platform --desired-count 1
   ```

### Google Cloud Platform (Cloud Run)

1. **Setup**:
   ```bash
   gcloud init
   gcloud auth configure-docker
   ```

2. **Deploy backend**:
   ```bash
   gcloud run deploy investment-platform-backend \
     --image gcr.io/PROJECT_ID/investment-platform-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Deploy frontend**:
   ```bash
   gcloud run deploy investment-platform-frontend \
     --image gcr.io/PROJECT_ID/investment-platform-frontend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Azure Container Instances

1. **Setup**:
   ```bash
   az login
   az acr create --resource-group myResourceGroup --name myRegistry --sku Basic
   ```

2. **Deploy**:
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name investment-platform \
     --image myregistry.azurecr.io/investment-platform:latest \
     --cpu 1 --memory 1 \
     --registry-login-server myregistry.azurecr.io \
     --registry-username <username> \
     --registry-password <password> \
     --dns-name-label investment-platform \
     --ports 80 8000
   ```

### DigitalOcean App Platform

1. Create a new app via the DigitalOcean dashboard
2. Connect your GitHub repository
3. Configure build settings:
   - Backend: Dockerfile at `/backend/Dockerfile`
   - Frontend: Dockerfile at `/frontend/Dockerfile`
4. Set environment variables
5. Deploy

## Environment Variables

### Backend
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)
- `PORT`: API port (default: 8000)

### Frontend
- API endpoint is proxied through nginx configuration

## Health Checks

Both services include health check endpoints:
- Backend: `http://localhost:8000/`
- Frontend: `http://localhost:3000/` (or `:80` in production)

## Monitoring

Consider adding:
- Application Performance Monitoring (APM) tools like Datadog, New Relic
- Log aggregation with ELK stack or CloudWatch
- Uptime monitoring with Pingdom, UptimeRobot

## Security

For production deployments:
1. Use HTTPS with SSL/TLS certificates (Let's Encrypt)
2. Set up environment variables for secrets
3. Configure CORS properly in backend
4. Use a production database (PostgreSQL recommended)
5. Implement rate limiting
6. Set up firewall rules
7. Regular security updates

## Scaling

- **Horizontal scaling**: Increase number of container instances
- **Vertical scaling**: Increase CPU/memory per container
- **Database**: Migrate to managed PostgreSQL for better performance
- **Caching**: Add Redis for session/data caching
- **CDN**: Use CloudFront, CloudFlare for static assets

## Backup & Recovery

1. Database backups:
   ```bash
   # Backup
   docker exec investment-platform-backend python -c "import sqlite3; conn = sqlite3.connect('portfolio.db'); conn.backup(open('backup.db', 'wb'))"

   # Restore
   docker cp backup.db investment-platform-backend:/app/portfolio.db
   ```

2. Volume backups:
   ```bash
   docker run --rm -v backend-data:/data -v $(pwd):/backup ubuntu tar czf /backup/backend-data-backup.tar.gz /data
   ```
