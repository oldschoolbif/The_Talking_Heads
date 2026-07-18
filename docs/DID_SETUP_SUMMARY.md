# D-ID Setup Summary & Action Plan

## Current Status

### What We Know ✅
1. **D-ID API Endpoint**: https://api.d-id.com
2. **Infrastructure**: AWS API Gateway in us-west-2 (Oregon)
3. **Authentication Required**: AWS Signature V4
4. **Service Name**: execute-api
5. **Your Current Credentials**: username:password format (44 chars)

### What's Not Working ❌
- Current API key format is incompatible with AWS SigV4
- Error: "The security token included in the request is invalid"
- Cannot authenticate with D-ID API

---

## The Issue Explained

D-ID uses AWS API Gateway, which requires **AWS IAM credentials**:
- AWS Access Key ID (starts with `AKIA`)
- AWS Secret Access Key (40 characters)

Your current API key (`username:password`) is a D-ID-specific key that needs to be:
- Converted to AWS credentials by D-ID backend, OR
- Replaced with proper AWS IAM credentials from D-ID dashboard

---

## Action Plan: Check D-ID Dashboard

### Step 1: Log into D-ID Studio
Go to: https://studio.d-id.com

### Step 2: Find API Credentials
Look in these sections (in order):

1. **Settings → API Keys**
   - Click profile icon → Settings
   - Look for "API" or "API Keys" tab

2. **Developer Section**
   - Main navigation → "Developers" or "API"
   - Look for credential management

3. **Account → Integration**
   - Account settings
   - Integration or API access section

### Step 3: What to Look For

You need to find **ONE of these**:

**Option A: AWS IAM Credentials (Best)**
```
AWS Access Key ID: AKIA****************
AWS Secret Access Key: ****************************************
```

**Option B: Different API Key Format**
```
API Key: sk-************************************
```
or
```
Bearer Token: eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Option C: Multiple Credential Types**
- Dropdown showing "Basic" vs "AWS" vs "Production"
- Button to "Generate AWS Credentials"
- Tab switching between credential types

### Step 4: Screenshot & Report

Take screenshots (remove sensitive data) and report:
- What credential types are available
- What the dashboard shows
- Any documentation links in the dashboard

---

## If You Find AWS Credentials

### Update Your `.env` File

Replace or add these lines:
```bash
# D-ID AWS IAM Credentials (from dashboard)
DID_AWS_ACCESS_KEY_ID=AKIA****************
DID_AWS_SECRET_ACCESS_KEY=****************************************
DID_AWS_REGION=us-west-2

# Keep or comment out the old format:
# DID_API_KEY=username:password
```

### Test Authentication
```bash
python scripts/test_did_aws_credentials.py
```

### If Successful
```bash
# I'll update the DIDProvider to use AWS credentials
# Then test end-to-end:
python scripts/generate_with_progress.py
```

---

## If Dashboard Doesn't Show AWS Credentials

### Possible Reasons:

1. **Free Tier Limitation**
   - AWS credentials may be enterprise-only
   - Basic auth may be for different endpoint

2. **API Version Difference**
   - Free tier uses different API (simpler auth)
   - Enterprise uses AWS API Gateway

3. **Account Setup Required**
   - May need to enable "Developer Access"
   - May need to verify email or complete setup

### What to Do:

**Option 1: Contact D-ID Support**
- Use support button in dashboard
- Or email: support@d-id.com
- Use template from `DID_CREDENTIAL_CHECK_GUIDE.md`

**Option 2: Check D-ID Documentation**
- https://docs.d-id.com
- Look for "Authentication" section
- Check for Python examples

**Option 3: Search for D-ID Python SDK**
- May have official SDK that handles auth
- Check: https://github.com/d-id
- PyPI: https://pypi.org/search/?q=d-id

---

## Alternatives (If D-ID is Blocked)

### Immediate Testing Options:

**1. MockAvatarProvider** (Free, 0 cost)
```yaml
# config/config.yaml
avatar:
  engine: "mock"
```
- ✅ Tests full pipeline
- ✅ No API costs
- ✅ Immediate results
- ⚠️ Colored backgrounds (not realistic avatars)
- ✅ Perfect for smoke testing

**2. HeyGen** (Paid, Production-Ready)
```yaml
# config/config.yaml
avatar:
  engine: "heygen"
```
- ✅ 100% working
- ✅ Webhook support
- ✅ High-quality avatars
- 💰 ~$0.15-0.30 per minute
- ✅ Ready for production

### Other Alternatives (Require Setup):

**3. Runway ML** (Gen-2)
- ✅ Free tier available
- 🎨 AI-generated video
- ⚠️ Not traditional avatars
- 📚 Different approach

**4. Synthesia**
- 🎨 Very high quality
- 💰💰 Expensive ($30+/month)
- 🔒 May require enterprise

**5. Rephrase.ai**
- 🎨 Good quality
- 💰 Paid service
- 📚 Developer-friendly

See `docs/AVATAR_API_ALTERNATIVES.md` for full comparison.

---

## My Recommendation

### For Smoke Testing (Your Goal):

**Best**: MockAvatarProvider
- Free
- Immediate
- Tests entire pipeline
- Validates all functionality
- No API dependencies

**Good**: HeyGen  
- Paid but working
- Production-quality
- Small cost for testing

**If Time Allows**: D-ID
- Continue investigating
- Contact support
- Add later when resolved

---

## Timeline Estimate

### D-ID Investigation:
- Dashboard check: 5-10 minutes
- If credentials found: 10 minutes to test
- If support needed: 1-2 days for response
- **Total**: Unknown (depends on dashboard)

### Alternative Approaches:
- MockAvatarProvider: Ready now (0 minutes)
- HeyGen testing: Ready now (5 minutes)
- **Total**: Immediate

---

## What I Need From You

Please check the D-ID dashboard and report:

1. **What credential types do you see?**
   - Only username:password?
   - AWS credentials option?
   - Other formats?

2. **Are there any Python code examples?**
   - How do they show authentication?
   - What headers do they use?

3. **What does the API documentation say?**
   - Links to auth docs in dashboard?
   - Examples or tutorials?

4. **Your preference:**
   - Continue with D-ID investigation?
   - Use MockProvider for smoke testing now?
   - Use HeyGen for realistic testing?

Let me know what you find, and I'll proceed accordingly!

