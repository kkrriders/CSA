# 🚀 Deploy Backend to Render.com

## ✅ Fixed Deployment Configuration

The `requirements.txt` path issue has been fixed! Your backend is now ready to deploy.

---

## 🔧 What Was Fixed

### Problem
```
❌ Render couldn't find requirements.txt
❌ Path was: adaptive-learning-platform/backend
❌ Should be: backend
```

### Solution
```
✅ Updated render.yaml to use correct rootDir: backend
✅ Created render.yaml in backend directory
✅ Fixed environment variable configuration
```

---

## 🚀 Deploy to Render (Step by Step)

### Option 1: Deploy from Root (Recommended)

1. **Push to GitHub**
   ```bash
   cd /mnt/c/Users/karti/CSA/adaptive-learning-platform
   git init
   git add .
   git commit -m "Initial commit - Adaptive Learning Platform"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/adaptive-learning-platform.git
   git push -u origin main
   ```

2. **Create Web Service on Render**
   - Go to https://render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically

3. **Configure Settings** (if not using render.yaml)
   - **Name**: adaptive-learning-backend
   - **Region**: Oregon (US West)
   - **Branch**: main
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**
   ```
   MONGODB_URI = mongodb+srv://kartikarora3135:Ak31351240.!@csa.spxmhnr.mongodb.net/?appName=CSA
   MONGODB_DB_NAME = adaptive_learning
   SECRET_KEY = af8d9c6e4b3a2f1d8e7c6b5a4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 1440
   LLM_PROVIDER = openrouter
   OPENROUTER_API_KEY = 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
   OPENROUTER_MODEL = mistralai/mistral-7b-instruct
   CORS_ORIGINS = http://localhost:3000,https://your-frontend.vercel.app
   MAX_FILE_SIZE = 52428800
   UPLOAD_DIR = ./uploads
   DEFAULT_QUESTION_TIME = 90
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes for deployment
   - Your backend will be live at: `https://adaptive-learning-backend.onrender.com`

---

### Option 2: Deploy from Backend Directory

1. **Navigate to Backend**
   ```bash
   cd backend
   ```

