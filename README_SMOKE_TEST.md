# 🎯 Smoke Test Guide - Start Here

## Current Situation

✅ **Webhook infrastructure:** Fully tested and working  
❌ **D-ID authentication:** Blocked - needs AWS IAM credentials  
✅ **HeyGen integration:** 100% functional  
✅ **MockProvider:** Ready for immediate free testing  

---

## 🚀 Three Ways to Smoke Test (Choose One)

### Option 1: FREE Smoke Test (Recommended) - 30 Seconds

**Use MockAvatarProvider** - Tests full pipeline at zero cost

```bash
# Step 1: Edit config/config.yaml (line 21)
# Change from:
  engine: "heygen"
# To:
  engine: "mock"

# Step 2: Run
python scripts/generate_with_progress.py

# Step 3: Check output
# File: examples/outputs/multi_persona_episode_podcast.mp4
```

**What you get:**
- ✅ Real ElevenLabs voices (Alice & Bob)
- ✅ Professional audio mixing  
- ✅ Full video composition
- ✅ All pipeline features tested
- ⚠️ Colored backgrounds (not real avatars)

**Time:** 1-2 minutes  
**Cost:** $0  
**Tests:** 95% of pipeline

---

### Option 2: PAID Realistic Test - 0 Seconds Setup

**Use HeyGen** - Already configured and working

```bash
# Already set in config! Just run:
python scripts/generate_with_progress.py

# HeyGen will:
# - Generate real avatar videos
# - Use webhooks for status updates
# - Create production-quality output
```

**What you get:**
- ✅ Real animated avatars
- ✅ Lip-sync to audio
- ✅ Professional quality
- ✅ Production-ready

**Time:** 2-5 minutes  
**Cost:** ~$0.08-0.30  
**Tests:** 100% of pipeline

---

### Option 3: FREE with D-ID (If You Can Fix Auth)

**Get AWS credentials from D-ID dashboard**

```bash
# Step 1: Check dashboard
# Visit: https://studio.d-id.com → Settings → API
# Look for: AWS Access Key ID & Secret Access Key

# Step 2: If found, add to .env:
DID_AWS_ACCESS_KEY_ID=AKIA****************
DID_AWS_SECRET_ACCESS_KEY=****************************************
DID_AWS_REGION=us-west-2

# Step 3: Test authentication:
python scripts/test_did_aws_credentials.py

# Step 4: If successful, change config:
# config/config.yaml: avatar.engine: "did"

# Step 5: Run:
python scripts/generate_with_progress.py
```

**What you get:**
- ✅ Real avatars
- ✅ Free trial
- ✅ High quality

**Time:** Unknown (depends on dashboard)  
**Cost:** Free (trial period)  
**Tests:** 100% (if authentication works)

---

## 🎓 D-ID Dashboard Check Guide

### What to Look For in https://studio.d-id.com:

**Location 1: Settings → API Keys**
- Profile icon (top-right) → Settings
- Look for "API" or "API Keys" tab
- Check for **"AWS Credentials"** section

**Location 2: Multiple Credential Types**
Look for:
- Dropdown showing credential types
- Tab switching between "Basic" and "AWS"
- "Generate AWS Credentials" button

**Location 3: Documentation/Code Examples**
- Check code examples in dashboard
- See what authentication they show
- Look for Python examples

### What to Report:
1. ✅ Do you see AWS Access Key ID / Secret Access Key?
2. ✅ Do you see multiple credential type options?
3. ✅ What authentication does D-ID documentation show?
4. ✅ Can you screenshot the API settings page? (remove sensitive data)

---

## 🆘 If D-ID Dashboard Doesn't Show AWS Credentials

**Possible reasons:**
1. Free tier uses different authentication
2. AWS credentials are enterprise-only
3. API changed and docs are outdated
4. Need to enable "Developer Access" in account

**What to do:**
1. Contact D-ID support (support button in dashboard)
2. Ask: "Where are AWS IAM credentials for api.d-id.com?"
3. Use alternative while waiting (Mock or HeyGen)

---

## 🎬 Quick Commands

```bash
# Smoke test with Mock (FREE) - recommended
python scripts/generate_with_progress.py

# Check D-ID credentials
python scripts/diagnose_did_credentials.py

# Test if D-ID AWS creds work (after dashboard check)
python scripts/test_did_aws_credentials.py

# Test HeyGen (PAID but working)
# (ensure config has engine: "heygen")
python scripts/generate_with_progress.py
```

---

## 📊 My Recommendation for Smoke Testing

### Best Approach (Parallel Tasks):

**NOW (30 seconds):**
1. Change `config/config.yaml` → `avatar.engine: "mock"`
2. Run `python scripts/generate_with_progress.py`
3. Validate pipeline works ✅

**PARALLEL (5-10 minutes):**
1. Check D-ID dashboard for AWS credentials
2. Screenshot API settings page
3. Report what you find

**RESULT:**
- ✅ Pipeline validated immediately (smoke test complete)
- ✅ Know if D-ID credentials available
- ✅ Can proceed with best option

---

## 🎯 Bottom Line

**For SMOKE TESTING specifically:**

**MockAvatarProvider is perfect because:**
- ✅ $0 cost (ideal for testing)
- ✅ Ready immediately (no setup needed)
- ✅ Tests full pipeline (validates all functionality)
- ✅ Real audio (validates TTS integration)
- ✅ Real video composition (validates FFmpeg)
- ⚠️ Placeholders only where avatars would be

**This is EXACTLY what smoke testing is for** - validating the system works before investing in production assets.

---

## 📞 What I Need From You

**Choose your path:**

1. **"Run smoke test with Mock"** → I'll guide you through config change and running it
2. **"Check D-ID dashboard first"** → Use checklist, report findings
3. **"Use HeyGen instead"** → We run test with real avatars (small cost)
4. **"All of the above"** → Mock test now, check D-ID parallel

What would you like to do?

