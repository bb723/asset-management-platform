@echo off
REM Deployment script for Asset Management Platform (Windows)

echo ==========================================
echo Asset Management Platform - Deployment
echo ==========================================

REM Push to GitHub
echo.
echo 1. Pushing to GitHub...
git push origin main

if %errorlevel% neq 0 (
    echo X GitHub push failed!
    exit /b 1
)
echo √ GitHub push successful

REM Deploy to Staging
echo.
echo 2. Deploying to Staging...
git push staging main

if %errorlevel% neq 0 (
    echo X Staging deployment failed!
    exit /b 1
)
echo √ Staging deployed

REM Prompt for production
echo.
echo 3. Staging deployment complete.
echo.
set /p deploy_prod="Deploy to production? (y/n): "

if /i "%deploy_prod%"=="y" (
    echo Deploying to production...
    git push production main

    if %errorlevel% neq 0 (
        echo X Production deployment failed!
        exit /b 1
    )
    echo √ Production deployed
    echo.
    echo Deployment complete!
    echo Staging: https://asset-mgmt-staging.herokuapp.com
    echo Production: https://asset-mgmt-production.herokuapp.com
) else (
    echo Production deployment skipped.
    echo To deploy later, run: git push production main
)
