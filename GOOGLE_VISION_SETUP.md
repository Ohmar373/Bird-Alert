# 🔍 Google Cloud Vision API Setup Guide

This guide explains how to set up Google Cloud Vision API for enhanced bird species detection in Bird-Alert.

## Why Google Vision API?

**Free Tier:** 1,000 requests/month  
**Accuracy:** Higher than local detection model  
**Cost:** ~$1.50 per 1,000 requests after free tier

The app uses a **hybrid approach**:
- ✅ **TensorFlow.js** - Always free, runs in browser
- 🚀 **Google Vision** - Optional upgrade for better accuracy

If Google Vision API is configured, it will be used for higher-accuracy detection. If not, the app falls back to TensorFlow.js automatically.

---

## Setup Steps

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **"Select a Project"** → **"New Project"**
3. Enter project name: `Bird-Alert`
4. Click **Create**

### Step 2: Enable Vision API

1. In the Cloud Console, search for **"Vision API"**
2. Click **Vision API**
3. Click **"Enable"**
4. Wait for it to finish enabling (1-2 minutes)

### Step 3: Create Service Account

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **"Create Service Account"**
3. Fill in:
   - **Service account name:** `bird-alert-vision`
   - **Service account ID:** auto-filled
4. Click **Create and Continue**
5. Grant these roles:
   - ✅ **Basic Editor**
   - ✅ **Vision API User**
6. Click **Continue**
7. Click **Done**

### Step 4: Create Credentials JSON Key

1. In Service Accounts, click on the **`bird-alert-vision`** account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Select **JSON**
5. Click **Create**
6. A JSON file will download automatically
7. **Save it in your project root** as `google-credentials.json`
8. **⚠️ IMPORTANT:** Add it to `.gitignore` to avoid exposing credentials

### Step 5: Configure Django

Add to your `.env` file:

```bash
GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json
```

Or set the environment variable in your system:

**Windows (PowerShell):**
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\google-credentials.json"
```

**Linux/Mac:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google-credentials.json"
```

### Step 6: Update requirements.txt

The package is already added:
```bash
google-cloud-vision==3.7.4
```

Install it:
```bash
pip install -r requirements.txt
```

---

## Testing

### Test 1: Check if credentials are loaded

```python
import os
print(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
```

### Test 2: Try a detection

1. Go to `/sightings/camera/`
2. Upload or capture an image
3. Check the detection method indicator
   - 🚀 **Google Vision API** = Successfully connected
   - 🎥 **Local Detection** = Credentials not found (fallback)

---

## Troubleshooting

### "No module named 'google.cloud.vision'"
Install the package:
```bash
pip install google-cloud-vision==3.7.4
```

### "GOOGLE_APPLICATION_CREDENTIALS not set"
Make sure the environment variable is set before running Django:
```bash
# Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS = "google-credentials.json"
python manage.py runserver

# Or Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="google-credentials.json"
python manage.py runserver
```

### "Invalid service account credentials"
- Check that `google-credentials.json` exists in the project root
- Verify the JSON file is valid (open it and check it has `type: service_account`)
- Ensure you downloaded the key from the correct service account

### "Quota exceeded"
You've used your 1,000 free monthly requests. Either:
- ✅ Wait until next month (quotas reset)
- ✅ Upgrade Google Cloud billing to pay-as-you-go (~$1.50 per 1,000 requests)
- ✅ The app will automatically fall back to TensorFlow.js (still free!)

---

## Monitoring Usage

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Search for **"Cloud Vision API"**
3. Click **Metrics** tab
4. View request count and status codes

---

## Cost Tracking

At $1.50 per 1,000 requests after the free tier:
- 100 detections/month = $0.15
- 500 detections/month = $0.75
- 1,000+ detections/month = $1.50+

For a small community app, you'll likely stay within the free tier or spend <$5/month.

---

## Disabling Google Vision (Optional)

If you want to disable Google Vision and only use TensorFlow.js:

1. Remove the `GOOGLE_APPLICATION_CREDENTIALS` variable from `.env`
2. Delete or rename `google-credentials.json`
3. The app will automatically fall back to local detection

---

## Security Note

**Never commit `google-credentials.json` to GitHub!**

Verify it's in `.gitignore`:
```bash
# Check .gitignore
cat .gitignore | grep google-credentials.json
```

If it's not there, add it:
```bash
echo "google-credentials.json" >> .gitignore
```

---

## Next Steps

After setup, visit `/sightings/camera/` to:
1. 📸 Upload or capture a bird image
2. 🔍 See detection with source method
3. 🔗 Use "Verify with Google Lens" for independent confirmation
4. ✅ Add your detected sighting

Happy birdwatching! 🐦
