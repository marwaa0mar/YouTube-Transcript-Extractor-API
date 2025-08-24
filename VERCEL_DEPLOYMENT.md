# Vercel Deployment Guide

This guide will help you deploy your YouTube Transcript API to Vercel.

## Prerequisites

1. **GitHub Account** - Your code should be in a GitHub repository
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com)
3. **Node.js** (optional) - For Vercel CLI

## Step 1: Prepare Your Repository

Make sure your repository has these files:
- ✅ `api/main.py` - Your FastAPI application
- ✅ `index.html` - Your frontend
- ✅ `requirements.txt` - Python dependencies
- ✅ `vercel.json` - Vercel configuration

## Step 2: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Go to [vercel.com](https://vercel.com)** and sign in
2. **Click "New Project"**
3. **Import your GitHub repository**
4. **Configure the project:**
   - Framework Preset: `Other`
   - Root Directory: `./` (leave as default)
   - Build Command: Leave empty
   - Output Directory: Leave empty
5. **Click "Deploy"**

### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   vercel
   ```

## Step 3: Configure Environment Variables (Optional)

If you need to add cookies or other environment variables:

1. Go to your Vercel project dashboard
2. Click on "Settings" → "Environment Variables"
3. Add any needed variables

## Step 4: Test Your Deployment

Your app will be available at:
- **Frontend**: `https://your-project-name.vercel.app/`
- **API**: `https://your-project-name.vercel.app/api/video-info/{video_id}`

## Step 5: Update Custom Domain (Optional)

1. Go to your Vercel project dashboard
2. Click on "Settings" → "Domains"
3. Add your custom domain

## File Structure for Vercel

```
your-project/
├── api/
│   └── main.py          # FastAPI application
├── index.html           # Frontend
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel configuration
└── README.md
```

## API Endpoints

After deployment, your API will have these endpoints:

- `GET /` - API information
- `GET /api/health` - Health check
- `GET /api/video-info/{video_id}` - Get video information
- `GET /api/transcript/{video_id}` - Get video transcript

## Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check that all dependencies are in `requirements.txt`
   - Ensure `api/main.py` exists and is valid Python

2. **API Not Working**
   - Verify the routes in `vercel.json`
   - Check that endpoints start with `/api/`

3. **CORS Issues**
   - The API is configured to allow all origins
   - If you have issues, check the CORS settings in `api/main.py`

### Debugging:

1. **Check Vercel Logs:**
   - Go to your project dashboard
   - Click on "Functions" to see serverless function logs

2. **Test API Directly:**
   - Try accessing `https://your-project.vercel.app/api/health`
   - This should return `{"status": "ok", "message": "Healthy"}`

## Performance Notes

- **Cold Starts**: First request might be slower (1-2 seconds)
- **Timeout**: Functions timeout after 30 seconds
- **Memory**: Limited to 1024MB per function

## Cost

- **Free Tier**: 100GB-hours per month
- **Hobby Plan**: $20/month for more resources

## Next Steps

After successful deployment:

1. **Test with different video IDs**
2. **Share your app URL with others**
3. **Monitor usage in Vercel dashboard**
4. **Set up custom domain if needed**

## Support

If you encounter issues:
1. Check Vercel documentation: [vercel.com/docs](https://vercel.com/docs)
2. Check your project logs in Vercel dashboard
3. Ensure all files are properly committed to GitHub
