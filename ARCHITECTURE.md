# Asset Management Platform - Architecture Documentation

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│  (Chrome, Firefox, Safari, Edge)                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTPS
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    Heroku Platform                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Flask Application (app.py)                   │  │
│  │                                                       │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │   Routes & Controllers                       │   │  │
│  │  │   - Entity Management                        │   │  │
│  │  │   - Building Management                      │   │  │
│  │  │   - Budget Management                        │   │  │
│  │  │   - Document Management                      │   │  │
│  │  │   - Shareable Links                          │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  │                                                       │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │   Authentication Layer                       │   │  │
│  │  │   - Microsoft OAuth (MSAL)                   │   │  │
│  │  │   - Session Management                       │   │  │
│  │  │   - @login_required Decorator                │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  │                                                       │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │   Business Logic                             │   │  │
│  │  │   - database/queries.py                      │   │  │
│  │  │   - models/ (Entity, Building, Budget, Doc)  │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
         ▼              ▼              ▼
┌────────────────┐ ┌──────────┐ ┌─────────────┐
│  Azure Active  │ │Snowflake │ │   Heroku    │
│   Directory    │ │ Database │ │ Filesystem  │
│    (OAuth)     │ │          │ │  (Uploads)  │
└────────────────┘ └──────────┘ └─────────────┘
```

## Component Architecture

### 1. Frontend Layer

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Stack                        │
├─────────────────────────────────────────────────────────┤
│  Bootstrap 5.3.0                                        │
│  - Responsive grid system                               │
│  - Pre-built components (cards, modals, forms)          │
│  - Utilities and helpers                                │
├─────────────────────────────────────────────────────────┤
│  Bootstrap Icons 1.11.0                                 │
│  - Icon font library                                    │
│  - 2000+ icons                                          │
├─────────────────────────────────────────────────────────┤
│  jQuery 3.7.0                                           │
│  - AJAX calls                                           │
│  - DOM manipulation                                     │
│  - Event handling                                       │
├─────────────────────────────────────────────────────────┤
│  Custom JavaScript (budget.js)                          │
│  - Budget calculations                                  │
│  - Budget save/load                                     │
│  - Table interactivity                                  │
├─────────────────────────────────────────────────────────┤
│  Custom CSS (styles.css)                                │
│  - Budget table styling                                 │
│  - Responsive adjustments                               │
│  - Custom animations                                    │
└─────────────────────────────────────────────────────────┘
```

### 2. Backend Layer

```
┌─────────────────────────────────────────────────────────┐
│                   Flask Application                      │
├─────────────────────────────────────────────────────────┤
│  app.py (Main Application)                              │
│  - Route handlers (24+ routes)                          │
│  - Authentication logic                                 │
│  - Error handlers (404, 500, 413)                       │
│  - Template filters                                     │
│  - Session configuration                                │
├─────────────────────────────────────────────────────────┤
│  Models Layer (models/)                                 │
│  - entity.py: Entity dataclass                          │
│  - building.py: Building dataclass                      │
│  - budget.py: BudgetItem dataclass                      │
│  - document.py: Document dataclass                      │
│  - from_dict() and to_dict() methods                    │
├─────────────────────────────────────────────────────────┤
│  Database Layer (database/)                             │
│  - queries.py: All SQL query functions                  │
│  - schema.sql: DDL statements                           │
│  - Uses foundation.clients.SnowflakeClient              │
│  - Parameterized queries (SQL injection prevention)     │
├─────────────────────────────────────────────────────────┤
│  Templates (templates/)                                 │
│  - Jinja2 templates                                     │
│  - Template inheritance (base.html)                     │
│  - 13 template files                                    │
└─────────────────────────────────────────────────────────┘
```

### 3. Data Layer

