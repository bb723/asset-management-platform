# Asset Management Platform - Deployment Guide

Complete guide for deploying the Asset Management Platform to Heroku (staging and production environments).

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Git Setup](#git-setup)
3. [Heroku Application Creation](#heroku-application-creation)
4. [Environment Configuration](#environment-configuration)
5. [Database Initialization](#database-initialization)
6. [Azure App Registration](#azure-app-registration)
7. [Deployment](#deployment)
8. [Post-Deployment Testing](#post-deployment-testing)
9. [Future Deployments](#future-deployments)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting deployment, ensure you have:

- [x] Git installed locally
- [x] Heroku CLI installed (`heroku --version`)
- [x] Heroku account with access to Standard Management organization
- [x] Access to Snowflake database credentials
- [x] Access to Microsoft Azure app registration
- [x] Python 3.10+ installed locally
- [x] Completed local development and testing

## Git Setup

### Step 1: Initialize Git Repository

```bash
cd asset-management-platform

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - Asset Management Platform"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/bb723
2. Click "New repository"
3. Name: `asset-management-platform`
4. Description: "Asset Management Platform for Standard Management Company"
5. Private repository
6. Do NOT initialize with README (we already have one)
7. Click "Create repository"

### Step 3: Link Local to GitHub

```bash
# Add GitHub remote
git remote add origin https://github.com/bb723/asset-management-platform.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

Verify: Visit https://github.com/bb723/asset-management-platform to confirm files are uploaded.

## Heroku Application Creation

### Step 1: Create Staging Application

```bash
# Create staging app
heroku create asset-mgmt-staging --team standard-management

# Expected output:
# Creating ⬢ asset-mgmt-staging... done
# https://asset-mgmt-staging.herokuapp.com/ | https://git.heroku.com/asset-mgmt-staging.git
```

### Step 2: Create Production Application

```bash
# Create production app
heroku create asset-mgmt-production --team standard-management

# Expected output:
# Creating ⬢ asset-mgmt-production... done
# https://asset-mgmt-production.herokuapp.com/ | https://git.heroku.com/asset-mgmt-production.git
```

### Step 3: Configure Git Remotes

```bash
# Add staging remote
heroku git:remote -a asset-mgmt-staging
git remote rename heroku staging

# Add production remote
heroku git:remote -a asset-mgmt-production
git remote rename heroku production

# Verify remotes
git remote -v

# Expected output:
# origin    https://github.com/bb723/asset-management-platform.git (fetch)
# origin    https://github.com/bb723/asset-management-platform.git (push)
# staging   https://git.heroku.com/asset-mgmt-staging.git (fetch)
# staging   https://git.heroku.com/asset-mgmt-staging.git (push)
# production https://git.heroku.com/asset-mgmt-production.git (fetch)
# production https://git.heroku.com/asset-mgmt-production.git (push)
```

## Environment Configuration

### Method 1: Using Heroku CLI (Recommended for Bulk Operations)

#### Generate Secret Keys

```bash
# Generate staging secret key
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output

# Generate production secret key (use different key!)
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output
```

#### Configure Staging Environment

```bash
# Flask Configuration
heroku config:set FLASK_SECRET_KEY=<paste-staging-secret-key-here> --remote staging
heroku config:set FLASK_ENV=staging --remote staging
heroku config:set REDIRECT_URI=https://asset-mgmt-staging.herokuapp.com/auth/callback --remote staging

# Snowflake Configuration (same for staging and production)
heroku config:set SNOWFLAKE_USER=your-snowflake-username --remote staging
heroku config:set SNOWFLAKE_PASSWORD="your-snowflake-password" --remote staging
heroku config:set SNOWFLAKE_ACCOUNT=your-snowflake-account --remote staging
heroku config:set SNOWFLAKE_WAREHOUSE=your-warehouse-name --remote staging
heroku config:set SNOWFLAKE_DATABASE=your-database-name --remote staging
heroku config:set SNOWFLAKE_ROLE=your-role-name --remote staging
heroku config:set SNOWFLAKE_SCHEMA=PUBLIC --remote staging

# Microsoft OAuth (same for staging and production)
heroku config:set MS_CLIENT_ID=your-azure-client-id --remote staging
heroku config:set MS_CLIENT_SECRET=your-azure-client-secret --remote staging
heroku config:set MS_TENANT_ID=your-azure-tenant-id --remote staging

# File Storage
heroku config:set UPLOAD_FOLDER=./uploads --remote staging
heroku config:set MAX_CONTENT_LENGTH=16777216 --remote staging
```

#### Configure Production Environment

```bash
# Flask Configuration
heroku config:set FLASK_SECRET_KEY=<paste-production-secret-key-here> --remote production
heroku config:set FLASK_ENV=production --remote production
heroku config:set REDIRECT_URI=https://asset-mgmt-production.herokuapp.com/auth/callback --remote production

# Snowflake Configuration (same as staging)
heroku config:set SNOWFLAKE_USER=your-snowflake-username --remote production
heroku config:set SNOWFLAKE_PASSWORD="your-snowflake-password" --remote production
heroku config:set SNOWFLAKE_ACCOUNT=your-snowflake-account --remote production
heroku config:set SNOWFLAKE_WAREHOUSE=your-warehouse-name --remote production
heroku config:set SNOWFLAKE_DATABASE=your-database-name --remote production
heroku config:set SNOWFLAKE_ROLE=your-role-name --remote production
heroku config:set SNOWFLAKE_SCHEMA=PUBLIC --remote production

# Microsoft OAuth (same as staging)
heroku config:set MS_CLIENT_ID=your-azure-client-id --remote production
heroku config:set MS_CLIENT_SECRET=your-azure-client-secret --remote production
heroku config:set MS_TENANT_ID=your-azure-tenant-id --remote production

# File Storage
heroku config:set UPLOAD_FOLDER=./uploads --remote production
heroku config:set MAX_CONTENT_LENGTH=16777216 --remote production
```

### Method 2: Using Heroku Dashboard (Easier for One-Time Setup)

1. Go to https://dashboard.heroku.com
2. Select `asset-mgmt-staging` app
3. Click "Settings" tab
4. Click "Reveal Config Vars"
5. Add each variable manually:

| Key | Value (Staging) |
|-----|----------------|
| FLASK_SECRET_KEY | (generated unique key) |
| FLASK_ENV | staging |
| REDIRECT_URI | https://asset-mgmt-staging.herokuapp.com/auth/callback |
| SNOWFLAKE_USER | your-snowflake-username |
| SNOWFLAKE_PASSWORD | your-snowflake-password |
| SNOWFLAKE_ACCOUNT | your-snowflake-account |
| SNOWFLAKE_WAREHOUSE | your-warehouse-name |
| SNOWFLAKE_DATABASE | your-database-name |
| SNOWFLAKE_ROLE | your-role-name |
| SNOWFLAKE_SCHEMA | PUBLIC |
| MS_CLIENT_ID | your-azure-client-id |
| MS_CLIENT_SECRET | your-azure-client-secret |
| MS_TENANT_ID | your-azure-tenant-id |
| UPLOAD_FOLDER | ./uploads |
| MAX_CONTENT_LENGTH | 16777216 |

6. Repeat for `asset-mgmt-production` (change FLASK_SECRET_KEY, FLASK_ENV, REDIRECT_URI)

### Verify Configuration

```bash
# Check staging config
heroku config --remote staging

# Check production config
heroku config --remote production
```

## Database Initialization

### Step 1: Run Schema Script on Production

```bash
# Deploy to production first (so script can run)
git push production main

# Run database initialization script
heroku run python scripts/init_db.py --remote production
```

Expected output:
```
============================================================
Asset Management Platform - Database Initialization
============================================================

Connecting to Snowflake...
✓ Connected to Snowflake

Reading schema file...
✓ Schema file loaded

Executing schema statements...
Executing: CREATE TABLE entities
✓ Created table: ENTITIES
Executing: CREATE TABLE buildings
✓ Created table: BUILDINGS
Executing: CREATE TABLE budget_items
✓ Created table: BUDGET_ITEMS
Executing: CREATE TABLE documents
✓ Created table: DOCUMENTS
Executing: CREATE TABLE share_tokens
✓ Created table: SHARE_TOKENS

============================================================
Summary: 5 succeeded, 0 failed
============================================================

Verifying tables...
✓ Table exists: ENTITIES
✓ Table exists: BUILDINGS
✓ Table exists: BUDGET_ITEMS
✓ Table exists: DOCUMENTS
✓ Table exists: SHARE_TOKENS

✓ Database initialization completed successfully
```

### Step 2: Verify Tables in Snowflake

Option A: Via Heroku Console
```bash
heroku run python -c "from foundation.clients import SnowflakeClient; sf = SnowflakeClient(); print(sf.execute_query('SHOW TABLES IN your-database-name.PUBLIC'))" --remote production
```

Option B: Via Snowflake Web UI
1. Log in to Snowflake
2. Navigate to your-database-name database
3. Check PUBLIC schema
4. Verify tables exist: ENTITIES, BUILDINGS, BUDGET_ITEMS, DOCUMENTS, SHARE_TOKENS

## Azure App Registration

### Update Redirect URIs

1. Go to https://portal.azure.com
2. Navigate to "Azure Active Directory" > "App registrations"
3. Find app with Client ID: `your-azure-client-id`
4. Click "Authentication" in left menu
5. Under "Redirect URIs", click "Add URI"
6. Add both staging and production URIs:
   - `https://asset-mgmt-staging.herokuapp.com/auth/callback`
   - `https://asset-mgmt-production.herokuapp.com/auth/callback`
7. Click "Save"

### Verify Configuration

1. Client ID: `your-azure-client-id`
2. Tenant ID: `your-azure-tenant-id`
3. Client Secret: Active and not expired
4. Redirect URIs: Include both staging and production URLs
5. API Permissions: `User.Read` granted

## Deployment

### Deploy to Staging

```bash
# Ensure you're on main branch
git checkout main

# Push to staging
git push staging main

# Monitor deployment
heroku logs --tail --remote staging
```

Expected output:
```
remote: -----> Building on the Heroku-22 stack
remote: -----> Using buildpack: heroku/python
remote: -----> Python app detected
remote: -----> Installing python-3.10.15
remote: -----> Installing pip 24.0, setuptools 69.0.3 and wheel 0.42.0
remote: -----> Installing SQLite3
remote: -----> Installing requirements with pip
remote: -----> Discovering process types
remote:        Procfile declares types -> web
remote: -----> Compressing...
remote: -----> Launching...
remote:        Released v1
remote:        https://asset-mgmt-staging.herokuapp.com/ deployed to Heroku
```

### Test Staging

```bash
# Open staging app in browser
heroku open --remote staging

# Check logs
heroku logs --tail --remote staging
```

Test checklist:
- [ ] Application loads successfully
- [ ] Login redirect to Microsoft works
- [ ] After login, redirected back to app
- [ ] Can create entity
- [ ] Can create building
- [ ] Can edit budget
- [ ] Can upload document
- [ ] Can generate shareable link
- [ ] Shareable link works (no auth required)

### Deploy to Production

**ONLY after staging is fully tested and verified!**

```bash
# Push to production
git push production main

# Monitor deployment
heroku logs --tail --remote production
```

### Test Production

```bash
# Open production app in browser
heroku open --remote production

# Check logs
heroku logs --tail --remote production
```

Repeat same test checklist as staging.

## Post-Deployment Testing

### Complete User Flow Test

1. **Authentication**
   - Navigate to application URL
   - Click "Login"
   - Sign in with Microsoft account
   - Verify successful redirect to home page

2. **Entity Management**
   - Create new entity
   - Edit entity
   - View entity details

3. **Building Management**
   - Add building to entity
   - Edit building details
   - View building details

4. **Budget Management**
   - Navigate to building budget
   - Edit budget values
   - Save changes
   - Verify totals calculate correctly
   - View entity-level aggregate budget

5. **Document Management**
   - Upload document
   - Download document
   - Delete document

6. **Shareable Links**
   - Generate shareable link
   - Copy link
   - Open in incognito/private window (no login)
   - Verify read-only access works

### Performance Testing

```bash
# Check app metrics
heroku metrics --remote production

# Check dyno status
heroku ps --remote production
```

### Error Monitoring

```bash
# Monitor logs for errors
heroku logs --tail --remote production | grep ERROR

# Check for warnings
heroku logs --tail --remote production | grep WARNING
```

## Future Deployments

### Standard Deployment Workflow

1. **Make changes locally**
   ```bash
   # Make code changes
   # Test locally: python app.py
   ```

2. **Commit changes**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

3. **Deploy to staging**
   ```bash
   git push staging main
   heroku open --remote staging
   # Test thoroughly
   ```

4. **Deploy to production**
   ```bash
   git push production main
   heroku open --remote production
   # Verify in production
   ```

### Rollback Procedure

If production deployment has issues:

```bash
# List releases
heroku releases --remote production

# Rollback to previous version
heroku rollback v<previous-version-number> --remote production

# Example:
heroku rollback v5 --remote production
```

### Database Migrations

For schema changes:

1. Update `database/schema.sql`
2. Test changes locally
3. Deploy to staging
4. Run migration script:
   ```bash
   heroku run python scripts/migrate_db.py --remote staging
   ```
5. Test thoroughly
6. Deploy to production
7. Run migration script:
   ```bash
   heroku run python scripts/migrate_db.py --remote production
   ```

## Troubleshooting

### Common Issues

#### Issue: Application won't start

**Symptoms**: H10 or H14 errors in logs

**Solution**:
```bash
# Check logs
heroku logs --tail --remote production

# Verify config vars
heroku config --remote production

# Restart dynos
heroku restart --remote production

# Check dyno status
heroku ps --remote production
```

#### Issue: Authentication fails

**Symptoms**: OAuth redirect errors, state mismatch

**Solution**:
1. Verify REDIRECT_URI is correct in config vars
2. Check Azure app registration has correct redirect URIs
3. Verify MS_CLIENT_ID, MS_CLIENT_SECRET, MS_TENANT_ID are correct
4. Check browser cookies are enabled
5. Try clearing browser cache and cookies

```bash
# Verify auth config
heroku config:get REDIRECT_URI --remote production
heroku config:get MS_CLIENT_ID --remote production
```

#### Issue: Database connection fails

**Symptoms**: SnowflakeClient errors, connection timeouts

**Solution**:
```bash
# Test connection
heroku run python -c "from foundation.clients import SnowflakeClient; sf = SnowflakeClient(); print('Connected:', sf.execute_query('SELECT 1'))" --remote production

# Verify Snowflake config
heroku config:get SNOWFLAKE_USER --remote production
heroku config:get SNOWFLAKE_ACCOUNT --remote production
```

#### Issue: File uploads fail

**Symptoms**: 413 errors, file not found errors

**Solution**:
1. Check file size is under 16MB
2. Verify UPLOAD_FOLDER is set
3. Check file type is allowed
4. On Heroku, use ephemeral filesystem (files deleted on dyno restart)
5. Consider S3 integration for persistent storage

```bash
heroku config:get UPLOAD_FOLDER --remote production
heroku config:get MAX_CONTENT_LENGTH --remote production
```

#### Issue: Budget save fails

**Symptoms**: AJAX errors, 500 errors on save

**Solution**:
1. Check browser console for JavaScript errors
2. Verify Snowflake connection
3. Check for SQL syntax errors in logs
4. Test locally first

```bash
# Check logs during save
heroku logs --tail --remote production
```

### Useful Commands

```bash
# View real-time logs
heroku logs --tail --remote production

# View recent logs
heroku logs -n 1000 --remote production

# Check dyno status
heroku ps --remote production

# Restart dynos
heroku restart --remote production

# Access Heroku console
heroku run bash --remote production

# Run Python commands
heroku run python --remote production

# List config vars
heroku config --remote production

# Set config var
heroku config:set KEY=VALUE --remote production

# Unset config var
heroku config:unset KEY --remote production

# Scale dynos
heroku ps:scale web=1 --remote production

# View app info
heroku info --remote production

# View releases
heroku releases --remote production

# Rollback
heroku rollback --remote production
```

### Support Resources

- Heroku Documentation: https://devcenter.heroku.com/
- Flask Documentation: https://flask.palletsprojects.com/
- Snowflake Documentation: https://docs.snowflake.com/
- Bootstrap Documentation: https://getbootstrap.com/docs/
- Foundation Package: https://github.com/bb723/foundation

### Monitoring and Maintenance

#### Regular Maintenance Tasks

1. **Weekly**:
   - Check application logs for errors
   - Verify backups are running
   - Review performance metrics

2. **Monthly**:
   - Update dependencies if needed
   - Review and optimize database queries
   - Check disk usage for uploaded files

3. **Quarterly**:
   - Security audit
   - Performance optimization
   - User feedback review

#### Log Monitoring

Set up log drains for long-term storage:

```bash
# Example: Papertrail
heroku addons:create papertrail --remote production

# View logs in Papertrail dashboard
heroku addons:open papertrail --remote production
```

## Integrating with Foundation Dashboard

To add a link from the Foundation Dashboard to this app:

1. Set environment variable in Foundation Dashboard:
   ```bash
   heroku config:set ASSET_MGMT_URL=https://asset-mgmt-production.herokuapp.com --app propertyops-dashboard-prod
   ```

2. Add route in Foundation Dashboard `app.py`:
   ```python
   @app.route('/assets')
   @login_required
   def assets():
       asset_url = os.getenv('ASSET_MGMT_URL', '#')
       return redirect(asset_url)
   ```

3. Add navigation link in Foundation Dashboard template:
   ```html
   <li class="nav-item">
       <a class="nav-link" href="{{ url_for('assets') }}">
           <i class="bi bi-building"></i> Asset Management
       </a>
   </li>
   ```

## Summary

You have successfully deployed the Asset Management Platform! The application is now:

- ✅ Running on Heroku (staging and production)
- ✅ Connected to Snowflake database
- ✅ Configured with Microsoft OAuth
- ✅ Ready for entity, building, budget, and document management
- ✅ Supporting shareable links for external stakeholders

For questions or issues, check logs first, then consult this guide's troubleshooting section.
