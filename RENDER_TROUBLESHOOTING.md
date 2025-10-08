# Render.com Deployment Troubleshooting

## 🚨 Common Build Errors & Solutions

### **Error: npm install fails with dependency conflicts**

**Error Message:**
```
npm error For a full report see: /root/.npm/_logs/...
process "/bin/sh -c npm install" did not complete successfully: exit code 1
```

**Solution 1 - Use Updated Dockerfile (Recommended):**
The main `Dockerfile` has been updated with:
```dockerfile
# Creates .npmrc with legacy peer deps
RUN echo "legacy-peer-deps=true" > .npmrc
RUN npm ci --legacy-peer-deps --no-optional || npm install --legacy-peer-deps
```

**Solution 2 - Use Alternative Dockerfiles:**
If the main Dockerfile still fails, try these alternatives:

**Option A - No CRACO (avoids ajv conflicts):**
1. Rename `Dockerfile` to `Dockerfile.backup`
2. Rename `Dockerfile.nocraco` to `Dockerfile`
3. Redeploy on Render

**Option B - Stable Version (recommended for production):**
1. Rename `Dockerfile` to `Dockerfile.backup`
2. Rename `Dockerfile.stable` to `Dockerfile`
3. Redeploy - gets full backend API + functional frontend

**Option C - Minimal Version (emergency deployment):**
1. Rename `Dockerfile` to `Dockerfile.backup`  
2. Rename `Dockerfile.minimal` to `Dockerfile`
3. Redeploy - gets basic functionality working immediately

**Solution 3 - Manual Package.json Fix:**
```bash
# Remove problematic fields from package.json
# Remove "packageManager" field
# Add to package.json:
"engines": {
  "node": "18.x",
  "npm": "10.x"
}
```

### **Error: Node version mismatch**

**Error Message:**
```
npm warn EBADENGINE Unsupported engine {
npm warn EBADENGINE   package: 'react-router-dom@7.9.3',
npm warn EBADENGINE   required: { node: '>=20.0.0' },
```

**Solutions:**

**1. Updated Dockerfile (Applied):**
Changed from `node:18-alpine` to `node:20-alpine` to meet React Router requirements.

**2. Downgraded React Router (Applied):**
Changed `react-router-dom` from `^7.5.1` to `^6.26.2` for better compatibility.

### **Error: ajv/ajv-keywords conflict**

**Error Messages:**
```
Error: Cannot find module 'ajv/dist/compile/codegen'
Error: Unknown keyword formatMinimum
```

**Solutions:**

**1. Use Updated Package.json (Applied):**
The package.json now includes dependency overrides:
```json
"overrides": {
  "ajv": "^8.12.0",
  "ajv-keywords": "^5.1.0"
}
```

**2. Use No-CRACO Dockerfile:**
CRACO sometimes causes ajv conflicts. Use `Dockerfile.nocraco` which:
- Uses `react-scripts` instead of `craco`
- Avoids complex webpack configurations

**3. Emergency Minimal Deployment:**
Use `Dockerfile.minimal` to get the API working immediately with a simple HTML frontend.

### **Error: Frontend build fails**

**Symptoms:**
- Build completes but app shows blank page
- Static files not loading
- React Router not working

**Solutions:**

**1. Check Build Output:**
```dockerfile
# Add this to see build output
RUN ls -la /app/frontend/build/
```

**2. Verify Static Files:**
Backend serves static files from `./frontend_build/static/`

**3. Environment Variables:**
```bash
# Add these to Render environment
CI=true
GENERATE_SOURCEMAP=false
NODE_OPTIONS=--max-old-space-size=4096
```

### **Error: Backend fails to start**

**Error Messages:**
- `uvicorn: command not found`
- `Module not found: backend.server`
- `Port already in use`

**Solutions:**

**1. Check Python Path:**
```dockerfile
# Make sure backend is copied correctly
COPY backend/ ./backend/
# Command should be:
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "10000"]
```

**2. Verify Requirements:**
```bash
# Make sure uvicorn is in requirements.txt
uvicorn==0.25.0
fastapi==0.110.1
```

### **Error: MongoDB connection fails**

**Error Messages:**
- `Connection failed: ...`
- `ServerSelectionTimeoutError`
- `Authentication failed`

**Solutions:**

**1. Check Connection String:**
```bash
# Format should be:
mongodb+srv://username:password@cluster.mongodb.net/database_name
```

**2. MongoDB Atlas Setup:**
- Whitelist IP: `0.0.0.0/0` (allow all)
- Create database user with read/write permissions
- Use correct database name in connection string

**3. Test Connection:**
```bash
# Test in Render shell
python -c "from motor.motor_asyncio import AsyncIOMotorClient; print('OK')"
```