```
┌─────────────────────────────────────────────────────────┐
│               Snowflake Database                         │
│         your-database-name.PUBLIC Schema                │
├─────────────────────────────────────────────────────────┤
│  entities                                               │
│  - entity_id (PK)                                       │
│  - name, description                                    │
│  - created_at, updated_at                               │
├─────────────────────────────────────────────────────────┤
│  buildings                                              │
│  - building_id (PK)                                     │
│  - entity_id (FK → entities)                            │
│  - name, address                                        │
│  - created_at, updated_at                               │
├─────────────────────────────────────────────────────────┤
│  budget_items                                           │
│  - budget_item_id (PK)                                  │
│  - building_id (FK → buildings)                         │
│  - month_year, category, amount, notes                  │
│  - created_at, updated_at                               │
│  - UNIQUE(building_id, month_year, category)            │
├─────────────────────────────────────────────────────────┤
│  documents                                              │
│  - document_id (PK)                                     │
│  - building_id (FK → documents)                         │
│  - category, filename, file_path, file_size             │
│  - uploaded_by, uploaded_at                             │
├─────────────────────────────────────────────────────────┤
│  share_tokens                                           │
│  - token (PK)                                           │
│  - entity_id (FK → entities)                            │
│  - created_at, expires_at                               │
└─────────────────────────────────────────────────────────┘
```

## Authentication Flow

```
┌────────┐                                    ┌──────────────┐
│ User   │                                    │  Flask App   │
└───┬────┘                                    └──────┬───────┘
    │                                                │
    │  1. Click "Login"                              │
    ├───────────────────────────────────────────────>│
    │                                                │
    │  2. Generate state & redirect to Azure AD     │
    │<───────────────────────────────────────────────┤
    │                                                │
    │                                   ┌────────────▼─────────┐
    │  3. Login with Microsoft          │   Azure AD (MSAL)    │
    ├──────────────────────────────────>│                      │
    │                                   │  - Verify credentials│
    │  4. Authorization code + state    │  - Issue auth code   │
    │<──────────────────────────────────┤                      │
    │                                   └────────────┬─────────┘
    │                                                │
    │  5. Exchange code for token                    │
    ├───────────────────────────────────────────────>│
    │                                                │
    │  6. Verify state & extract user info           │
    │                                                │
    │  7. Store user in session                      │
    │                                                │
    │  8. Redirect to home page                      │
    │<───────────────────────────────────────────────┤
    │                                                │
    │  9. Access protected routes                    │
    │     (@login_required decorator)                │
    ├───────────────────────────────────────────────>│
    │                                                │
```

## Request Flow

### Authenticated Request Flow

```
1. User Request
   ↓
2. Flask Route Handler
   ↓
3. @login_required Decorator
   ↓ (checks session['user']['authenticated'])
   ↓
4. Business Logic
   ↓
5. Database Query (database/queries.py)
   ↓
6. SnowflakeClient (foundation package)
   ↓
7. Snowflake Database
   ↓
8. Results returned up the chain
   ↓
9. Template Rendering (Jinja2)
   ↓
10. HTML Response to User
```

### Budget Save Flow (AJAX)

```
1. User edits budget values in table
   ↓
2. Click "Save Budget" button
   ↓
3. JavaScript collects all values
   ↓
4. AJAX POST to /buildings/<id>/budget/save
   ↓
5. Flask receives JSON data
   ↓
6. Validates data
   ↓
7. Calls bulk_upsert_budget_items()
   ↓
8. MERGE statements in Snowflake
   ↓
9. Returns JSON response
   ↓
10. JavaScript updates UI
   ↓
11. Shows success message
```

### Document Upload Flow

```
1. User selects file and category
   ↓
2. Submit form (multipart/form-data)
   ↓
3. Flask receives file
   ↓
4. Validate file type and size
   ↓
5. Secure filename with werkzeug
   ↓
6. Save to uploads/<building_id>/filename
   ↓
7. Create document record in database
   ↓
8. Show success message
   ↓
9. Redirect to documents list
```

### Shareable Link Flow

