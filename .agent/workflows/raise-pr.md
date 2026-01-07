---
description: Automatically create branch, commit changes, and raise PR
---

# Raise PR Workflow

This workflow automates the entire Git workflow from creating a feature branch to raising a Pull Request.

## Steps:

### 1. Check current Git status

```bash
git status
```

### 2. Create a feature branch

- Branch naming convention: `feature/<descriptive-name>` or `fix/<issue-name>`
- Example: `feature/add-blog-api` or `fix/database-connection`

```bash
git checkout -b <branch-name>
```

### 3. Stage all changes

// turbo

```bash
git add .
```

### 4. Commit with descriptive message

- Format: `<type>: <short description>`
- Types: feat, fix, docs, style, refactor, test, chore
- Example: `feat: add blog model and database setup`

```bash
git commit -m "<commit-message>"
```

### 5. Push to remote

// turbo

```bash
git push -u origin <branch-name>
```

### 6. Create Pull Request using GitHub CLI

- Requires GitHub CLI (`gh`) to be installed and authenticated
- Auto-generates title from commit message
- Adds detailed description of changes

```bash
gh pr create --title "<PR-title>" --body "<PR-description>" --base main
```

## Notes:

- Make sure you're in the correct repository directory
- Ensure you have proper permissions to push to the repository
- GitHub CLI must be installed: `winget install GitHub.cli`
- Authenticate with: `gh auth login`
