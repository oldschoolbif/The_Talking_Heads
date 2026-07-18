# D-ID Dashboard Checklist - Find Your AWS Credentials

## 🎯 Goal
Find the correct AWS IAM credentials or alternative authentication method for D-ID API.

---

## 📋 Quick Checklist

When logged into https://studio.d-id.com, check these locations:

### ✅ Location 1: Settings → API
- [ ] Click your profile icon (top-right)
- [ ] Select "Settings" or "Account Settings"
- [ ] Look for "API" or "API Keys" tab
- [ ] Check for:
  - [ ] "AWS Credentials" section
  - [ ] "Developer Credentials" section  
  - [ ] "API Access" or "API Authentication"
  - [ ] Multiple API key types (Basic, AWS, Production)

### ✅ Location 2: Developer/API Section
- [ ] Look in main navigation for "Developers" or "API"
- [ ] Check for:
  - [ ] "Generate Credentials" button
  - [ ] "Create API Key" with options
  - [ ] Different credential types dropdown

### ✅ Location 3: Account/Billing
- [ ] Check "Account" or "Billing" section
- [ ] Some services hide AWS credentials here
- [ ] Look for "Integration" or "API Access"

### ✅ Location 4: Documentation/Help
- [ ] In-dashboard documentation
- [ ] "Getting Started" guide
- [ ] Code examples (especially Python)
- [ ] Check what authentication they show

---

## 🔍 What to Look For

### Good Signs (What We Need):

**AWS IAM Credentials:**
```
AWS Access Key ID: AKIA****************
AWS Secret Access Key: ****************************************  
Region: us-west-2 (or any region)
```

**Alternative API Key Format:**
```
API Key: sk-proj-************************************
```
or
```
Bearer Token: eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Multiple Credential Options:**
- Dropdown or tabs showing different credential types
- "Production API Key" vs "Test API Key"
- "Basic Auth" vs "AWS Credentials"

### Bad Signs (Not What We Need):

❌ Only showing `username:password` format  
❌ No mention of AWS or IAM credentials  
❌ No alternative credential types available

---

## 📸 What to Capture

If you find something that looks promising:

1. **Screenshot** (remove sensitive parts):
   - Settings/API page
   - Credential generation dialog
   - Any dropdown menus for credential types

2. **Text to copy**:
   - Credential format shown in examples
   - Any authentication documentation
   - Python code examples if available

3. **URLs**:
   - Direct link to API credentials page
   - Link to authentication docs

---

## 🚀 Once You Find Credentials

### If You Find AWS Credentials:

1. **Copy them** carefully (AWS Secret Key shows only once!)

2. **Add to `.env`**:
```bash
# Replace existing DID_API_KEY with these:
DID_AWS_ACCESS_KEY_ID=AKIA****************
DID_AWS_SECRET_ACCESS_KEY=****************************************
DID_AWS_REGION=us-west-2
```

3. **Test authentication**:
```bash
python scripts/test_did_aws_credentials.py
```

4. **I'll update the code** to use AWS credentials

---

### If You Find Alternative API Key Format:

1. **Copy the new API key**

2. **Update `.env`**:
```bash
# Update DID_API_KEY with new format:
DID_API_KEY=sk-proj-************************************
```

3. **Tell me the format** and I'll update the authentication code

---

### If D-ID Dashboard Doesn't Show AWS Credentials:

This could mean:
1. D-ID changed their authentication method
2. AWS credentials are only for enterprise accounts
3. There's a different API endpoint for free tier

**Next steps**:
- Contact D-ID support (support button in dashboard)
- Check if there's a different API for free tier
- Consider alternatives (see `docs/AVATAR_API_ALTERNATIVES.md`)

---

## ⚡ Quick Alternative: MockAvatarProvider

While investigating, you can test the pipeline immediately:

```bash
# 1. Switch to mock provider
# Edit config/config.yaml:
#   avatar:
#     engine: "mock"

# 2. Test the pipeline
python scripts/generate_with_progress.py

# This will:
# ✅ Test full pipeline
# ✅ Generate audio with ElevenLabs
# ✅ Mix audio tracks
# ✅ Create placeholder videos
# ✅ Compose final video
# ✅ Verify all components work
```

---

## 📞 D-ID Support Contact Template

If you need to contact support:

**Subject**: AWS Credentials for API Integration

**Message**:
```
Hello,

I'm integrating with the D-ID API (api.d-id.com) and need help with authentication.

Current situation:
- I have an API key in format: username:password
- The API requires AWS Signature V4 authentication
- My tests show region us-west-2 and service 'execute-api'
- Getting error: "The security token included in the request is invalid"

Questions:
1. Where can I find AWS IAM credentials in my dashboard?
2. Is there a separate AWS Access Key ID and Secret Access Key?
3. Is there a Python SDK that handles authentication?
4. Is my current API key format correct, or do I need different credentials?

Use case: Multi-persona podcast generation with talking avatars

Thank you!
```

---

## 🎯 Decision Point

After checking dashboard:

**Found AWS credentials?**
→ Add to `.env` → Test → Generate videos ✅

**No AWS credentials available?**
→ Contact D-ID support OR use HeyGen/Mock provider

**D-ID too complicated?**
→ Use HeyGen (working now) → Add D-ID later

---

## Summary

1. ✅ Check D-ID dashboard using locations above
2. ✅ Look for AWS IAM credentials
3. ✅ Copy credentials if found
4. ✅ Report back what you found
5. ✅ I'll update the code based on what you find

Let me know what you discover!

