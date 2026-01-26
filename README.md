# Linear Backend Clone

FastAPI-based backend for a Linear-like project management system with complete issue tracking, comments, and activity logs.

## Features

### Authentication & Users

- ✅ User Authentication (Signup/Login with JWT)
- ✅ Duplicate email validation
- ✅ Password hashing with bcrypt

### Issues Management

- ✅ Complete CRUD operations for issues
- ✅ Issue status tracking (backlog, todo, in_progress, done, canceled)
- ✅ Priority levels (0-3)
- ✅ Advanced filtering (status, priority, team, project, assignee, search)
- ✅ Activity logging for all changes
- ✅ Assignee management
- ✅ Export issues to CSV with filters

### Comments

- ✅ Add comments to issues
- ✅ Author information with comments
- ✅ Timestamp tracking

### Activity Logs

- ✅ Automatic tracking of issue changes
- ✅ Track status, priority, title, assignee changes
- ✅ User attribution for all activities
- ✅ Complete audit trail

### Teams & Projects

- ✅ Team management
- ✅ Project organization
- ✅ Issue assignment to teams and projects

### Attachments

- ✅ File upload support (local storage)
- ✅ Attach files to specific issues
- ✅ Secure file validation (images, docs)
- ✅ Complete CRUD for attachments
- ✅ Secure file validation (images, docs)

### Dashboard Analytics

- ✅ Real-time statistics
- ✅ Status distribution charts
- ✅ Priority breakdown
- ✅ Team progress tracking

### Real-time Updates (WebSockets)

- ✅ Live issue updates (Create, Update, Delete)
- ✅ Secure WebSocket authentication
- ✅ Team-specific channels
- ✅ Automatic connection management

## Architecture

We use a **Service-Repository Pattern** to separate concerns:

- **Routers**: Handle HTTP requests and response.
- **Services**: Handle business logic and validation.
- **CRUD/Repositories**: Handle direct database operations.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database with async support
- **SQLAlchemy** - ORM with async operations
- **Alembic** - Database migrations
- **JWT** - Token-based authentication
- **Pydantic** - Data validation
- **Python-dotenv** - Environment variable management

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Vaidiasri/linear-backend.git
cd linear-backend
```

### 2. Create virtual environment

```bash
python -m venv myenv
myenv\Scripts\activate  # Windows
# source myenv/bin/activate  # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup environment variables

Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

Update `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost/database_name
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Run the server

```bash
python main.py
```

Server will start at `http://127.0.0.1:8080`

## Docker Deployment 🐳

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

### Quick Start with Docker

1. **Clone the repository**

   ```bash
   git clone https://github.com/Vaidiasri/linear-backend.git
   cd linear-backend
   ```

2. **Create environment file**

   ```bash
   # Copy the Docker environment template
   cp .env.docker .env

   # Edit .env and update these values:
   # - POSTGRES_PASSWORD (use a strong password)
   # - SECRET_KEY (generate with: openssl rand -hex 32)
   ```

3. **Build and start containers**

   ```bash
   docker-compose up -d
   ```

4. **Check container status**

   ```bash
   docker-compose ps
   ```

5. **View logs**

   ```bash
   # All services
   docker-compose logs -f

   # Backend only
   docker-compose logs -f backend

   # Database only
   docker-compose logs -f postgres
   ```

6. **Access the application**
   - API: `http://localhost:8080`
   - Swagger Docs: `http://localhost:8080/docs`
   - Health Check: `http://localhost:8080/health`

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (⚠️ deletes all data)
docker-compose down -v

# Rebuild containers
docker-compose up -d --build

# View container logs
docker-compose logs -f backend

# Access backend container shell
docker-compose exec backend bash

# Access PostgreSQL shell
docker-compose exec postgres psql -U linearuser -d lineardb

# Run database migrations manually
docker-compose exec backend alembic upgrade head
```

### Environment Variables for Docker

| Variable                      | Description         | Default                |
| ----------------------------- | ------------------- | ---------------------- |
| `POSTGRES_USER`               | PostgreSQL username | `linearuser`           |
| `POSTGRES_PASSWORD`           | PostgreSQL password | `linearpass`           |
| `POSTGRES_DB`                 | Database name       | `lineardb`             |
| `SECRET_KEY`                  | JWT secret key      | (change in production) |
| `ALGORITHM`                   | JWT algorithm       | `HS256`                |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time   | `30`                   |

### Docker Architecture

- **Backend Container**: FastAPI application running on port 8080
- **PostgreSQL Container**: Database running on port 5432
- **Docker Network**: Isolated network for service communication
- **Volumes**:
  - `postgres_data`: Persistent database storage
  - `./static`: Mounted for file uploads
  - `./logs`: Mounted for application logs

### Troubleshooting

**Container won't start:**

```bash
# Check logs
docker-compose logs backend

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

**Database connection error:**

```bash
# Check if PostgreSQL is ready
docker-compose exec postgres pg_isready -U linearuser

# Check database logs
docker-compose logs postgres
```

**Migration errors:**

```bash
# Run migrations manually
docker-compose exec backend alembic upgrade head

# Check migration history
docker-compose exec backend alembic current
```

**Port already in use:**

```bash
# Change ports in docker-compose.yml
# For backend: "8081:8080" instead of "8080:8080"
# For postgres: "5433:5432" instead of "5432:5432"
```

### Production Deployment

For production deployment:

1. **Update environment variables**
   - Use strong passwords
   - Generate secure SECRET_KEY: `openssl rand -hex 32`
   - Set appropriate token expiry time

2. **Use production-ready PostgreSQL**
   - Consider managed database services (AWS RDS, Google Cloud SQL)
   - Update `DATABASE_URL` in `.env`

