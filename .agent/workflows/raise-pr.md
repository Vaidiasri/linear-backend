---
description: Professional PR workflow - commits only essential documentation files
---

# Professional PR Workflow

This workflow creates a professional Pull Request with only essential documentation and code files.

## Step 1: Check Current Status

```bash
git status
```

## Step 2: Create Feature Branch

Branch naming convention:

- `feature/celery-email-worker` - For new features
- `fix/email-validation` - For bug fixes
- `docs/api-documentation` - For documentation

```bash
git checkout -b feature/celery-email-worker
```

## Step 3: Stage Only Professional Files

**Include:**

- ✅ Code files (`app/workers/*.py`)
- ✅ Configuration files (`requirements.txt`, `.env.example`)
- ✅ Essential documentation (`README.md`, `API_GUIDELINES.md`)
- ✅ Feature-specific guides (e.g., `EMAIL_WORKER_GUIDE.md`)

**Exclude:**

- ❌ Temporary files (`*.log`, `*.tmp`)
- ❌ Development guides (`QUICK_START.md`, `REDIS_SETUP_WINDOWS.md`)
- ❌ Internal docs (`BUG_FIXES_SUMMARY.md`, `FEATURE_REVIEW.md`)
- ❌ Test scripts (`test_celery.py`)
- ❌ Batch files (`*.bat`)
- ❌ Environment files (`.env`)

// turbo

```bash
# Add code files
git add app/workers/*.py

# Add configuration
git add requirements.txt

# Add essential documentation (if modified)
git add README.md
git add EMAIL_WORKER_GUIDE.md
```

## Step 4: Commit with Professional Message

Format: `<type>(<scope>): <description>`

Types:

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `refactor` - Code refactoring
- `perf` - Performance improvement
- `test` - Adding tests
- `chore` - Maintenance

Example:

```
feat(workers): implement celery email worker with redis

- Add Celery configuration with Redis broker
- Implement email tasks with retry logic
- Create email templates module
- Add input validation for emails
- Reduce code complexity to 1
- Add comprehensive documentation
```

```bash
git commit -m "feat(workers): implement celery email worker with redis

- Add Celery configuration with Redis broker
- Implement email tasks with retry logic
- Create email templates module
- Add input validation for emails
- Reduce code complexity to 1
- Add comprehensive documentation"
```

## Step 5: Push to Remote

// turbo

```bash
git push -u origin feature/celery-email-worker
```

## Step 6: Create Pull Request

Using GitHub CLI:

```bash
gh pr create \
  --title "feat(workers): Implement Celery Email Worker with Redis" \
  --body "## Summary

Implemented production-ready Celery email worker system with Redis for background email processing.

## Changes

### New Files
- \`app/workers/celery_app.py\` - Celery configuration
- \`app/workers/email_tasks.py\` - Email task implementations
- \`app/workers/email_templates.py\` - Email template module
- \`app/workers/example_usage.py\` - FastAPI integration examples
- \`EMAIL_WORKER_GUIDE.md\` - Complete setup guide

### Modified Files
- \`requirements.txt\` - Added Celery, Redis, Flower dependencies
- \`.env.example\` - Added Redis configuration

## Features

✅ Background email processing with Celery
✅ Automatic retry with exponential backoff
✅ Email validation with test domain support
✅ Template separation for maintainability
✅ Scheduled tasks (daily reports, cleanup)
✅ Monitoring with Flower UI
✅ Code complexity reduced to 1

## Testing

- All tasks registered successfully
- Email validation working
- Worker processes tasks correctly
- Test suite passing

## Documentation

Complete setup guide included in \`EMAIL_WORKER_GUIDE.md\`

## Breaking Changes

None

## Dependencies

- celery==5.3.4
- redis==5.0.1
- flower==2.0.1
- email-validator==2.3.0 (already in requirements)

## Deployment Notes

Requires Redis server running. See \`EMAIL_WORKER_GUIDE.md\` for setup instructions." \
  --base main
```

## Alternative: Manual PR Creation

If GitHub CLI is not available:

1. Push the branch (Step 5)
2. Go to GitHub repository
3. Click "Compare & pull request"
4. Fill in the PR template with above information
5. Submit PR

## Notes

### Before Raising PR

- ✅ Code reviewed and tested
- ✅ All tests passing
- ✅ Documentation updated
- ✅ No sensitive data committed
- ✅ Only professional files included

### PR Best Practices

- Clear, descriptive title
- Detailed description with context
- List all changes
- Include testing information
- Mention breaking changes (if any)
- Link related issues

### File Selection Strategy

**Always Include:**

- Source code files
- Configuration files
- API documentation
- Feature-specific guides
- Updated README

**Never Include:**

- `.env` files (use `.env.example`)
- Log files
- Temporary files
- Development-only scripts
- Internal review documents

---

**Professional PR ready to raise! 🚀**