### **Error: CORS issues**

**Symptoms:**
- Frontend loads but API calls fail
- Console shows CORS errors
- "Access-Control-Allow-Origin" errors

**Solutions:**

**1. Set Correct CORS Origins:**
```bash
# In Render environment variables:
CORS_ORIGINS=https://your-app-name.onrender.com
```

**2. For Development:**
```bash
CORS_ORIGINS=https://your-app.onrender.com,http://localhost:3000
```

**3. Wildcard (Less Secure):**
```bash
CORS_ORIGINS=*
```

## 🔧 **Step-by-Step Debugging**

### **1. Check Build Logs**
- Go to Render Dashboard → Your Service → Logs
- Look for specific error messages
- Check both build logs and runtime logs

### **2. Test Locally**
```bash
# Build Docker image locally
docker build -t test-app .

# Run and test
docker run -p 10000:10000 \
  -e MONGO_URL="your-mongodb-url" \
  -e DB_NAME="test_db" \
  -e CORS_ORIGINS="http://localhost:10000" \
  test-app
```

### **3. Use Render Shell**
```bash
# Access your running container
# In Render Dashboard → Shell tab
ls -la /app/
ls -la /app/frontend_build/
curl http://localhost:10000/api/
```

### **4. Check Environment Variables**
```bash
# In Render shell
env | grep -E "(MONGO|CORS|PORT)"
```

## 🛠️ **Alternative Deployment Methods**

### **Method 1: Separate Frontend & Backend**

If the combined build keeps failing, deploy separately:

**Backend Only (Render Web Service):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ ./
RUN pip install -r requirements.txt
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "10000"]
```

**Frontend (Render Static Site):**
```bash
# Build command: npm run build
# Publish directory: build
```

### **Method 2: Use Different Base Images**

If Node 18 Alpine causes issues:

```dockerfile
# Try Ubuntu base
FROM node:18 AS frontend-builder
# Or specific versions
FROM node:18.17.0-alpine AS frontend-builder
```

### **Method 3: Pre-build Frontend**

Build frontend locally and commit to git:

```bash
# Locally
cd frontend
npm install
npm run build
git add build/
git commit -m "Add pre-built frontend"
```

Then use simple backend-only Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ ./backend/
COPY frontend/build/ ./frontend_build/
# ... rest of backend setup
```

## 📋 **Deployment Checklist**

### **Before Deploying:**
- [ ] Remove `packageManager` from package.json
- [ ] Ensure MongoDB Atlas is configured
- [ ] Check all environment variables
- [ ] Test Dockerfile locally if possible

### **During Deployment:**
- [ ] Monitor build logs in real-time
- [ ] Check for specific error messages
- [ ] Note which stage fails (frontend build, backend setup, or startup)

### **After Deployment:**
- [ ] Test API endpoint: `https://your-app.onrender.com/api/`
- [ ] Check frontend loads: `https://your-app.onrender.com/`
- [ ] Test WordPress connection
- [ ] Verify all functionality works

## 🆘 **Emergency Solutions**

### **Quick Fix 1 - Minimal Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ ./backend/
RUN pip install fastapi uvicorn motor pymongo python-dotenv
EXPOSE 10000
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "10000"]
```

### **Quick Fix 2 - Static Frontend:**
Create simple HTML frontend:
```html
<!DOCTYPE html>
<html>
<head><title>WordPress Manager</title></head>
<body>
  <div id="root">
    <h1>CVLTURE WordPress Manager</h1>
    <p>API: <a href="/api/">Click here</a></p>
  </div>
</body>
</html>
```

## 📞 **Getting Help**

### **Render Support:**
- Check [Render Documentation](https://render.com/docs)
- Visit [Render Community](https://community.render.com)
- Submit support ticket (paid plans)

### **Debug Information to Collect:**
1. Complete build logs from Render
2. Runtime logs showing errors
3. Environment variables (without secrets)
4. Dockerfile content
5. Package.json content

### **Common Working Configurations:**

**Environment Variables:**
```
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/db
DB_NAME=wordpress_manager_db
CORS_ORIGINS=https://your-app.onrender.com
PORT=10000
PYTHONUNBUFFERED=1
```

**Minimal requirements.txt:**
```
fastapi==0.110.1
uvicorn==0.25.0
motor==3.3.1
python-dotenv>=1.0.1
pydantic>=2.6.4
```

Most deployment issues are resolved by:
1. Using `--legacy-peer-deps` for npm
2. Setting correct CORS origins
3. Proper MongoDB connection string
4. Using port 10000 for Render

Good luck with your deployment! 🚀