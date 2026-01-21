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

### Health Check

- `GET /health` - Server health check

## Project Structure

```
backend/
├── app/
│   ├── lib/
│   │   └── database.py           # Database configuration
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
│   │   └── attached.py           # Attachment routes

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
