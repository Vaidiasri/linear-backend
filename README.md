# Linear Backend Clone

FastAPI-based backend for a Linear-like project management system.

## Features

- ✅ User Authentication (Signup/Login with JWT)
- ✅ Duplicate email validation
- ✅ PostgreSQL database with async support
- ✅ Environment-based configuration

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM with async support
- **JWT** - Token-based authentication
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

### 5. Run the server

```bash
python main.py
```

Server will start at `http://127.0.0.1:8080`

## API Endpoints

### Authentication

- `POST /auth/login` - User login
- `POST /users/` - User signup

### Health Check

- `GET /health` - Server health check

## Project Structure

```
backend/
├── app/
│   ├── lib/
│   │   └── database.py      # Database configuration
│   ├── model/
│   │   └── model.py         # SQLAlchemy models
│   ├── routers/
│   │   ├── auth.py          # Authentication routes
│   │   └── user.py          # User routes
│   ├── schemas/
│   │   └── __init__.py      # Pydantic schemas
│   ├── oauth2.py            # JWT token handling
│   ├── utils.py             # Utility functions
│   └── main.py              # FastAPI app entry point
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── .gitignore
└── requirements.txt
```

## Development

- Database tables are created automatically on startup
- Server runs with hot reload enabled
- All sensitive data is stored in `.env` file

## Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Duplicate email validation
- Environment variables for sensitive data
