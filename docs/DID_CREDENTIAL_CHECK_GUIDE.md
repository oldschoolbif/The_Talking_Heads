# D-ID Credential Check Guide

## Step-by-Step Guide to Finding Proper D-ID Credentials

### Why This Guide?

Your current D-ID API key (`username:password` format) is not working with AWS Signature V4 authentication. D-ID likely provides separate AWS IAM credentials or uses a different authentication method.

---

## Step 1: Access D-ID Studio

1. **Open your browser** and go to: https://studio.d-id.com
2. **Log in** with your account credentials
3. You should see the D-ID Studio dashboard

---

## Step 2: Navigate to API Settings

Look for one of these locations:

### Option A: Settings Menu
1. Click your **profile/user icon** (usually top-right corner)
2. Look for:
   - "Settings"
   - "Account Settings"
   - "API Settings"
   - "Developer Settings"

### Option B: API/Developer Section
1. Look in the main navigation for:
   - "API"
   - "Developers"
   - "Integrations"
   - "API Keys"

### Option C: Direct URL
Try navigating directly to:
- https://studio.d-id.com/settings
- https://studio.d-id.com/api
- https://studio.d-id.com/account/api

---

## Step 3: Look for These Credential Types

Once in the API/Settings section, look for:

### ✅ What We Need:

**Option 1: AWS Credentials (Best)**
```
AWS Access Key ID: AKIA****************
AWS Secret Access Key: ****************************************
AWS Region: us-west-2
```

**Option 2: API Key with Different Format**
```
API Key: sk-************************************
```
(Similar to OpenAI format)

**Option 3: Bearer Token**
```
Bearer Token: eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Option 4: Multiple Credential Types**
D-ID may offer different credential types for different purposes:
- Basic API Key (what you have)
- AWS IAM Credentials (what we need)
- Developer Token
- Production API Key

---

## Step 4: Look for Documentation Links

In the D-ID dashboard, look for:
- "API Documentation" link
- "Getting Started" guide
- "Authentication" section
- Code examples (especially Python)

**What to check**:
- How they show authentication in code examples
- What credential format they use
- If they mention AWS or SigV4

---

## Step 5: Check for API Version

D-ID may have multiple API versions:
- REST API v1
- REST API v2
- Studio API
- Legacy API

**Look for**:
- Version selector or dropdown
- Different endpoints for different versions
- Migration guides

---

## Step 6: Try the API Playground (if available)

Many API services have a built-in testing tool:
1. Look for "API Playground", "Try it", or "Test API"
2. Try making a request to `/avatars` endpoint
3. **Check the request headers** - this shows the correct authentication format
4. Use browser Developer Tools (F12) → Network tab to see actual request

---

## Step 7: Contact D-ID Support

If you can't find the proper credentials, D-ID support can help:

**Where to Contact**:
- Look for "Support", "Help", or "Contact" in the dashboard
- Check for live chat widget
- Email: support@d-id.com (if available)

**What to Ask**:
```
Subject: AWS Signature V4 Authentication for api.d-id.com

Hello,

I'm integrating with the D-ID API at https://api.d-id.com and receiving
authentication errors. The API appears to require AWS Signature V4
authentication.

My findings:
- Region: us-west-2 (from IP analysis)
- Service: execute-api
- Error: "The security token included in the request is invalid"

Questions:
1. What is the correct authentication method for api.d-id.com?
2. Do I need AWS IAM credentials, or is there a different auth method?
3. Where can I find the proper credentials in my dashboard?
4. Is there a Python SDK that handles authentication automatically?

My current API key format: username:password (from Studio → Settings)
Project: Multi-persona podcast generation with avatars

Thank you!
```

---

## Step 8: Check for Python SDK

D-ID may have an official Python SDK that handles auth automatically:

**Search for**:
- https://github.com/d-id
- https://pypi.org/search/?q=d-id
- In D-ID docs: "SDK", "Libraries", "Python"

**If SDK exists**:
```bash
pip install d-id-client  # (or whatever the package name is)
```

The SDK would handle authentication automatically.

---

## What to Report Back

After checking, please report:

1. **What you found in the dashboard**:
   - Screenshots of Settings/API page (remove sensitive parts)
   - List of available credential types
   - Any authentication documentation

2. **Current API key format**:
   - Does it look like: `username:password`
   - Or something else: `sk-****`, `AKIA****`, etc.

3. **Any code examples**:
   - How D-ID shows authentication in their docs
   - What headers they use

4. **SDK availability**:
   - Is there a Python SDK?
   - What's the package name?

---

## Meanwhile: Alternative for Testing

While investigating D-ID credentials, you can:

### Option 1: Use MockAvatarProvider (Free, Immediate)
```yaml
# config/config.yaml
avatar:
  engine: "mock"
```
- Tests entire pipeline
- No API costs
- Validates all functionality
- Just uses colored backgrounds instead of real avatars

### Option 2: Use HeyGen (Paid, Production-Ready)
```yaml
# config/config.yaml  
avatar:
  engine: "heygen"
```
- Already 100% working
- Webhook support tested
- High-quality avatars
- Requires credits (~$0.15-0.30 per minute)

---

## Next Steps After Finding Credentials

Once you find the proper credentials:

1. **Update `.env` file**:
```bash
# If AWS credentials:
DID_AWS_ACCESS_KEY_ID=AKIA****************
DID_AWS_SECRET_ACCESS_KEY=****************************************
DID_AWS_REGION=us-west-2

# Or if different format:
DID_API_KEY=your_new_key_format
```

2. **Update code** (if needed):
```python
# I'll update DIDProvider to use the correct credential format
```

3. **Test authentication**:
```bash
python scripts/test_did_comprehensive.py
```

4. **Generate first video**:
```bash
python scripts/generate_with_progress.py
```

---

## Summary

**Immediate Actions**:
1. ✅ Check D-ID dashboard for proper credentials
2. ✅ Look for AWS IAM credentials or alternative auth method
3. ✅ Check for Python SDK
4. ✅ Contact support if credentials not found

**Fallback Options**:
- Use MockAvatarProvider for free testing
- Use HeyGen for production-quality testing

Let me know what you find in the dashboard!