2. **Create Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Backend deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/backend.git
   git push -u origin main
   ```

3. **Deploy on Render**
   - Connect repository
   - **Root Directory**: Leave empty (or use `/`)
   - Rest same as above

---

## 📝 Render Configuration Files

### `render.yaml` (Root Directory)
```yaml
services:
  - type: web
    name: adaptive-learning-backend
    runtime: python
    region: oregon
    plan: free
    branch: main
    rootDir: backend  # ✅ This is the fix!
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### `backend/render.yaml` (Backup)
Same configuration but without rootDir (since it's already in backend)

---

## 🔑 Environment Variables for Render

Add these in Render Dashboard → Environment:

```env
# Required
MONGODB_URI=mongodb+srv://kartikarora3135:Ak31351240.!@csa.spxmhnr.mongodb.net/?appName=CSA
MONGODB_DB_NAME=adaptive_learning
SECRET_KEY=af8d9c6e4b3a2f1d8e7c6b5a4d3c2b1a0f9e8d7c6b5a4d3c2b1a0f9e8d7c6b5a

# OpenRouter AI
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=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
OPENROUTER_MODEL=mistralai/mistral-7b-instruct

# Optional (have defaults)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
MAX_FILE_SIZE=52428800
UPLOAD_DIR=./uploads
DEFAULT_QUESTION_TIME=90

# Update after frontend deployment
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

---

## ✅ Verify Deployment

### 1. Check Build Logs
```
=== Building...
Looking for requirements.txt
✓ Found requirements.txt
Installing dependencies...
✓ Successfully installed packages
```

### 2. Check Deploy Logs
```
Starting service...
✓ Uvicorn running on http://0.0.0.0:10000
✓ Connected to MongoDB: adaptive_learning
```

### 3. Test API
```bash
# Replace with your Render URL
curl https://adaptive-learning-backend.onrender.com/health

# Expected response:
{"status":"healthy"}
```

### 4. Test API Docs
Visit: `https://adaptive-learning-backend.onrender.com/docs`

You should see the interactive Swagger UI!

---

## 🐛 Troubleshooting

### Issue: "Could not find requirements.txt"

**Solution 1: Check Root Directory**
```yaml
# In render.yaml, ensure:
rootDir: backend  # Not "adaptive-learning-platform/backend"
```

**Solution 2: Deploy from Backend**
- Push only the backend folder to a separate repo
- Deploy that repo without rootDir

**Solution 3: Manual Configuration**
- On Render dashboard, set "Root Directory" to `backend`
- Don't use render.yaml (manual config)

### Issue: "Module not found"

**Check Python Version:**
```yaml
envVars:
  - key: PYTHON_VERSION
    value: 3.11.0  # Make sure this matches
```

**Check requirements.txt:**
```bash
cat backend/requirements.txt
# Should list all dependencies
```

### Issue: "MongoDB connection failed"

**Fix MongoDB URI:**
```env
# Make sure URI is properly formatted:
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=CSA

# Check:
# 1. Password is URL-encoded
# 2. Cluster address is correct
# 3. MongoDB Atlas IP whitelist includes Render IPs (0.0.0.0/0)
```

### Issue: "OpenRouter API failed"

**Verify API Key:**
- Check key at: https://openrouter.ai/keys
- Make sure you have credits
- Try different model if current one is down

### Issue: "CORS error from frontend"

**Update CORS_ORIGINS:**
```env
# Add your Vercel frontend URL
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

---

## 📊 Render Free Tier Limits

- ✅ **750 hours/month** of runtime
- ✅ **Automatic deploys** from GitHub
- ✅ **Free SSL certificate**
- ⚠️ **Spins down after 15 min** of inactivity
- ⚠️ **Cold start** takes ~30s to wake up

**Note:** First request after inactivity will be slow (cold start). Subsequent requests are fast!

---

## 🔄 Update Deployment

### Method 1: Auto-Deploy (Recommended)
```bash
# Make changes locally
git add .
git commit -m "Update backend"
git push origin main

# Render auto-deploys! ✅
```

### Method 2: Manual Deploy
- Go to Render Dashboard
- Click "Manual Deploy" → "Deploy latest commit"

---

## 🎯 Post-Deployment

### 1. Get Your Backend URL
```
https://adaptive-learning-backend.onrender.com
```

### 2. Update Frontend
```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://adaptive-learning-backend.onrender.com/api
```

### 3. Test Integration
```bash
# From frontend
npm run build
npm start

# Or deploy to Vercel
vercel deploy --prod
```

### 4. Update CORS
Go back to Render → Environment → Update CORS_ORIGINS with frontend URL

---

## 📚 Deployment Checklist

### Pre-Deployment
- [x] requirements.txt exists in backend/
- [x] render.yaml configured correctly
- [x] .env variables documented
- [x] MongoDB Atlas IP whitelist updated
- [x] OpenRouter API key valid

### During Deployment
- [ ] Repository pushed to GitHub
- [ ] Render service created
- [ ] Environment variables added
- [ ] Deployment successful
- [ ] Build logs clean

### Post-Deployment
- [ ] Health check endpoint works
- [ ] API docs accessible
- [ ] Can register/login users
- [ ] Can upload documents
- [ ] OpenRouter API working
- [ ] Frontend can connect

---

## 🌐 Example Deployment URLs

**Backend API:**
```
https://adaptive-learning-backend.onrender.com
```

**API Documentation:**
```
https://adaptive-learning-backend.onrender.com/docs
```

**Health Check:**
```
https://adaptive-learning-backend.onrender.com/health
```

**API Endpoints:**
```
POST https://adaptive-learning-backend.onrender.com/api/auth/register
POST https://adaptive-learning-backend.onrender.com/api/auth/login
GET  https://adaptive-learning-backend.onrender.com/api/documents/
POST https://adaptive-learning-backend.onrender.com/api/questions/generate
```

---

## 💰 Cost Estimate

**Free Tier:**
- Backend hosting: **FREE** ✅
- MongoDB Atlas (512MB): **FREE** ✅
- OpenRouter API: **~$0.10-0.50/month** (very affordable)

**Total:** Essentially free for development and testing!

---

## 🎉 Success!

Your backend should now be deployed and accessible at:
```
https://adaptive-learning-backend.onrender.com
```

**Test it:**
```bash
curl https://adaptive-learning-backend.onrender.com/health
# Expected: {"status":"healthy"}
```

**Next:** Deploy frontend to Vercel!

---

## 📞 Support

**Render Issues:**
- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs
- Status: https://status.render.com

**Backend Issues:**
- Check logs in Render Dashboard
- View build logs for errors
- Check environment variables

---

**🚀 Happy Deploying!**