3. **Enable HTTPS**
   - Use reverse proxy (Nginx, Traefik)
   - Configure SSL certificates

4. **Configure CORS**
   - Update allowed origins in `app/main.py`

5. **Monitor and backup**
   - Set up log aggregation
   - Configure automated database backups
   - Monitor container health

## API Endpoints

### Authentication

- `POST /auth/login` - User login
- `POST /users/` - User signup

### Issues

- `POST /issues/` - Create new issue
- `GET /issues/` - Get all issues (with filters)
- `GET /issues/{id}` - Get issue details with comments and activities
- `PUT /issues/{id}` - Update issue
- `DELETE /issues/{id}` - Delete issue

**Query Parameters for GET /issues/**

- `status_filter` - Filter by status
- `priority` - Filter by priority
- `team_id` - Filter by team
- `project_id` - Filter by project
- `assignee_id` - Filter by assignee

- `GET /issues/search` - Global search for issues
  - `q` - Search query (searches title and description)
- `GET /issues/export` - Export issues to CSV
  - Supports all filters (status, priority, team, project, assignee)

### Comments

- `POST /issues/{issue_id}/comments` - Add comment to issue
- `GET /issues/{issue_id}/comments` - Get all comments for issue

### Teams

- `POST /teams/` - Create team
- `GET /teams/` - Get all teams

### Projects

- `POST /projects/` - Create project
- `GET /projects/` - Get all projects

### Attachments

- `POST /attachments/{issue_id}` - Upload file for an issue
- `GET /attachments/issue/{issue_id}` - List all attachments for an issue
- `GET /attachments/{attachment_id}` - Get attachment details
- `PUT /attachments/{attachment_id}` - Update attachment filename
- `DELETE /attachments/{attachment_id}` - Delete attachment (and file)

### Dashboard

- `GET /dashboard/stats` - Get aggregated statistics (Status, Priority, Progress)

### Real-time / WebSockets

- `WS /ws?token={jwt_token}` - Establish WebSocket connection
  - **Auth**: Token passed via Query Parameter
  - **Events**: `ISSUE_CREATED`, `ISSUE_UPDATED`, `ISSUE_DELETED`

### Health Check

- `GET /health` - Server health check

## Project Structure

```
backend/
├── app/
│   ├── lib/
│   │   └── database.py           # Database configuration
│   ├── crud/                     # CRUD operations (New)
│   │   ├── base.py
│   │   └── issue.py
│   ├── services/                 # Business logic (New)
│   │   └── issue.py
│   ├── filters.py                # Reusable filters
│   ├── model/                    # SQLAlchemy models (refactored)

│   │   ├── __init__.py
│   │   ├── user.py               # User model
│   │   ├── team.py               # Team model
│   │   ├── project.py            # Project model
│   │   ├── issue.py              # Issue model
│   │   ├── comment.py            # Comment model
│   │   ├── activity.py           # Activity model
│   │   └── attached.py           # Attachment model

│   ├── routers/                  # API routes
│   │   ├── auth.py               # Authentication routes
│   │   ├── user.py               # User routes
│   │   ├── issue.py              # Issue routes
│   │   ├── comment.py            # Comment routes
│   │   ├── team.py               # Team routes
│   │   ├── project.py            # Project routes
│   │   ├── attached.py           # Attachment routes
│   │   ├── dashboard.py          # Dashboard routes (New)
│   │   └── websocket.py          # WebSocket routes (New)
│   ├── connectionManager.py      # WebSocket connection manager (New)

│   ├── schemas/                  # Pydantic schemas (refactored)
│   │   ├── __init__.py
│   │   ├── user.py               # User schemas
│   │   ├── team.py               # Team schemas
│   │   ├── project.py            # Project schemas
│   │   ├── issue.py              # Issue schemas + Enums
│   │   ├── comment.py            # Comment schemas
│   │   ├── activity.py           # Activity schemas
│   │   └── attached.py           # Attachment schemas

│   ├── utils/
│   │   └── __init__.py           # Utility functions
│   ├── oauth2.py                 # JWT token handling
│   └── main.py                   # FastAPI app entry point
├── alembic/                      # Database migrations
│   └── versions/
├── .env                          # Environment variables (not in git)
├── .env.example                  # Environment template
├── .gitignore
├── alembic.ini                   # Alembic configuration
├── requirements.txt
└── README.md
```

## Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Organization

- **Models**: Organized by entity (one file per model)
- **Schemas**: Organized by entity (one file per schema)
- **Routers**: Organized by resource
- **Clean imports**: `from app.model import User, Issue`

## Features in Detail

### Activity Logging

Every issue update is automatically logged:

- Status changes
- Priority changes
- Title updates
- Assignee changes

### Complete Issue View

GET `/issues/{id}` returns:

- Issue details
- All comments with author info
- Complete activity history
- Uses eager loading for performance

### Error Handling

- Global exception handler for uncaught errors
- Automatic error logging to `app.log`
- Comprehensive try-except blocks
- Database rollback on errors
- Meaningful error messages
- ACID transaction guarantees

## Security

- ✅ Passwords hashed using bcrypt
- ✅ JWT tokens for authentication
- ✅ Duplicate email validation
- ✅ Environment variables for sensitive data
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Authorization checks on all endpoints

## Performance Optimizations

- ✅ Async database operations
- ✅ Eager loading to prevent N+1 queries
- ✅ Database indexes on frequently queried fields
- ✅ Connection pooling

## API Documentation

Interactive API documentation available at:

- Swagger UI: `http://127.0.0.1:8080/docs`
- ReDoc: `http://127.0.0.1:8080/redoc`
