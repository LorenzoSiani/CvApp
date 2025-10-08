# Render.com Deployment Guide

## 🚀 **Deploy CVLTURE WordPress Manager to Render.com**

This guide will help you deploy your WordPress management application to Render.com using their Docker deployment feature.

### **Prerequisites**

1. **Render.com Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **MongoDB Database**: Set up MongoDB Atlas or another MongoDB service

### **Step 1: Prepare MongoDB Database**

#### **Option A: MongoDB Atlas (Recommended)**
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create a database user with read/write permissions
4. Whitelist Render.com IP addresses (or use 0.0.0.0/0 for all IPs)
5. Get your connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

#### **Option B: Other MongoDB Services**
- Use any MongoDB service that provides a connection string
- Ensure it's accessible from external services

### **Step 2: Deploy to Render.com**

#### **Method 1: Using Render Dashboard (Recommended)**

1. **Connect Repository**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing your WordPress manager

2. **Configure Service**:
   - **Name**: `cvlture-wordpress-manager` (or your preferred name)
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your deployment branch)
   - **Dockerfile Path**: `./Dockerfile`

3. **Set Environment Variables**:
   ```
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/wordpress_manager_db
   DB_NAME=wordpress_manager_db
   CORS_ORIGINS=https://your-app-name.onrender.com
   PORT=10000
   PYTHONUNBUFFERED=1
   ```

4. **Deploy**:
   - Click "Create Web Service"
   - Wait for build and deployment (usually 5-10 minutes)

#### **Method 2: Using render.yaml (Infrastructure as Code)**

1. **Update render.yaml**:
   ```yaml
   services:
     - type: web
       name: cvlture-wordpress-manager
       env: docker
       dockerfilePath: ./Dockerfile
       plan: starter
       healthCheckPath: /api/
       envVars:
         - key: MONGO_URL
           sync: false  # Set this manually in dashboard for security
         - key: DB_NAME
           value: wordpress_manager_db
         - key: CORS_ORIGINS
           value: https://your-app-name.onrender.com
         - key: PORT
           value: 10000
         - key: PYTHONUNBUFFERED
           value: 1
   ```

2. **Deploy**:
   - Commit `render.yaml` to your repository
   - Render will automatically detect and deploy

### **Step 3: Configure Environment Variables**

In the Render dashboard, set these environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `MONGO_URL` | `mongodb+srv://...` | Your MongoDB connection string |
| `DB_NAME` | `wordpress_manager_db` | Database name |
| `CORS_ORIGINS` | `https://your-app.onrender.com` | Your Render app URL |
| `PORT` | `10000` | Port (required by Render) |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |

**Security Note**: Keep your `MONGO_URL` secret and don't commit it to your repository.

### **Step 4: Custom Domain (Optional)**

1. **Add Custom Domain**:
   - Go to your service settings
   - Click "Custom Domains"
   - Add your domain (e.g., `manager.cvlture.it`)

2. **Update DNS**:
   - Add CNAME record pointing to your Render URL
   - Update `CORS_ORIGINS` environment variable

3. **SSL Certificate**:
   - Render automatically provides SSL certificates
   - No additional configuration needed

### **Step 5: Verify Deployment**

1. **Check Service Health**:
   - Visit your Render app URL
   - Should show CVLTURE loading screen then setup page

2. **Test API**:
   - Visit `https://your-app.onrender.com/api/`
   - Should return: `{"message": "WordPress Management API"}`

3. **Configure WordPress Connection**:
   - Enter your WordPress credentials
   - Test the connection to `https://www.cvlture.it`

### **Render.com Specific Features**

#### **Automatic Deployments**
- Renders automatically deploys on git push to main branch
- No manual deployment needed after initial setup

#### **Build Logs**
- View real-time build logs in dashboard
- Helpful for debugging deployment issues

#### **Health Checks**
- Render pings `/api/` endpoint every 30 seconds
- Automatically restarts if health check fails

#### **Sleep Mode**
- Free plans sleep after 15 minutes of inactivity
- First request after sleep may take 10-30 seconds

### **Performance Optimization**

#### **For Better Performance**:
1. **Upgrade Plan**: Consider Starter plan ($7/month) for always-on
2. **Database Location**: Use MongoDB region close to Render region
3. **CDN**: Consider adding CDN for static assets

#### **Environment-Specific Settings**:
```bash
# Production optimizations
CORS_ORIGINS=https://your-production-domain.com
DB_NAME=wordpress_manager_prod
```

### **Troubleshooting**

#### **Common Issues**:

1. **Build Fails**:
   - Check Dockerfile syntax
   - Ensure `package.json` exists in frontend directory
   - Verify `requirements.txt` in backend directory

2. **App Won't Start**:
   - Check environment variables are set correctly
   - Verify MongoDB connection string
   - Check service logs in Render dashboard

3. **CORS Issues**:
   - Ensure `CORS_ORIGINS` matches your domain exactly
   - Include both `http://` and `https://` if needed

4. **Database Connection Issues**:
   - Verify MongoDB connection string
   - Check database user permissions
   - Ensure IP whitelist includes Render IPs

#### **Debugging Steps**:
1. Check Render service logs
2. Verify environment variables
3. Test MongoDB connection separately
4. Check GitHub repository permissions

### **Monitoring & Maintenance**

#### **Monitor Your App**:
- Use Render dashboard for basic metrics
- Monitor response times and error rates
- Set up uptime monitoring (like UptimeRobot)

#### **Updates & Maintenance**:
- Git push automatically triggers redeployment
- Monitor MongoDB Atlas usage
- Regular security updates

### **Cost Estimation**

#### **Free Tier**:
- Render Web Service: Free (with limitations)
- MongoDB Atlas: Free (512MB storage)
- **Total**: $0/month

#### **Production Setup**:
- Render Starter Plan: $7/month
- MongoDB Atlas Shared: $9/month  
- **Total**: ~$16/month

### **Security Best Practices**

1. **Environment Variables**: Never commit secrets to git
2. **Database Security**: Use strong passwords and IP restrictions
3. **HTTPS**: Render provides automatic SSL
4. **Updates**: Keep dependencies updated regularly

Your CVLTURE WordPress Manager is now ready for production deployment on Render.com! 🎉

### **Next Steps**

1. Deploy the application
2. Configure your WordPress connection
3. Set up Google Analytics integration
4. Test all functionality
5. Consider setting up monitoring

For support, check Render.com documentation or create an issue in your repository.