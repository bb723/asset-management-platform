#!/bin/bash
# Deployment script for Asset Management Platform

echo "=========================================="
echo "Asset Management Platform - Deployment"
echo "=========================================="

# Push to GitHub
echo ""
echo "1. Pushing to GitHub..."
git push origin main

if [ $? -ne 0 ]; then
    echo "❌ GitHub push failed!"
    exit 1
fi
echo "✅ GitHub push successful"

# Deploy to Staging
echo ""
echo "2. Deploying to Staging..."
git push staging main

if [ $? -ne 0 ]; then
    echo "❌ Staging deployment failed!"
    exit 1
fi
echo "✅ Staging deployed"

# Prompt for production
echo ""
echo "3. Staging deployment complete."
echo ""
read -p "Deploy to production? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deploying to production..."
    git push production main

    if [ $? -ne 0 ]; then
        echo "❌ Production deployment failed!"
        exit 1
    fi
    echo "✅ Production deployed"
    echo ""
    echo "🎉 Deployment complete!"
    echo "Staging: https://asset-mgmt-staging.herokuapp.com"
    echo "Production: https://asset-mgmt-production.herokuapp.com"
else
    echo "Production deployment skipped."
    echo "To deploy later, run: git push production main"
fi