```
1. User clicks "Generate Shareable Link"
   ↓
2. Check if token exists for entity
   ↓
3. If not, generate secure token (secrets.token_urlsafe(32))
   ↓
4. Store in share_tokens table (365-day expiration)
   ↓
5. Return URL: /shared/<token>
   ↓
6. User copies and shares URL
   ↓
7. External user visits URL (NO AUTH REQUIRED)
   ↓
8. Verify token and check expiration
   ↓
9. Load entity and budget data
   ↓
10. Render public_view.html (read-only)
```

## Data Flow Diagrams

### Entity → Buildings → Budget Relationship

```
┌─────────────────────┐
│      Entity         │
│  - entity_id (PK)   │
│  - name             │
│  - description      │
└──────────┬──────────┘
           │
           │ 1:N
           │
┌──────────▼──────────┐
│     Building        │
│  - building_id (PK) │
│  - entity_id (FK)   │
│  - name             │
│  - address          │
└──────────┬──────────┘
           │
           │ 1:N
           │
┌──────────▼──────────┐
│   Budget Item       │
│  - budget_item_id   │
│  - building_id (FK) │
│  - month_year       │
│  - category         │
│  - amount           │
└─────────────────────┘
```

### Budget Categories Structure

```
Building Budget (24 months)
├── Revenue
│   └── Monthly values (24 months)
├── Operating Expenses
│   └── Monthly values (24 months)
├── Debt Service
│   └── Monthly values (24 months)
├── Capital Expenses
│   └── Monthly values (24 months)
└── Net Operating Income (calculated)
    └── Monthly values (24 months)

Entity Budget = SUM(All Building Budgets)
```

## Security Architecture

### Authentication Security

```
1. OAuth 2.0 with Microsoft Azure AD
   - Industry standard authentication
   - No password storage
   - Token-based authentication

2. Session Security
   - Secure cookies (httponly, secure, samesite)
   - Session timeout (7 days)
   - State verification (CSRF protection)

3. Authorization
   - @login_required decorator on all routes (except /shared/<token>)
   - Session-based access control
   - No role-based access (all authenticated users have full access)
```

### Data Security

```
1. SQL Injection Prevention
   - Parameterized queries (all queries use %s placeholders)
   - No string concatenation in SQL
   - Snowflake client handles escaping

2. File Upload Security
   - File type validation (whitelist)
   - File size limit (16MB)
   - Secure filename generation (werkzeug)
   - Isolated storage (per-building folders)

3. Share Token Security
   - Cryptographically secure tokens (secrets.token_urlsafe(32))
   - 365-day expiration
   - Read-only access
   - No sensitive data exposed
```

### Transport Security

```
1. HTTPS Everywhere
   - Heroku enforces HTTPS
   - Secure cookies
   - No mixed content

2. API Security
   - Same-origin policy
   - CORS not enabled (no cross-origin access)
   - CSRF protection via session state
```

## Deployment Architecture

### Heroku Infrastructure

```
┌───────────────────────────────────────────────────────────┐
│                  Heroku Platform                           │
├───────────────────────────────────────────────────────────┤
│  Web Dyno (Standard-1X or higher)                         │
│  - Python 3.10                                            │
│  - Gunicorn WSGI server                                   │
│  - Flask application                                      │
│  - Ephemeral filesystem (uploads lost on restart)         │
├───────────────────────────────────────────────────────────┤
│  Environment Variables (Config Vars)                       │
│  - 15 environment variables                               │
│  - Secure storage                                         │
│  - No version control                                     │
├───────────────────────────────────────────────────────────┤
│  Automatic HTTPS                                          │
│  - SSL/TLS termination                                    │
│  - Certificate management                                 │
└───────────────────────────────────────────────────────────┘
```

### Environment Separation

```
Development (Local)
- localhost:5000
- Local Snowflake connection
- Development Azure redirect URI
- Debug mode enabled

Staging (Heroku)
- asset-mgmt-staging.herokuapp.com
- Shared Snowflake database
- Staging Azure redirect URI
- Debug mode disabled

Production (Heroku)
- asset-mgmt-production.herokuapp.com
- Shared Snowflake database
- Production Azure redirect URI
- Debug mode disabled
- Monitored logs
```

## Technology Decisions

### Why Flask?

