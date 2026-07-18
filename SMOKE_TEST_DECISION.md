# 🚦 Smoke Test Decision - Choose Your Path

## 📊 Your Options (Ranked for Smoke Testing)

### 🥇 OPTION 1: MockAvatarProvider (BEST FOR SMOKE TEST)

**⏱️ Ready in:** 30 seconds  
**💰 Cost:** $0  
**✅ Tests:** 95% of pipeline  

**How to run:**
```bash
# 1. Edit config/config.yaml (change one line):
#    avatar:
#      engine: "mock"

# 2. Run:
python scripts/generate_with_progress.py

# 3. Check output:
#    outputs/multi_persona_episode_podcast.mp4
```

**What you get:**
- ✅ Real ElevenLabs voices (Alice & Bob)
- ✅ Professional audio mixing
- ✅ Full video composition
- ⚠️ Colored backgrounds instead of avatars

**Perfect for:** Pipeline validation, workflow testing, smoke tests

---

### 🥈 OPTION 2: HeyGen (PRODUCTION QUALITY)

**⏱️ Ready in:** 0 seconds (already configured)  
**💰 Cost:** ~$0.08 for 30-second test  
**✅ Tests:** 100% of pipeline  

**How to run:**
```bash
# Already configured! Just run:
python scripts/generate_with_progress.py

# Webhook server will start automatically
# HeyGen will generate real avatars
# Takes 2-5 minutes for video generation
```

**What you get:**
- ✅ Real avatars (professional quality)
- ✅ Lip-sync animation
- ✅ Real ElevenLabs voices
- ✅ Production-ready output

**Perfect for:** Final validation, client demos, production preview

---

### 🥉 OPTION 3: D-ID (BLOCKED - Needs Investigation)

**⏱️ Ready in:** Unknown  
**💰 Cost:** Free trial available  
**✅ Tests:** 100% (if working)  

**How to proceed:**
```bash
# 1. Check D-ID dashboard for AWS credentials:
#    https://studio.d-id.com → Settings → API

# 2. Look for:
#    - AWS Access Key ID (AKIA***)
#    - AWS Secret Access Key

# 3. If found, add to .env:
DID_AWS_ACCESS_KEY_ID=AKIA****************
DID_AWS_SECRET_ACCESS_KEY=****************************************
DID_AWS_REGION=us-west-2

# 4. Test:
python scripts/test_did_aws_credentials.py
```

**Status:** 
- ❌ Current API key format doesn't work
- ⏳ Need AWS IAM credentials from dashboard
- 📞 May need to contact D-ID support

**Perfect for:** Free testing (once auth is fixed)

---

## 🎯 My Recommendation

For **smoke testing** (your stated goal), use this approach:

### Phase 1: Immediate Smoke Test (NOW)
```bash
# Use MockAvatarProvider
# Change config → Run script → Validate pipeline
# Time: 30 seconds
# Cost: $0
```
**Result:** Know if pipeline works end-to-end

### Phase 2: Parallel Investigation (5-10 min)
```bash
# While Mock runs, check D-ID dashboard
# Follow: docs/DID_DASHBOARD_CHECKLIST.md
# Look for AWS credentials
```
**Result:** Find if D-ID credentials exist

### Phase 3: Upgrade (As Needed)
```bash
# If D-ID credentials found → Update .env → Test
# OR
# Use HeyGen for production-quality test
```
**Result:** Real avatar testing

---

## 📈 Testing Progression

```
1. Mock Test (0 cost)
   ↓ validates pipeline
   
2. D-ID Investigation (parallel)
   ↓ if credentials found
   
3. Real Avatar Test
   ├─→ D-ID (if fixed)
   └─→ HeyGen (if D-ID blocked)
```

---

## 🎬 Quick Commands Reference

```bash
# Smoke test with Mock (change config first)
python scripts/generate_with_progress.py

# Check D-ID credentials
python scripts/diagnose_did_credentials.py

# Test D-ID (if you find AWS creds)
python scripts/test_did_aws_credentials.py

# Verify all APIs
python scripts/test_all_apis.py

# Test webhook functionality
python scripts/test_webhook_functionality.py
```

---

## 📋 Checklist for You

- [ ] **Decide:** Mock test now OR investigate D-ID first?
- [ ] **If Mock:** Change config, run script (30 sec)
- [ ] **If D-ID:** Check dashboard for AWS credentials (5-10 min)
- [ ] **Report:** What you found in D-ID dashboard
- [ ] **Next:** Based on findings, proceed to real avatars

---

## 💬 Tell Me

**Which path do you want to take?**

**A)** Run mock smoke test NOW → investigate D-ID later  
**B)** Check D-ID dashboard first → then decide  
**C)** Use HeyGen for immediate realistic test  

I recommend **A** - validate pipeline with Mock while you check D-ID dashboard in parallel.

---

## 📚 Documentation Reference

- `QUICK_START_SMOKE_TEST.md` ← You are here
- `DID_ACTION_REQUIRED.md` ← D-ID credential guide
- `docs/DID_DASHBOARD_CHECKLIST.md` ← Step-by-step dashboard check
- `docs/AVATAR_API_ALTERNATIVES.md` ← All avatar service options
- `docs/WEBHOOK_TEST_RESULTS.md` ← Webhook tests (passed)

Everything is documented and ready. What's your decision?

