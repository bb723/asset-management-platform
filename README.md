# Asset Management Platform

A comprehensive Flask-based web application for managing property entities, buildings, budgets, and documents for Standard Management Company.

## Features

### Entity Management
- Create and manage property management entities
- View entity details and associated buildings
- Edit entity information and descriptions
- Delete entities (with cascade to buildings and data)

### Building Management
- Add buildings to entities
- Track building addresses and details
- Manage building-specific budgets and documents
- Edit and delete buildings

### Budget Management
- 24-month rolling budget for each building
- Spreadsheet-like interface for easy editing
- Multiple budget categories:
  - Revenue
  - Operating Expenses
  - Debt Service
  - Capital Expenses
  - Net Operating Income
- Aggregate budget view at entity level
- Real-time calculations and totals
- Auto-save with change tracking

### Document Management
- Upload and organize documents by category:
  - Insurance Binders
  - Loan Documents
  - Management Agreements
  - HVAC Service Contracts
  - Lawn Care & Plowing Contracts
  - Tax Bills
  - Water/Sewer Bills
  - Electric Bills
  - Other
- Download documents
- Track upload history and file metadata
- Delete documents

### Shareable Links
- Generate secure, shareable links for entities
- Public view with no authentication required
- Read-only access to entity and budget data
- Professional presentation for external stakeholders
- 365-day token expiration

### Authentication
- Microsoft OAuth (Azure AD) integration
- Session-based authentication
- Secure state management
- User profile display

## Architecture

### Technology Stack
- **Backend**: Flask 3.0
- **Database**: Snowflake (your-database-name.PUBLIC schema)
- **Authentication**: Microsoft OAuth via foundation package
- **Frontend**: Bootstrap 5, jQuery
- **Deployment**: Heroku
- **Python**: 3.10

### Architecture Pattern
This application follows a **Standalone App with Direct Database Access** pattern:

```
Asset Management Platform
  ↓ (Direct SQL via foundation.clients.SnowflakeClient)
Snowflake Database (your-database-name.PUBLIC schema)
```

No API dependencies on other applications. All data access is direct to Snowflake.

## Project Structure

```
asset-management-platform/
├── app.py                       # Main Flask application
├── requirements.txt             # Python dependencies
├── Procfile                     # Heroku configuration
├── runtime.txt                  # Python version
├── .env                         # Local environment variables (not committed)
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore patterns
├── README.md                    # This file
├── DEPLOYMENT.md                # Deployment guide
├── models/                      # Data models
│   ├── __init__.py
│   ├── entity.py               # Entity model
│   ├── building.py             # Building model
│   ├── budget.py               # Budget model
│   └── document.py             # Document model
├── database/                    # Database layer
│   ├── __init__.py
│   ├── schema.sql              # Snowflake schema
│   └── queries.py              # Database queries
├── scripts/                     # Utility scripts
│   └── init_db.py              # Database initialization
├── templates/                   # HTML templates
│   ├── base.html               # Base template
│   ├── error.html              # Error page
│   ├── entity/                 # Entity templates
│   ├── building/               # Building templates
│   ├── budget/                 # Budget templates
│   ├── documents/              # Document templates
│   └── shared/                 # Shareable view templates
└── static/                      # Static assets
    ├── css/
    │   └── styles.css
    └── js/
        └── budget.js
```

## Local Development Setup

