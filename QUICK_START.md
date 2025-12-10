# Quick Start: Deploying to Vercel

## Option 1: Using Vercel Dashboard (Easiest)

1. **Push your code to GitHub**
   ```powershell
   cd C:\Users\MSI\Handgesture
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/Handgesture.git
   git push -u origin main
   ```

2. **Go to Vercel and deploy**
   - Visit https://vercel.com/new
   - Click "Import Git Repository"
   - Connect GitHub and select your Handgesture repository
   - Click "Import"
   - Click "Deploy"
   - ✅ Done! Your app is live in ~2-3 minutes

## Option 2: Using Vercel CLI

```powershell
# Install Vercel CLI
npm install -g vercel

# Navigate to project
cd C:\Users\MSI\Handgesture

# Deploy
vercel
```

## Option 3: Using Deployment Script (Windows)

```powershell
cd C:\Users\MSI\Handgesture
.\deploy-vercel.bat
```

---

## After Deployment

✅ Your app will be available at: `https://your-project-name.vercel.app`

### View Your App
- Main URL: Check your Vercel dashboard
- API Health: `https://your-project-name.vercel.app/api/health`
- API Gestures: `https://your-project-name.vercel.app/api/gestures/list`

---

## ⚠️ Important Limitations

**Vercel is a serverless platform.** Your app will work, but some features won't:

❌ **Won't Work:**
- Real-time video streaming (no camera access)
- File persistence between deployments
- Background processes

✅ **Will Work:**
- API endpoints for gesture processing
- Web interface
- Model inference
- Data export

---

## Recommended: Use Cloud Services

For production, add these services:

1. **Database**: MongoDB Atlas, Firebase, or PostgreSQL
   - Store gesture models
   - Store gesture data

2. **Cloud Storage**: AWS S3 or Google Cloud Storage
   - Store trained models
   - Store gesture samples

3. **Frontend**: Keep on Vercel or Netlify
   - Upload images/video for processing
   - Get results back via API

---

## Environment Variables

If needed, add environment variables in Vercel dashboard:

Settings → Environment Variables

Example:
```
ROBOFLOW_API_KEY=your_key_here
VERCEL_ENV=production
```

---

## Questions?

- Vercel Docs: https://vercel.com/docs
- GitHub Issues: Create an issue in your repo
- Python on Vercel: https://vercel.com/docs/concepts/runtimes/python

---

**Good luck! 🚀**
