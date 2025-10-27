# Git Security - What's Included and Excluded

## ✅ INCLUDED in Git (Safe to Commit)

### Deployment Scripts
- ✅ `deploy.sh` - Bash deployment script
- ✅ `deploy.bat` - Windows deployment script
- ✅ `.github/workflows/deploy.yml` - GitHub Actions workflow

**Why it's safe**: These scripts don't contain credentials, they use Git remotes and Heroku config vars

### Configuration Templates
- ✅ `.env.example` - Example environment variables (NO REAL CREDENTIALS)
- ✅ `.gitignore` - Files to exclude from Git
- ✅ `Procfile` - Heroku process configuration
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - Python dependencies

**Why it's safe**: These are templates or configuration files without sensitive data

### Documentation
- ✅ `README.md`
- ✅ `DEPLOYMENT.md`
- ✅ `QUICKSTART.md`
- ✅ `ARCHITECTURE.md`
- ✅ `PROJECT_SUMMARY.md`
- ✅ `DEPLOYMENT_CHECKLIST.md`

**Why it's safe**: Documentation for the project

### Application Code
- ✅ `app.py` - Main Flask application
- ✅ `models/` - Data models
- ✅ `database/` - Database queries and schema
- ✅ `scripts/` - Utility scripts
- ✅ `templates/` - HTML templates
- ✅ `static/` - CSS and JavaScript

**Why it's safe**: Application code without credentials

## ❌ EXCLUDED from Git (Contains Secrets)

### Environment Variables
- ❌ `.env` - **LOCAL ENVIRONMENT FILE WITH REAL CREDENTIALS**

**Contains**:
- Snowflake password: `your-snowflake-password`
- Microsoft client secret: `your-azure-client-secret`
- Flask secret keys
- Database connection strings

**Why excluded**: Contains all production credentials - **NEVER COMMIT THIS**

### Generated Files
- ❌ `venv/` - Python virtual environment
- ❌ `__pycache__/` - Python cache files
- ❌ `*.pyc` - Compiled Python files
- ❌ `uploads/` - Uploaded documents
- ❌ `*.log` - Log files

**Why excluded**: Generated files, not part of source code

### IDE Files
- ❌ `.vscode/` - VS Code settings
- ❌ `.idea/` - PyCharm settings
- ❌ `.claude/` - Claude Code settings (may contain local paths)

**Why excluded**: Personal IDE configuration

## How Credentials are Managed

### Local Development
```
.env (NOT in Git)
  ↓
Loaded by python-dotenv
  ↓
Environment variables available to app.py
```

### Heroku (Production)
```
heroku config:set SNOWFLAKE_PASSWORD="..." --remote production
  ↓
Stored securely in Heroku's config vars
  ↓
Environment variables available to app.py
```

### GitHub Actions (Optional)
```
GitHub Secrets (in repository settings)
  ↓
Referenced in .github/workflows/deploy.yml
  ↓
Used for deployment
```

## Security Verification

### Check if .env is excluded:
```bash
git check-ignore .env
# Should output: .env (means it's ignored)
```

### Check what will be committed:
```bash
git status
# Should NOT show .env or uploads/
```

### View what's in staging:
```bash
git diff --cached
# Should NOT contain any passwords or secrets
```

### Search for accidentally committed secrets:
```bash
git log --all --full-history -- .env
# Should show no results (file never committed)
```

## What to Do If You Accidentally Commit Secrets

### If you haven't pushed to GitHub yet:
```bash
# Remove the file from Git history
git rm --cached .env

# Commit the removal
git commit --amend -m "Remove .env from Git"
```

### If you already pushed to GitHub:
1. **Immediately rotate all credentials** (change passwords, regenerate secrets)
2. Remove from Git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   git push origin --force --all
   ```
3. Update Heroku config vars with new credentials
4. Update Azure app secrets if needed

## Credentials Reference

### Where credentials are stored:

| Credential | Local | Heroku Staging | Heroku Production | GitHub (Actions) |
|------------|-------|----------------|-------------------|------------------|
| Snowflake Password | `.env` | Config Vars | Config Vars | Secrets (optional) |
| MS Client Secret | `.env` | Config Vars | Config Vars | Secrets (optional) |
| Flask Secret Key | `.env` | Config Vars | Config Vars | N/A |
| Heroku API Key | N/A | N/A | N/A | Secrets (optional) |

### Files with NO credentials (safe to commit):
- `.env.example` - Example only, uses placeholders
- `DEPLOYMENT.md` - Shows commands but credentials are in config vars
- All other files

## Quick Security Checklist

Before pushing to Git:

- [ ] `.env` is NOT in the staging area
- [ ] No passwords visible in `git diff --cached`
- [ ] `.gitignore` includes `.env`
- [ ] `git status` doesn't show `.env`
- [ ] `.env.example` has placeholder values only
- [ ] No API keys or tokens in code comments

Before deploying:

- [ ] All credentials set in Heroku config vars
- [ ] Different `FLASK_SECRET_KEY` for staging and production
- [ ] Azure redirect URIs updated
- [ ] Snowflake credentials are correct

## Summary

✅ **SAFE TO COMMIT:**
- All code files (`.py`, `.html`, `.css`, `.js`)
- Documentation (`.md` files)
- Configuration templates (`.env.example`, `requirements.txt`)
- Deployment scripts (`deploy.sh`, `deploy.bat`)

❌ **NEVER COMMIT:**
- `.env` file (contains real credentials)
- `uploads/` folder (user files)
- Virtual environment (`venv/`)
- Cache files (`__pycache__/`, `*.pyc`)

🔒 **CREDENTIALS LOCATION:**
- **Local**: `.env` file (not in Git)
- **Heroku**: Config vars (dashboard or CLI)
- **GitHub Actions**: Repository secrets (if used)

---

**Last Updated**: 2025-10-27

**Status**: ✅ All credentials properly secured
