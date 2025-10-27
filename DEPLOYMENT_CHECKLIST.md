# Asset Management Platform - Deployment Checklist

Use this checklist to ensure successful deployment to Heroku.

## Pre-Deployment Checklist

### Local Development

- [ ] Application runs locally without errors (`python app.py`)
- [ ] All routes are accessible and working
- [ ] Authentication works (Microsoft OAuth login)
- [ ] Database connection successful (can create entities)
- [ ] All tests pass (if any)
- [ ] Code is committed to git
- [ ] `.env` file has all required variables
- [ ] `.gitignore` excludes `.env` and other sensitive files

### Code Review

- [ ] No hardcoded credentials in code
- [ ] No debug print statements in production code
- [ ] Error handling implemented for all critical paths
- [ ] Logging configured appropriately
- [ ] Comments and documentation are up to date
- [ ] No TODO or FIXME comments for critical issues

## Git Setup

- [ ] Git repository initialized (`git init`)
- [ ] All files added (`git add .`)
- [ ] Initial commit created (`git commit -m "Initial commit"`)
- [ ] GitHub repository created (bb723/asset-management-platform)
- [ ] Remote added (`git remote add origin <url>`)
- [ ] Code pushed to GitHub (`git push -u origin main`)
- [ ] Repository is accessible on GitHub

## Heroku Setup

### Create Applications

- [ ] Staging app created (`heroku create asset-mgmt-staging`)
- [ ] Production app created (`heroku create asset-mgmt-production`)
- [ ] Git remotes configured (staging, production)
- [ ] Remote verification (`git remote -v` shows all three remotes)

### Environment Configuration - Staging

#### Flask Configuration
- [ ] `FLASK_SECRET_KEY` set (unique, generated)
- [ ] `FLASK_ENV` set to `staging`
- [ ] `REDIRECT_URI` set to `https://asset-mgmt-staging.herokuapp.com/auth/callback`

#### Snowflake Configuration
- [ ] `SNOWFLAKE_USER` set to `your-snowflake-username`
- [ ] `SNOWFLAKE_PASSWORD` set (correct password)
- [ ] `SNOWFLAKE_ACCOUNT` set to `your-snowflake-account`
- [ ] `SNOWFLAKE_WAREHOUSE` set to `your-warehouse-name`
- [ ] `SNOWFLAKE_DATABASE` set to `your-database-name`
- [ ] `SNOWFLAKE_ROLE` set to `your-role-name`
- [ ] `SNOWFLAKE_SCHEMA` set to `PUBLIC`

#### Microsoft OAuth Configuration
- [ ] `MS_CLIENT_ID` set to `your-azure-client-id`
- [ ] `MS_CLIENT_SECRET` set (correct secret)
- [ ] `MS_TENANT_ID` set to `your-azure-tenant-id`

#### File Storage Configuration
- [ ] `UPLOAD_FOLDER` set to `./uploads`
- [ ] `MAX_CONTENT_LENGTH` set to `16777216`

#### Verification
- [ ] All config vars verified (`heroku config --remote staging`)
- [ ] No typos in variable names
- [ ] No missing values

### Environment Configuration - Production

#### Flask Configuration
- [ ] `FLASK_SECRET_KEY` set (unique, different from staging)
- [ ] `FLASK_ENV` set to `production`
- [ ] `REDIRECT_URI` set to `https://asset-mgmt-production.herokuapp.com/auth/callback`

#### Snowflake Configuration (Same as Staging)
- [ ] `SNOWFLAKE_USER` set
- [ ] `SNOWFLAKE_PASSWORD` set
- [ ] `SNOWFLAKE_ACCOUNT` set
- [ ] `SNOWFLAKE_WAREHOUSE` set
- [ ] `SNOWFLAKE_DATABASE` set
- [ ] `SNOWFLAKE_ROLE` set
- [ ] `SNOWFLAKE_SCHEMA` set

