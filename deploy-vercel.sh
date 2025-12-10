#!/bin/bash

# Deployment script for Vercel (Linux/Mac)

echo "Deploying Hand Gesture Recognition App to Vercel..."
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI globally..."
    npm install -g vercel
fi

# Initialize git if not already done
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Ready for Vercel deployment"
fi

# Deploy to Vercel
echo ""
echo "Starting Vercel deployment..."
vercel

echo ""
echo "Deployment complete!"
echo ""
echo "Your app will be available at: https://your-project-name.vercel.app"
echo "Check https://vercel.com/dashboard for your deployment URL"
