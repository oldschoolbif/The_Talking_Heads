# D-ID 500 Error Solution - Step-by-Step Guide

## ✅ What We Found

The troubleshooting script (`scripts/troubleshoot_did.py`) has identified:

1. **✅ API Key:** Valid and working
2. **✅ Authentication:** Successfully authenticating with D-ID API
3. **✅ Account Credits:** 400 credits remaining (active subscription)
4. **❌ Image URLs:** D-ID requires image URLs that end with `.jpg`, `.jpeg`, or `.png` (no query parameters)

## 🔍 Root Cause

The 500 errors are likely caused by **invalid image URLs**. D-ID's API validation requires:
- Image URL must end with `.jpg`, `.jpeg`, or `.png`
- No query parameters allowed in the URL
- Image must be publicly accessible

## 📋 Step-by-Step Solution

### Step 1: Get a Valid Image URL

You have **3 options**:

#### Option A: Upload Image to D-ID Studio (Recommended)
1. Go to https://studio.d-id.com
2. Log in to your account
3. Navigate to **"Avatars"** or **"Images"** section
4. Click **"Upload"** or **"Create Avatar"**
5. Upload a `.jpg`, `.jpeg`, or `.png` image
6. Copy the **image URL** from the dashboard
7. This URL will be in format: `https://d-id-public-bucket.s3.amazonaws.com/your-image-id.jpg`

#### Option B: Use a Public Image URL
1. Find a publicly accessible image URL that:
   - Ends with `.jpg`, `.jpeg`, or `.png`
   - Has NO query parameters (no `?w=400` or similar)
   - Is accessible without authentication
2. Example format: `https://example.com/image.jpg` ✅
3. Bad format: `https://example.com/image.jpg?w=400` ❌

#### Option C: Use D-ID Preset Avatars (if available)
1. Check D-ID documentation for preset avatar URLs
2. These should be in format: `preset://avatar-name` or direct URLs
3. Verify the format in D-ID's latest documentation

### Step 2: Update Your Code

Once you have a valid image URL, update the code:

**File:** `src/core/avatar_generator.py`

**Current code (around line 1200-1300):**
```python
# In DIDProvider.generate method
avatar_mapping = {
    "amy": "https://d-id-public-bucket.s3.amazonaws.com/amy.jpg",
    "sara": "https://d-id-public-bucket.s3.amazonaws.com/sara.jpg",
    "john": "https://d-id-public-bucket.s3.amazonaws.com/john.jpg",
}
```

**Replace with your valid image URL:**
```python
# Option 1: Use your uploaded D-ID image URL
avatar_mapping = {
    "amy": "https://d-id-public-bucket.s3.amazonaws.com/YOUR-IMAGE-ID.jpg",
    # ... etc
}

# Option 2: Or use a single valid public image URL for all avatars
source_url = "https://your-valid-image-url.com/image.jpg"  # Must end with .jpg/.jpeg/.png
```

### Step 3: Test the Fix

Run the troubleshooting script again:
```powershell
python scripts/troubleshoot_did.py
```

Or test with a simple script:
```powershell
python scripts/test_did_simple.py
```

### Step 4: Verify Success

Look for these indicators:
- ✅ Status code `200`, `201`, or `202` (not `400` or `500`)
- ✅ Response contains `"id"` field (talk ID)
- ✅ No validation errors in response

## 🛠️ Quick Test Command

After updating the image URL, test immediately:

```powershell
python scripts/troubleshoot_did.py
```

The script will:
1. Verify your API key
2. Test authentication
3. Check account credits
4. Test image URL accessibility
5. Attempt to create a talk with your image URL
6. Report success or specific error

## 📝 What to Do Right Now

1. **Go to D-ID Studio:** https://studio.d-id.com
2. **Upload an image** (or use an existing avatar)
3. **Copy the image URL** (must end with `.jpg`, `.jpeg`, or `.png`)
4. **Update `src/core/avatar_generator.py`** with the valid URL
5. **Run:** `python scripts/troubleshoot_did.py`
6. **Verify:** You should see `[OK] SUCCESS! D-ID API is working!`

## 🚨 If Still Getting 500 Errors

If you've followed all steps and still get 500 errors:

1. **Check D-ID Status:** https://status.d-id.com
2. **Verify Image URL:**
   - Must end with `.jpg`, `.jpeg`, or `.png`
   - Must be publicly accessible
   - No query parameters
   - Test in browser: `curl -I <your-image-url>`
3. **Check Account:**
   - Credits > 0
   - Subscription active
   - No account restrictions
4. **Contact D-ID Support:**
   - Email: support@d-id.com
   - Include: API key (masked), image URL, error response

## 📚 Additional Resources

- **D-ID API Docs:** https://docs.d-id.com/reference/talks-create
- **D-ID Studio:** https://studio.d-id.com
- **D-ID Support:** https://support.d-id.com/

## ✅ Summary

**The Problem:** Invalid image URLs (don't end with `.jpg/.jpeg/.png` or have query parameters)

**The Solution:** 
1. Upload image to D-ID Studio OR use valid public image URL
2. Update code with valid URL
3. Test with `python scripts/troubleshoot_did.py`

**Expected Result:** Status `200/201/202` with talk ID in response

