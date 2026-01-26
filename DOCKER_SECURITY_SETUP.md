# ⚠️ SECURITY NOTICE - REQUIRED SETUP

## Before Running Docker Compose

You **MUST** create a `.env` file with your credentials. The `docker-compose.yml` file does NOT have default values for security reasons.

### Quick Setup

1. **Copy the template**:

   ```bash
   cp .env.docker .env
   ```

2. **Update these values in `.env`**:

   ```bash
   # Change these REQUIRED values:
   POSTGRES_PASSWORD=your-strong-password-here
   SECRET_KEY=generate-with-openssl-rand-hex-32

   # Optional (have defaults):
   POSTGRES_USER=linearuser
   POSTGRES_DB=lineardb
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Generate SECRET_KEY**:

   ```bash
   # On Linux/Mac:
   openssl rand -hex 32

   # On Windows PowerShell:
   -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | % {[char]$_})
   ```

4. **Update DATABASE_URL** in `.env`:
   ```bash
   DATABASE_URL=postgresql+asyncpg://linearuser:YOUR_PASSWORD@postgres:5432/lineardb
   ```

### Example `.env` File

```bash
# PostgreSQL Configuration
POSTGRES_USER=linearuser
POSTGRES_PASSWORD=MyStr0ng!P@ssw0rd2024
POSTGRES_DB=lineardb

# Database URL
DATABASE_URL=postgresql+asyncpg://linearuser:MyStr0ng!P@ssw0rd2024@postgres:5432/lineardb

# JWT Configuration
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Security Best Practices

✅ **Use strong passwords** (minimum 16 characters)  
✅ **Generate random SECRET_KEY** (minimum 32 characters)  
✅ **Never commit `.env` to git** (already in `.gitignore`)  
✅ **Use different credentials** for dev/staging/production  
✅ **Rotate secrets regularly** in production

### Why No Defaults?

GitHub security scanning (GitGuardian) flags hardcoded passwords as security vulnerabilities. By requiring explicit configuration, we ensure:

- No accidental exposure of credentials
- Developers consciously set secure passwords
- Production deployments use unique credentials

---

**After creating `.env`, run**:

```bash
docker-compose up -d
```
