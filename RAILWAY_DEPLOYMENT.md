# Railway Deployment Guide

## 🚂 Deploying to Railway

### 1. Initial Setup
- Connect your GitHub repo to Railway
- Railway will automatically detect the Python app

### 2. Environment Variables (Optional)
Railway will automatically install dependencies from `requirements.txt`

### 3. Cookie Management for Railway

**IMPORTANT**: Your `cookies.txt` file will be deployed with your code, but cookies expire quickly. You need to update them regularly.

#### Option A: Update cookies locally and redeploy
1. Run locally: `python generate_cookies.py`
2. Commit the new `cookies.txt`
3. Push to GitHub
4. Railway will auto-deploy

#### Option B: Use Railway's file system (Advanced)
1. SSH into your Railway instance
2. Generate cookies directly on Railway
3. Save to the persistent file system

### 4. Testing Your Deployment

After deployment, test these endpoints:

```bash
# Check if API is running
curl "https://your-app.railway.app/"

# Check authentication status
curl "https://your-app.railway.app/auth-status"

# Test YouTube connectivity
curl "https://your-app.railway.app/test-youtube"

# Try to get a transcript
curl "https://your-app.railway.app/transcript/dQw4w9WgXcQ"
```

### 5. Common Railway Issues

1. **Cookies expired**: Update cookies.txt and redeploy
2. **Build failures**: Check requirements.txt is correct
3. **Runtime errors**: Check Railway logs for detailed error messages

### 6. Monitoring

- Use `/health` endpoint for basic health checks
- Use `/auth-status` to monitor cookie validity
- Use `/test-youtube` to verify YouTube connectivity

### 7. Auto-deployment

Railway automatically redeploys when you push to your main branch. Make sure to:
- Update cookies regularly
- Test locally before pushing
- Monitor Railway logs for errors

## 🔄 Cookie Update Workflow

1. **Local development**:
   ```bash
   python generate_cookies.py
   python main.py
   # Test locally
   ```

2. **Deploy to Railway**:
   ```bash
   git add .
   git commit -m "Update cookies"
   git push origin main
   ```

3. **Verify deployment**:
   - Check Railway logs
   - Test `/auth-status` endpoint
   - Test `/test-youtube` endpoint

## 🚨 Troubleshooting

If you still get "Sign in to confirm you're not a bot":

1. Check `/auth-status` - are cookies expired?
2. Check `/test-youtube` - does the test pass?
3. Update cookies locally and redeploy
4. Check Railway logs for detailed errors

## 📝 Notes

- Cookies typically expire within hours/days
- Railway instances may have different IP addresses
- Consider setting up a cron job or GitHub Action to update cookies regularly
- Monitor your Railway usage and costs
