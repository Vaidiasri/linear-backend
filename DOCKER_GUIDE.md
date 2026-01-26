# 🚀 Docker Deployment Guide - Linear Backend Clone

## Quick Start (3 Steps)

### Step 1: Setup Environment

```bash
# Copy environment template
cp .env.docker .env

# Edit .env and change these values:
# - POSTGRES_PASSWORD (use a strong password)
# - SECRET_KEY (generate with: openssl rand -hex 32)
```

### Step 2: Start Services

```bash
docker-compose up -d
```

### Step 3: Verify

```bash
# Check containers are running
docker-compose ps

# Test the API
curl http://localhost:8080/health
```

That's it! Your backend is now running at `http://localhost:8080` 🎉

---

## What Docker Does

Docker packages your entire application into "containers":

- ✅ **Backend Container**: Your FastAPI application
- ✅ **PostgreSQL Container**: Your database
- ✅ **Automatic Migrations**: Runs on startup
- ✅ **Data Persistence**: Database data saved in volumes

**Benefits:**

- Same environment everywhere (dev, staging, production)
- No "works on my machine" issues
- Easy to deploy to cloud (AWS, Google Cloud, Azure)
- Isolated and secure

---

## Common Commands

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart services
docker-compose restart
```

### View Logs

```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec postgres psql -U linearuser -d lineardb

# Run migrations manually
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Container Management

```bash
# Access backend container shell
docker-compose exec backend bash

# Rebuild containers (after code changes)
docker-compose up -d --build

# View container status
docker-compose ps

# View resource usage
docker stats
```

---

## Environment Variables

Create a `.env` file with these variables:

```env
# PostgreSQL Configuration
POSTGRES_USER=linearuser
POSTGRES_PASSWORD=your-secure-password-here
POSTGRES_DB=lineardb

# Database URL (use 'postgres' as hostname in Docker)
DATABASE_URL=postgresql+asyncpg://linearuser:your-secure-password-here@postgres:5432/lineardb

# JWT Configuration
SECRET_KEY=your-super-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Security Tips:**

- Use strong passwords (minimum 16 characters)
- Generate SECRET_KEY with: `openssl rand -hex 32`
- Never commit `.env` to git
- Use different credentials for production

---

## Troubleshooting

### Container won't start

```bash
# Check logs for errors
docker-compose logs backend

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Database connection error

```bash
# Check if PostgreSQL is ready
docker-compose exec postgres pg_isready -U linearuser

# Verify database exists
docker-compose exec postgres psql -U linearuser -l
```

### Port already in use

Edit `docker-compose.yml` and change port mapping:

```yaml
ports:
  - "8081:8080" # Change 8080 to 8081
```

### Reset everything (⚠️ deletes all data)

```bash
docker-compose down -v
docker-compose up -d --build
```

### View detailed container info

```bash
docker inspect linear-backend
docker inspect linear-postgres
```

---

## Production Deployment

### Cloud Platforms

**Render.com** (Easiest)

1. Push code to GitHub
2. Create new Web Service on Render
3. Select "Docker" as environment
4. Add environment variables
5. Deploy!

**AWS ECS/Fargate**

1. Push image to ECR
2. Create ECS task definition
3. Configure RDS for PostgreSQL
4. Deploy service

**Google Cloud Run**

1. Build image: `gcloud builds submit --tag gcr.io/PROJECT_ID/linear-backend`
2. Deploy: `gcloud run deploy --image gcr.io/PROJECT_ID/linear-backend`

**DigitalOcean App Platform**

1. Connect GitHub repository
2. Select Dockerfile
3. Add environment variables
4. Deploy

### Production Checklist

- [ ] Use managed database (AWS RDS, Google Cloud SQL)
- [ ] Generate strong SECRET_KEY
- [ ] Enable HTTPS (use reverse proxy like Nginx)
- [ ] Configure CORS for your frontend domain
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Configure automated backups
- [ ] Use Docker secrets for sensitive data
- [ ] Set resource limits in docker-compose.yml
- [ ] Enable logging aggregation
- [ ] Configure health checks

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Docker Network                  │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   Backend    │    │  PostgreSQL  │  │
│  │  Container   │───▶│  Container   │  │
│  │  Port: 8080  │    │  Port: 5432  │  │
│  └──────────────┘    └──────────────┘  │
│         │                    │          │
└─────────┼────────────────────┼──────────┘
          │                    │
          ▼                    ▼
    Host:8080          postgres_data
                         (Volume)
```

**Components:**

- **Backend Container**: FastAPI app with Uvicorn (4 workers)
- **PostgreSQL Container**: Database with persistent storage
- **Docker Network**: Isolated communication between containers
- **Volumes**: Data persistence for database and static files

---

## File Structure

```
backend/
├── Dockerfile              # Multi-stage build configuration
├── docker-compose.yml      # Multi-container orchestration
├── .dockerignore          # Exclude files from build
├── docker-entrypoint.sh   # Startup script (migrations + server)
├── .env.docker            # Environment template for Docker
├── .env                   # Your actual environment (not in git)
└── DOCKER_GUIDE.md        # This file
```

---

## Advanced Usage

### Custom Network

```bash
# Create custom network
docker network create linear-network

# Use in docker-compose.yml
networks:
  default:
    external:
      name: linear-network
```

### Volume Backup

```bash
# Backup database volume
docker run --rm -v linear-backend_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres-backup.tar.gz /data

# Restore database volume
docker run --rm -v linear-backend_postgres_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/postgres-backup.tar.gz -C /
```

### Multi-stage Build Benefits

- **Smaller Image**: ~200MB vs ~1GB
- **Faster Builds**: Cached layers
- **More Secure**: No build tools in production image

---

## Support

For issues or questions:

1. Check logs: `docker-compose logs -f`
2. Review troubleshooting section above
3. Open GitHub issue with logs and error messages

---

**Happy Deploying! 🚀**