- Lightweight and flexible
- Easy to get started
- Great for MVPs
- Excellent documentation
- Large ecosystem
- Python (team familiarity)

### Why Snowflake?

- Already in use by organization
- Excellent performance
- SQL-based (familiar)
- Cloud-native
- Scales automatically
- foundation package provides client

### Why Bootstrap?

- Rapid development
- Responsive out-of-the-box
- Professional look
- Large component library
- Good documentation
- CDN-hosted (no bundle needed)

### Why Microsoft OAuth?

- Organization uses Azure AD
- Single sign-on
- No password management
- Industry standard
- Secure and reliable
- foundation package provides integration

### Why Heroku?

- Easy deployment
- Git-based workflow
- Automatic SSL
- Environment variable management
- Logging and monitoring
- Scales easily

## Performance Considerations

### Database Performance

```
Optimizations:
- Indexes on foreign keys
- Efficient query design
- Batch operations (bulk_upsert_budget_items)
- Parameterized queries (query plan caching)

Considerations:
- Snowflake warehouse costs per query
- Connection pooling (future enhancement)
- Query result caching (future enhancement)
```

### Frontend Performance

```
Optimizations:
- CDN-hosted libraries (Bootstrap, jQuery)
- Minimal custom JavaScript
- Client-side budget calculations
- Lazy loading of document lists

Considerations:
- Large budget tables (24 months × 5 categories)
- File upload progress indicators (future)
- Image optimization for documents (future)
```

### Application Performance

```
Optimizations:
- Session-based auth (no DB lookup on every request)
- Direct database access (no API layer overhead)
- Efficient query patterns

Considerations:
- Heroku dyno startup time (cold starts)
- Ephemeral filesystem (uploads)
- Single dyno deployment (future: scale horizontally)
```

## Scalability

### Current Limitations

1. **Single Dyno**: One web process handles all requests
2. **Ephemeral Filesystem**: File uploads lost on dyno restart
3. **No Caching**: No Redis or memcached
4. **Session Storage**: In-memory sessions (lost on restart)

### Scaling Strategies

```
Horizontal Scaling:
- Add more dynos (heroku ps:scale web=3)
- Requires session storage solution (Redis)
- Requires file storage solution (S3)

Vertical Scaling:
- Upgrade dyno type (Standard-1X → Standard-2X)
- More memory and CPU
- Handles more concurrent requests

Database Scaling:
- Snowflake auto-scales
- Consider warehouse size optimization
- Implement connection pooling
```

## Monitoring and Logging

### Current Logging

```
Application Logs:
- INFO level logging
- Structured format
- Request/response logging
- Error logging with stack traces

Heroku Logs:
- heroku logs --tail --remote production
- Router logs (request routing)
- Application logs (print/logger output)
- System logs (dyno events)

Log Retention:
- Heroku: Last 1,500 lines
- Recommend: Add log drain (Papertrail, Splunk, etc.)
```

### Recommended Monitoring

```
Application Monitoring:
- New Relic or Datadog (APM)
- Error tracking (Sentry)
- Uptime monitoring (Pingdom, UptimeRobot)

Database Monitoring:
- Snowflake query history
- Warehouse utilization
- Query performance

User Analytics:
- Google Analytics (optional)
- User flow tracking
- Feature usage metrics
```

## Maintenance and Operations

### Regular Maintenance

```
Weekly:
- Review application logs
- Check for errors
- Monitor performance

Monthly:
- Update dependencies (security patches)
- Review Snowflake costs
- Check disk usage (uploaded files)

Quarterly:
- Security audit
- Performance optimization
- User feedback review
```

### Backup and Recovery

```
Database:
- Snowflake Time Travel (90 days)
- No manual backups needed

Application Code:
- GitHub repository (versioned)
- Heroku release history

Files:
- No backup (ephemeral filesystem)
- Recommend: S3 integration for persistence

Configuration:
- Environment variables documented in DEPLOYMENT.md
- Can be restored from documentation
```

---

**Last Updated**: 2025-10-27