### Prerequisites
- Python 3.10+
- Git
- Heroku CLI (for deployment)
- Access to Snowflake database
- Microsoft Azure app credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bb723/asset-management-platform.git
   cd asset-management-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy example file
   copy .env.example .env

   # Edit .env and add your credentials
   # Generate a new FLASK_SECRET_KEY:
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. **Initialize database**
   ```bash
   python scripts/init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open your browser to: http://localhost:5000

### Environment Variables

See `.env.example` for all required environment variables:

- **Microsoft OAuth**: MS_CLIENT_ID, MS_CLIENT_SECRET, MS_TENANT_ID
- **Flask**: FLASK_SECRET_KEY, FLASK_ENV, REDIRECT_URI
- **Snowflake**: SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT, etc.
- **File Storage**: UPLOAD_FOLDER, MAX_CONTENT_LENGTH

## Usage

### Creating an Entity
1. Log in with Microsoft account
2. Click "New Entity" button
3. Fill in entity name and description
4. Submit form

### Adding Buildings
1. Navigate to entity view
2. Click "Add Building"
3. Enter building name and address
4. Submit form

### Managing Budgets
1. Navigate to building view
2. Click "Budget" tab or "Manage Budget"
3. Edit budget values directly in the table
4. Click "Save Budget" to persist changes
5. View aggregate budget at entity level

### Uploading Documents
1. Navigate to building view
2. Click "Documents" tab
3. Click "Upload Document"
4. Select category and file
5. Submit form

### Sharing with Stakeholders
1. Navigate to entity view
2. Click "Generate Shareable Link"
3. Copy the generated URL
4. Share with external stakeholders (no login required)

## Database Schema

The application uses the following Snowflake tables in `your-database-name.PUBLIC`:

- **entities**: Property management entities
- **buildings**: Physical buildings/properties
- **budget_items**: Monthly budget line items
- **documents**: Uploaded documents metadata
- **share_tokens**: Shareable link tokens

See `database/schema.sql` for complete schema definition.

## Error Handling

The application implements comprehensive error handling:
- Flash messages for user feedback
- Logging at INFO level
- Graceful error pages (404, 500)
- Transaction management for critical operations
- Batch operation results tracking

## Security Features

- Microsoft OAuth authentication
- Session-based authentication with secure cookies
- SQL injection prevention (parameterized queries)
- File upload validation (type and size)
- CSRF protection
- Secure shareable tokens (URL-safe, 32 bytes)

## Testing

To test the application locally:

1. Start the local server: `python app.py`
2. Test authentication flow
3. Create test entities and buildings
4. Test budget editing and saving
5. Upload test documents
6. Generate and test shareable links

## Deployment

### Quick Deploy Workflow

**Heroku Pipeline**: `foundation-asset-management` (connected to GitHub `bb723/asset-management-platform`)

1. **Push to GitHub** (triggers automatic staging deployment)
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

2. **Test on staging**
   ```bash
   heroku open --app asset-mgmt-staging
   heroku logs --tail --app asset-mgmt-staging
   ```

3. **Promote to production** (after thorough testing)
   ```bash
   heroku pipelines:promote --app asset-mgmt-staging
   heroku open --app asset-mgmt-production
   ```

### Applications

- **Staging**: `asset-mgmt-staging` (auto-deploys from GitHub main branch)
  - URL: https://asset-mgmt-staging.herokuapp.com
  - Purpose: Testing and validation before production

- **Production**: `asset-mgmt-production` (promoted from staging)
  - URL: https://asset-mgmt-production.herokuapp.com
  - Purpose: Live production environment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions including:
- Git setup
- Heroku pipeline configuration
- Environment variables
- Database initialization
- Azure app registration updates

## Troubleshooting

### Common Issues

**Authentication fails**
- Verify MS_CLIENT_ID, MS_CLIENT_SECRET, MS_TENANT_ID
- Check REDIRECT_URI matches Azure app registration
- Ensure cookies are enabled

**Database connection fails**
- Verify Snowflake credentials
- Check network connectivity
- Ensure proper role and warehouse permissions

**File upload fails**
- Check UPLOAD_FOLDER exists and is writable
- Verify file size is under MAX_CONTENT_LENGTH (16MB)
- Ensure file type is in allowed extensions

**Budget save fails**
- Check browser console for JavaScript errors
- Verify network connectivity
- Check server logs for database errors

## Contributing

This is an internal Standard Management Company application. For changes or improvements:

1. **Create a feature branch** (optional for larger features)
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test locally**
   ```bash
   python app.py
   # Test at http://localhost:5000
   ```

3. **Commit and push to GitHub**
   ```bash
   git add .
   git commit -m "Add feature: description"
   git push origin main  # or merge feature branch to main
   ```

4. **Automatic deployment to staging**
   - Heroku automatically deploys when you push to GitHub main branch

5. **Test thoroughly on staging**
   ```bash
   heroku open --app asset-mgmt-staging
   ```

6. **Promote to production** (after validation)
   ```bash
   heroku pipelines:promote --app asset-mgmt-staging
   ```

## License

Proprietary - Standard Management Company

## Support

For issues or questions:
- Check logs: `heroku logs --tail --remote production`
- Review error messages in browser console
- Contact development team

## Related Applications

- **propertyops-pipeline**: ETL pipeline for property operations data
- **foundation-dashboard**: Main dashboard application
- **foundation**: Shared package for auth and database clients

## Version History

- **v1.0.0** (2025-01): Initial release
  - Entity management
  - Building management
  - 24-month budgets
  - Document management
  - Shareable links
  - Microsoft OAuth authentication
