# Azure App Registration Setup

## Your Application Details

- **Client ID**: `your-azure-client-id`
- **Tenant ID**: `your-azure-tenant-id`
- **Production URL**: `https://asset-mgmt-production-d0b9c7434d7d.herokuapp.com`

## Step-by-Step: Add Redirect URI

### 1. Access Azure Portal

Go to: https://portal.azure.com

### 2. Navigate to App Registration

1. Click "Azure Active Directory" (or search for it)
2. Click "App registrations" in the left menu
3. Click "All applications"
4. Find your app with Client ID: `your-azure-client-id`

### 3. Add Redirect URIs

1. Click "Authentication" in the left menu
2. Under "Platform configurations" → "Web" → "Redirect URIs"
3. Click "Add URI"
4. Add this URL:
   ```
   https://asset-mgmt-production-d0b9c7434d7d.herokuapp.com/auth/callback
   ```
5. Click "Save" at the bottom

### 4. Verify Configuration

Make sure you have:
- ✅ Redirect URI added for production
- ✅ "Access tokens" is checked (under Implicit grant and hybrid flows)
- ✅ "ID tokens" is checked (under Implicit grant and hybrid flows)

## Update Heroku Config

After adding the redirect URI in Azure, update your Heroku config:

```powershell
# Production
heroku config:set REDIRECT_URI=https://asset-mgmt-production-d0b9c7434d7d.herokuapp.com/auth/callback --remote production

# Verify it's set
heroku config:get REDIRECT_URI --remote production
```

## Testing Authentication

1. Open your app: https://asset-mgmt-production-d0b9c7434d7d.herokuapp.com
2. Click "Login"
3. You should be redirected to Microsoft login
4. After signing in, you should be redirected back to your app
5. You should see your name in the navigation bar

## Troubleshooting

### Issue: "AADSTS50011: The reply URL specified in the request does not match..."

**Cause**: The redirect URI in Azure doesn't match your Heroku URL

**Fix**:
1. Check the exact URL in the error message
2. Add that exact URL to Azure redirect URIs
3. Make sure there are no typos or extra characters

### Issue: "State mismatch in OAuth callback"

**Cause**: Session cookies not being preserved

**Fix**:
1. Clear browser cache and cookies
2. Try in incognito/private mode
3. Check that cookies are enabled

### Issue: Authentication succeeds but then fails

**Cause**: REDIRECT_URI config var doesn't match actual Heroku URL

**Fix**:
```powershell
heroku config:set REDIRECT_URI=https://asset-mgmt-production-d0b9c7434d7d.herokuapp.com/auth/callback --remote production
heroku restart --remote production
```

## Current Redirect URIs Needed

Add these to Azure (if you have staging):

1. **Production**:
   ```
   https://asset-mgmt-production-d0b9c7434d7d.herokuapp.com/auth/callback
   ```

2. **Staging** (if you deployed it):
   ```
   https://asset-mgmt-staging-<your-hash>.herokuapp.com/auth/callback
   ```

3. **Local Development**:
   ```
   http://localhost:5000/auth/callback
   ```

## Screenshot of Azure Configuration

Your "Authentication" section should look like this:

```
Platform configurations
  Web
    Redirect URIs
      ✓ https://asset-mgmt-production-d0b9c7434d7d.herokuapp.com/auth/callback
      ✓ http://localhost:5000/auth/callback

    Front-channel logout URL: (leave blank)

Implicit grant and hybrid flows
  ✓ Access tokens
  ✓ ID tokens
```

---

**After completing these steps, restart your app:**

```powershell
heroku restart --remote production
```

Then try logging in again!
