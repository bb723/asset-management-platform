# Quick Start Guide

Get the Asset Management Platform running locally in 5 minutes.

## Prerequisites

- Python 3.10+ installed
- Git installed
- Internet connection

## Steps

### 1. Clone and Navigate

```bash
cd c:\Users\brett\OneDrive\Desktop\projects\foundation-asset-management
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The foundation package installation may take a few minutes as it's installed from GitHub.

### 4. Configure Environment

The `.env` file is already created with all credentials. You just need to generate a Flask secret key:

```bash
# Generate a secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and replace `your-secret-key-change-this-in-production` in [.env](.env) with the generated key.

### 5. Initialize Database (One-Time)

```bash
python scripts/init_db.py
```

Expected output:
```
============================================================
Asset Management Platform - Database Initialization
============================================================

Connecting to Snowflake...
✓ Connected to Snowflake
...
✓ Database initialization completed successfully
```

### 6. Run the Application

```bash
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

### 7. Access the Application

Open your browser and go to: **http://localhost:5000**

You should see the login page. Click "Login" to authenticate with Microsoft.

## First-Time Setup

After logging in for the first time:

1. **Create an Entity**
   - Click "New Entity"
   - Name: "Test Entity"
   - Description: "My first test entity"
   - Click "Create Entity"

2. **Add a Building**
   - Click "Add Building"
   - Name: "Test Building"
   - Address: "123 Main St"
   - Click "Add Building"

3. **Manage Budget**
   - Click on the building
   - Click "Manage Budget"
   - Edit some values
   - Click "Save Budget"

4. **Upload a Document**
   - Click "Documents" tab
   - Click "Upload Document"
   - Select category and file
   - Click "Upload"

5. **Generate Shareable Link**
   - Go back to entity view
   - Click "Generate Shareable Link"
   - Copy the link and open in incognito/private window
   - You should see the public view (no login required)

## Troubleshooting

### Issue: `pip install` fails

**Solution**: Make sure you have an active internet connection and try again. The foundation package is hosted on GitHub.

### Issue: Database initialization fails

**Solution**:
1. Check your Snowflake credentials in `.env`
2. Verify you have network access to Snowflake
3. Check that the ETL_USER has proper permissions

### Issue: Authentication fails

**Solution**:
1. Make sure you're using the correct Microsoft account
2. Clear browser cache and cookies
3. Try using incognito/private mode
4. Verify the Azure app registration has the correct redirect URI

### Issue: Port 5000 is already in use

**Solution**:
```bash
# Find what's using port 5000 (Windows)
netstat -ano | findstr :5000

# Kill the process (replace PID with the actual process ID)
taskkill /PID <PID> /F

# Or use a different port
export PORT=5001  # Mac/Linux
set PORT=5001     # Windows
python app.py
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions
- Explore the codebase in your IDE

## Stopping the Application

Press `Ctrl+C` in the terminal where the app is running.

To deactivate the virtual environment:
```bash
deactivate
```

## Need Help?

- Check the logs in the terminal for error messages
- Review the code comments in `app.py`
- Consult [README.md](README.md) for detailed information
- Check [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
