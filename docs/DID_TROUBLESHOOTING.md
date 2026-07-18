# D-ID API Troubleshooting Guide

## Step-by-Step Troubleshooting Process

### Step 1: Verify API Key

**Check your `.env` file:**
```bash
# Should have:
DID_API_KEY=your_api_key_here
```

**API Key Format:**
- D-ID supports two formats:
  - `username:password` (Basic Auth)
  - Single token value (Bearer token)

**Verify:**
```bash
python scripts/troubleshoot_did.py
```

This will check if your API key exists and is in the correct format.

---

### Step 2: Test Authentication

**What to check:**
- Can you authenticate with D-ID API?
- Does the API key have proper permissions?

**Test:**
```bash
python scripts/troubleshoot_did.py
```

**Expected Results:**
- ✓ Status 200: Authentication successful
- ✗ Status 401: API key invalid or expired
- ✗ Status 403: API key lacks permissions

**If authentication fails:**
1. Go to https://studio.d-id.com
2. Navigate to Account & API settings
3. Generate a new API key
4. Update your `.env` file
5. Restart your application

---

### Step 3: Check Account Status & Credits

**Manual Check:**
1. Go to https://studio.d-id.com
2. Log in to your account
3. Navigate to "Credits" or "Usage" section
4. Verify:
   - Credits available > 0
   - Subscription is active
   - No account restrictions

**Common Issues:**
- ✗ **No credits**: Purchase credits or upgrade subscription
- ✗ **Subscription expired**: Renew subscription
- ✗ **Account suspended**: Contact D-ID support

**D-ID Pricing:**
- Check current pricing at https://www.d-id.com/pricing
- Credits are consumed per video generation
- Different plans have different credit limits

---

### Step 4: Verify Image URLs

**What to check:**
- Are the D-ID preset image URLs accessible?
- Do we need to use different image URLs?

**Test:**
```bash
python scripts/troubleshoot_did.py
```

**Common Image URLs:**
- `https://d-id-public-bucket.s3.amazonaws.com/amy.jpg`
- `https://d-id-public-bucket.s3.amazonaws.com/sara.jpg`
- `https://d-id-public-bucket.s3.amazonaws.com/john.jpg`

**If URLs don't work:**
1. Check D-ID documentation for current image URLs
2. Upload your own image and use that URL
3. Use D-ID's avatar creation API to get valid URLs

---

### Step 5: Test Minimal Talk Creation

**What to test:**
- Can we create a talk with the simplest possible payload?
- What error do we get?

**Minimal Payload:**
```json
{
  "source_url": "https://d-id-public-bucket.s3.amazonaws.com/amy.jpg",
  "script": {
    "type": "text",
    "input": "Hello"
  }
}
```

**Run Test:**
```bash
python scripts/troubleshoot_did.py
```

**Status Code Meanings:**
- ✓ **200/201/202**: Success! Talk created
- ✗ **400**: Bad request - check payload format
- ✗ **402**: Payment required - no credits
- ✗ **403**: Forbidden - API key lacks permissions
- ✗ **429**: Rate limited - wait before retrying
- ✗ **500**: Internal server error (see below)

---

### Step 6: Diagnose 500 Errors

**If you get 500 Internal Server Error:**

#### Check 1: Account Credits
```bash
# Go to D-ID dashboard
https://studio.d-id.com
```
- Verify credits > 0
- Check if subscription is active
- Look for any account warnings

#### Check 2: API Key Permissions
- Some API keys may have restricted permissions
- Try generating a new API key
- Ensure key has "talks" creation permission

#### Check 3: Image URL Validity
- Verify image URL is accessible
- Try a different image URL
- Check if URL format is correct (must end in .jpg, .jpeg, or .png)

#### Check 4: Request Format
- Verify payload matches current D-ID API format
- Check D-ID documentation: https://docs.d-id.com/
- Try different payload formats

#### Check 5: D-ID Server Status
- Check D-ID status page (if available)
- Try again later (may be temporary outage)
- Contact D-ID support: https://support.d-id.com/

---

### Step 7: Test Alternative Formats

**If standard format fails, try:**

**Format 1: With driver parameter**
```json
{
  "source_url": "https://...",
  "script": {
    "type": "text",
    "input": "Hello"
  },
  "driver": "text"
}
```

**Format 2: Different script format**
```json
{
  "source_url": "https://...",
  "script": "Hello"
}
```

**Format 3: With additional parameters**
```json
{
  "source_url": "https://...",
  "script": {
    "type": "text",
    "input": "Hello"
  },
  "config": {
    "result_format": "mp4"
  }
}
```

---

### Step 8: Contact D-ID Support

**If all else fails:**

1. **Gather Information:**
   - API key format (masked)
   - Request payload (sanitized)
   - Response status code and body
   - Timestamp of error
   - Account email/ID

2. **Contact Support:**
   - Email: support@d-id.com
   - Support Portal: https://support.d-id.com/
   - Include all gathered information

3. **Ask About:**
   - Account status and credits
   - API key permissions
   - Current API endpoint format
   - Known issues or outages

---

## Quick Diagnostic Commands

**Run full diagnostic:**
```bash
python scripts/troubleshoot_did.py
```

**Test simple API call:**
```bash
python scripts/test_did_simple.py
```

**Test E2E pipeline:**
```bash
python scripts/test_did_e2e.py
```

---

## Common Solutions

### Solution 1: Add Credits
1. Go to https://studio.d-id.com
2. Navigate to "Credits" or "Billing"
3. Purchase credits or upgrade plan
4. Retry API call

### Solution 2: Regenerate API Key
1. Go to https://studio.d-id.com
2. Navigate to "Account & API"
3. Generate new API key
4. Update `.env` file
5. Restart application

### Solution 3: Use Different Image URL
1. Upload your own image to a public URL
2. Or use D-ID's avatar creation API
3. Update `source_url` in request

### Solution 4: Check API Documentation
1. Visit https://docs.d-id.com/
2. Check "Talks" API endpoint documentation
3. Verify current request format
4. Update code if format changed

---

## Prevention

**To avoid 500 errors:**

1. **Monitor Credits:**
   - Set up alerts for low credits
   - Keep credits balance above threshold

2. **Handle Errors Gracefully:**
   - Implement retry logic for transient errors
   - Log detailed error information
   - Fall back to alternative providers if needed

3. **Stay Updated:**
   - Check D-ID documentation regularly
   - Subscribe to D-ID status updates
   - Monitor D-ID changelog

4. **Test Regularly:**
   - Run diagnostic script weekly
   - Test with minimal payloads
   - Verify account status

---

## Additional Resources

- **D-ID Documentation:** https://docs.d-id.com/
- **D-ID Dashboard:** https://studio.d-id.com/
- **D-ID Support:** https://support.d-id.com/
- **API Reference:** https://docs.d-id.com/reference/talks-create

