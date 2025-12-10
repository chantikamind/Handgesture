# Hand Gesture Recognition - Vercel Deployment Guide

## Prerequisites

1. **Vercel Account** - Sign up at https://vercel.com
2. **GitHub Account** - Your repository should be on GitHub
3. **Git installed** locally

## Deployment Steps

### Step 1: Push to GitHub

```bash
cd C:\Users\MSI\Handgesture
git init
git add .
git commit -m "Initial commit - Ready for Vercel deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Handgesture.git
git push -u origin main
```

### Step 2: Deploy to Vercel

**Option A: Using Vercel CLI**

```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to project directory
cd C:\Users\MSI\Handgesture

# Deploy
vercel
```

**Option B: Using Vercel Dashboard**

1. Go to https://vercel.com/new
2. Connect your GitHub account
3. Select the Handgesture repository
4. Click "Import"
5. Configure project settings:
   - **Framework**: Other
   - **Root Directory**: ./
   - **Build Command**: `pip install -r api/requirements.txt`
6. Add Environment Variables (if needed)
7. Click "Deploy"

### Step 3: Configure vercel.json

The `vercel.json` file is already configured to:
- Use Python runtime via `@vercel/python`
- Route all requests to `api/app.py`
- Set environment variables

### Important Notes

⚠️ **Limitations on Vercel Free Tier:**
- No persistent storage (files in `/tmp` are cleared between deployments)
- No camera/video input support (serverless environment)
- Maximum 10 second execution time per request
- No background processes

### Recommended Changes for Production

For a production deployment with full features:

1. **Use a Database** (MongoDB, PostgreSQL, etc.)
   - Replace CSV file storage with database
   - Store gesture data in cloud database

2. **Use Cloud Storage** (AWS S3, Google Cloud Storage, etc.)
   - Store gesture samples
   - Store trained models

3. **Separate Backend & Frontend**
   - Keep Flask API on Vercel
   - Deploy frontend separately (Vercel, Netlify, etc.)

4. **Remove OpenCV Dependencies**
   - OpenCV requires display output (not available in serverless)
   - Use image processing alternatives or move processing to client

### Example Environment Variables

Create a `.env.local` file (for local development):

```env
VERCEL_ENV=development
FLASK_ENV=development
```

### Accessing Your App

After deployment, your app will be available at:
```
https://your-project-name.vercel.app
```

### Monitoring & Logs

- View logs: `vercel logs`
- Check deployments: https://vercel.com/dashboard
- Monitor performance: Vercel Dashboard → Project → Analytics

### Troubleshooting

**Issue: OpenCV fails to import**
- Solution: Vercel doesn't support display servers. Remove video processing or use headless alternatives.

**Issue: Models/Data not persisting**
- Solution: Use cloud storage (S3, Firebase) instead of local files.

**Issue: Timeout errors**
- Solution: Optimize code, reduce processing time, or use async tasks.

## Local Testing (Vercel Functions Locally)

```bash
# Install Vercel CLI
npm install -g vercel

# Test locally
vercel dev
```

Your app will be available at `http://localhost:3000`

## Next Steps

1. Modify code to work without camera input
2. Implement cloud storage for gesture data
3. Use API endpoints for gesture processing instead of real-time video
4. Consider using Edge Functions for better performance

---

For more help, visit: https://vercel.com/docs/concepts/deployments/overview
