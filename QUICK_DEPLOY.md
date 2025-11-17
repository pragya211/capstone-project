# Quick Deployment Guide

## Fastest Way: Vercel + Railway

### Step 1: Deploy Backend to Railway (5 minutes)

1. Go to [railway.app](https://railway.app) and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Python
5. Add environment variables:
   - `OPENAI_API_KEY` = your OpenAI API key
   - `ALLOWED_ORIGINS` = (leave empty for now, add after frontend deploy)
   - `ENVIRONMENT` = `production`
6. Click "Deploy"
7. Copy the deployment URL (e.g., `https://your-app.railway.app`)

### Step 2: Deploy Frontend to Vercel (5 minutes)

1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Set root directory to `capstone-ui`
5. Add environment variable:
   - `REACT_APP_API_BASE_URL` = your Railway backend URL (from Step 1)
6. Click "Deploy"
7. Copy the deployment URL (e.g., `https://your-app.vercel.app`)

### Step 3: Update Backend CORS

1. Go back to Railway dashboard
2. Add/Update environment variable:
   - `ALLOWED_ORIGINS` = your Vercel frontend URL (from Step 2)
3. Railway will automatically redeploy

### Step 4: Test

Visit your Vercel URL and test the application!

---

## Alternative: Render (Free Tier Available)

### Backend on Render

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Settings:
   - **Name**: capstone-backend
   - **Root Directory**: capstone_project
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as Railway)
6. Click "Create Web Service"

### Frontend on Render

1. Click "New +" → "Static Site"
2. Connect your GitHub repo
3. Settings:
   - **Root Directory**: capstone-ui
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: build
4. Add environment variable: `REACT_APP_API_BASE_URL`
5. Click "Create Static Site"

---

## Environment Variables Checklist

### Backend (Railway/Render)
- [ ] `OPENAI_API_KEY` - Your OpenAI API key
- [ ] `ALLOWED_ORIGINS` - Your frontend URL (comma-separated if multiple)
- [ ] `ENVIRONMENT` - Set to `production`
- [ ] `SECRET_KEY` - Random string for JWT tokens (generate with: `openssl rand -hex 32`)
- [ ] `DATABASE_URL` - (Optional) For PostgreSQL, otherwise uses SQLite

### Frontend (Vercel/Render)
- [ ] `REACT_APP_API_BASE_URL` - Your backend URL

---

## Troubleshooting

**CORS Error?**
- Make sure `ALLOWED_ORIGINS` includes your frontend URL exactly
- Check that `ENVIRONMENT=production` is set in backend

**API Not Found?**
- Verify `REACT_APP_API_BASE_URL` is set correctly
- Check backend logs in Railway/Render dashboard

**Build Fails?**
- Check that all dependencies are in `requirements.txt`
- Verify Python version matches (3.11)

---

## Cost Estimate

- **Vercel**: Free tier (hobby) - sufficient for most projects
- **Railway**: $5/month after free trial, or use Render free tier
- **Render**: Free tier available (slower, but works)

**Total**: $0-5/month for small to medium traffic