#### Microsoft OAuth Configuration (Same as Staging)
- [ ] `MS_CLIENT_ID` set
- [ ] `MS_CLIENT_SECRET` set
- [ ] `MS_TENANT_ID` set

#### File Storage Configuration (Same as Staging)
- [ ] `UPLOAD_FOLDER` set
- [ ] `MAX_CONTENT_LENGTH` set

#### Verification
- [ ] All config vars verified (`heroku config --remote production`)
- [ ] Secret keys are different between staging and production
- [ ] Redirect URIs are environment-specific

## Azure App Registration

- [ ] Azure portal accessed (https://portal.azure.com)
- [ ] Correct app registration found (Client ID: 909fcd82...)
- [ ] "Authentication" section accessed
- [ ] Staging redirect URI added: `https://asset-mgmt-staging.herokuapp.com/auth/callback`
- [ ] Production redirect URI added: `https://asset-mgmt-production.herokuapp.com/auth/callback`
- [ ] Changes saved
- [ ] API permissions verified (User.Read)
- [ ] Client secret is active and not expired

## Database Setup

- [ ] Production app deployed first (`git push production main`)
- [ ] Database initialization script run (`heroku run python scripts/init_db.py --remote production`)
- [ ] Script output shows success for all tables
- [ ] Tables verified in Snowflake UI or via CLI
- [ ] All 5 tables created: entities, buildings, budget_items, documents, share_tokens
- [ ] Indexes created successfully

## Staging Deployment

### Deployment
- [ ] Code pushed to staging (`git push staging main`)
- [ ] Build completed successfully (check logs)
- [ ] No build errors or warnings
- [ ] Dyno started successfully
- [ ] Application accessible via URL

### Testing
- [ ] Application loads (no 503 errors)
- [ ] Home page renders correctly
- [ ] Login button appears
- [ ] Clicking login redirects to Microsoft
- [ ] After Microsoft login, redirected back to app
- [ ] User name appears in navigation
- [ ] Can create entity
- [ ] Can edit entity
- [ ] Can delete entity
- [ ] Can create building
- [ ] Can edit building
- [ ] Can delete building
- [ ] Can view budget
- [ ] Can edit budget values
- [ ] Can save budget (AJAX call successful)
- [ ] Can view entity budget (aggregate)
- [ ] Can upload document
- [ ] Can download document
- [ ] Can delete document
- [ ] Can generate shareable link
- [ ] Shareable link works (no auth required)
- [ ] Shareable link shows correct data
- [ ] Logout works
- [ ] No JavaScript errors in browser console
- [ ] No Python errors in Heroku logs

### Performance
- [ ] Pages load within acceptable time (< 3 seconds)
- [ ] Budget save responds within acceptable time (< 2 seconds)
- [ ] No timeout errors
- [ ] Database queries execute successfully

## Production Deployment

### Pre-Deployment
- [ ] Staging fully tested and verified
- [ ] All critical bugs fixed
- [ ] Team notified of upcoming deployment
- [ ] Backup plan documented (rollback procedure)

### Deployment
- [ ] Code pushed to production (`git push production main`)
- [ ] Build completed successfully
- [ ] No build errors or warnings
- [ ] Dyno started successfully
- [ ] Application accessible via URL

### Testing (Same as Staging)
- [ ] Application loads
- [ ] Authentication works
- [ ] Entity CRUD operations work
- [ ] Building CRUD operations work
- [ ] Budget operations work
- [ ] Document operations work
- [ ] Shareable links work
- [ ] No errors in logs
- [ ] No JavaScript errors

### Post-Deployment
- [ ] Production URL shared with team
- [ ] Monitoring enabled (if applicable)
- [ ] Documentation updated
- [ ] Deployment logged in team records

## Post-Deployment Verification

### Functional Testing
- [ ] Complete user workflow tested end-to-end
- [ ] All major features working
- [ ] Error messages are user-friendly
- [ ] Flash messages appear correctly
- [ ] Navigation works as expected

### Performance Testing
- [ ] Application responds quickly
- [ ] No slow database queries
- [ ] No memory leaks
- [ ] Dyno metrics look healthy

### Security Testing
- [ ] Authentication required for protected routes
- [ ] Session management works correctly
- [ ] No sensitive data in URLs
- [ ] HTTPS enforced
- [ ] Share tokens work but don't expose sensitive data

### Browser Compatibility
- [ ] Works in Chrome
- [ ] Works in Firefox
- [ ] Works in Safari
- [ ] Works in Edge
- [ ] Mobile responsive (basic testing)

## Documentation

- [ ] README.md is up to date
- [ ] DEPLOYMENT.md is complete
- [ ] QUICKSTART.md is accurate
- [ ] PROJECT_SUMMARY.md reflects current state
- [ ] ARCHITECTURE.md is current
- [ ] All URLs updated to production URLs
- [ ] Team documentation updated (if applicable)

## Integration (Optional)

- [ ] Link added to Foundation Dashboard (if desired)
- [ ] Environment variable set in Foundation Dashboard
- [ ] Navigation link tested
- [ ] Single sign-on works between apps

## Monitoring Setup (Recommended)

- [ ] Log drain configured (Papertrail, Splunk, etc.)
- [ ] Uptime monitoring enabled (Pingdom, UptimeRobot, etc.)
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Performance monitoring enabled (New Relic, Datadog, etc.)
- [ ] Alerts configured for critical errors

## Team Communication

- [ ] Deployment announced to team
- [ ] Production URL shared
- [ ] User guide provided (if needed)
- [ ] Support contact information shared
- [ ] Known issues documented (if any)

## Rollback Plan

Document rollback procedure in case of issues:

- [ ] Rollback command documented: `heroku rollback v<previous-version> --remote production`
- [ ] Previous working version identified
- [ ] Rollback tested on staging
- [ ] Team knows who can execute rollback
- [ ] Communication plan for rollback

## Future Enhancements

Document planned improvements:

- [ ] S3 integration for file storage (persistent uploads)
- [ ] Email notifications for share links
- [ ] Excel export for budgets
- [ ] Audit logging for all changes
- [ ] Additional user roles and permissions
- [ ] API layer for integrations
- [ ] Mobile app (future consideration)

## Sign-Off

### Technical Review
- [ ] Developer review completed
- [ ] Code quality approved
- [ ] Security review passed
- [ ] Performance acceptable

### Business Review
- [ ] Meets business requirements
- [ ] User acceptance testing passed
- [ ] Stakeholder approval received

### Deployment Approval
- [ ] Staging deployment approved
- [ ] Production deployment approved
- [ ] Go-live date confirmed

---

## Quick Reference

### Useful Commands

```bash
# View logs
heroku logs --tail --remote production

# Check config
heroku config --remote production

# Restart dynos
heroku restart --remote production

# Check dyno status
heroku ps --remote production

# Run database script
heroku run python scripts/init_db.py --remote production

# Access Heroku console
heroku run bash --remote production

# Scale dynos
heroku ps:scale web=1 --remote production

# View releases
heroku releases --remote production

# Rollback
heroku rollback v<version> --remote production
```

### Important URLs

- **GitHub Repository**: https://github.com/bb723/asset-management-platform
- **Staging**: https://asset-mgmt-staging.herokuapp.com
- **Production**: https://asset-mgmt-production.herokuapp.com
- **Azure Portal**: https://portal.azure.com
- **Heroku Dashboard**: https://dashboard.heroku.com

### Support Contacts

- **Developer**: Brett (bb723)
- **GitHub Issues**: https://github.com/bb723/asset-management-platform/issues
- **Foundation Package**: https://github.com/bb723/foundation

---

**Deployment Date**: _________________

**Deployed By**: _________________

**Version**: _________________

**Status**: [ ] Staging  [ ] Production  [ ] Complete

**Notes**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
