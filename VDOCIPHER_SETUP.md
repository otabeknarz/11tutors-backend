# VdoCipher Setup Guide

## 🎥 What is VdoCipher?

VdoCipher is a secure video hosting platform that provides:
- Video encryption and DRM protection
- Secure video streaming
- Upload API for video management
- Analytics and playback tracking

## 🔑 Getting Your API Key

### Step 1: Create VdoCipher Account
1. Go to: https://www.vdocipher.com/
2. Click "Sign Up" or "Get Started"
3. Create an account (free trial available)
4. Verify your email

### Step 2: Get API Secret Key
1. Log in to VdoCipher Dashboard: https://www.vdocipher.com/dashboard
2. Go to **API** section in the sidebar
3. Find your **API Secret Key**
4. Copy the key (it looks like: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

## ⚙️ Configure Backend

### Step 1: Create `.env` File

In the backend directory, create a `.env` file:

```bash
cd /Users/otabeknarz/Desktop/projects/11tutors/backend
cp .env.example .env
```

### Step 2: Add VdoCipher API Key

Edit `.env` file and add your API key:

```env
VIDEO_SERVICE_SECRET_KEY=your-actual-vdocipher-api-key-here
```

**Example:**
```env
VIDEO_SERVICE_SECRET_KEY=abc123def456ghi789jkl012mno345pqr678
```

### Step 3: Install python-dotenv (if not installed)

```bash
pip install python-dotenv
```

### Step 4: Restart Django Server

```bash
python manage.py runserver
```

## 🧪 Test the Setup

### Method 1: Check in Django Shell

```bash
python manage.py shell
```

```python
from django.conf import settings
print(settings.VIDEO_SERVICE_SECRET_KEY)
# Should print your API key, not None
```

### Method 2: Test Upload Endpoint

1. Start Django server: `python manage.py runserver`
2. Go to frontend and try uploading a video
3. Check backend terminal for logs

## 📋 Expected Behavior

### ✅ When API Key is Correct:

**Backend logs:**
```
POST /api/courses/vdocipher/upload-credentials/ 200
```

**Frontend console:**
```
Starting VdoCipher upload for: My Lesson
Requesting upload credentials from backend...
Received upload credentials: { videoId: "...", uploadUrl: "...", ... }
Starting upload to VdoCipher...
```

### ❌ When API Key is Missing/Wrong:

**Backend logs:**
```
VdoCipher API error: 401 - {"message":"Invalid API Secret"}
POST /api/courses/vdocipher/upload-credentials/ 500
```

**Frontend console:**
```
Failed to get credentials: {"error":"Failed to get upload credentials from VdoCipher"}
```

## 🔍 Troubleshooting

### Error: "Failed to get upload credentials from VdoCipher"

**Possible causes:**

1. **API key not set**
   - Check `.env` file exists
   - Check `VIDEO_SERVICE_SECRET_KEY` is set
   - Restart Django server

2. **Invalid API key**
   - Verify key from VdoCipher dashboard
   - Make sure no extra spaces or quotes
   - Key should be ~40 characters long

3. **VdoCipher account issue**
   - Check if account is active
   - Check if free trial has expired
   - Verify API access is enabled

### Check Environment Variable

```bash
# In backend directory
python manage.py shell
```

```python
import os
from django.conf import settings

# Check if .env is loaded
print("VIDEO_SERVICE_SECRET_KEY:", settings.VIDEO_SERVICE_SECRET_KEY)

# Should NOT be None
# Should NOT be "your-vdocipher-api-key-here"
```

### Check VdoCipher API Directly

```bash
curl -X PUT https://dev.vdocipher.com/api/videos \
  -H "Authorization: Apisecret YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Video","folderId":"root"}'
```

**Expected response (200 OK):**
```json
{
  "videoId": "...",
  "uploadUrl": "...",
  "clientPayload": {...}
}
```

**Error response (401 Unauthorized):**
```json
{
  "message": "Invalid API Secret"
}
```

## 📝 Environment File Structure

Your `.env` file should look like:

```env
# Django
SECRET_KEY=django-insecure-your-secret-key
DEBUG=True

# VdoCipher (REQUIRED)
VIDEO_SERVICE_SECRET_KEY=abc123def456ghi789jkl012mno345pqr678

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## 🎯 Quick Fix Checklist

- [ ] VdoCipher account created
- [ ] API Secret Key copied from dashboard
- [ ] `.env` file created in backend directory
- [ ] `VIDEO_SERVICE_SECRET_KEY` added to `.env`
- [ ] No extra spaces or quotes around the key
- [ ] Django server restarted
- [ ] Test upload from frontend

## 🔗 Useful Links

- VdoCipher Dashboard: https://www.vdocipher.com/dashboard
- API Documentation: https://www.vdocipher.com/docs/api/
- Support: https://www.vdocipher.com/support

---

Once you've set up the API key, video uploads should work! 🎉
