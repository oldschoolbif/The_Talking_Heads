# D-ID Dashboard: Visual Guide with Exact Clicks

## 🎯 This Guide Shows You Exactly Where to Click

---

## 📍 Starting Point: D-ID Studio Dashboard

**What you should see:**
- A website with D-ID branding
- Possibly a dashboard with projects or videos
- Your name or profile icon in the **top-right corner**

**Look for this in the top-right:**
```
┌─────────────────────────────────┐
│  [Logo]  D-ID Studio    [You] 👤│  ← Click here
└─────────────────────────────────┘
```

---

## 🖱️ Click 1: Your Profile/Account

**Location:** Top-right corner of the page

**What to look for:**
- A circle with your initials (like "JD" or "AB")
- Your profile picture
- Your name or email
- Three dots (⋯) or three lines (☰)

**Visual:**
```
                    ┌─────┐
                    │ 👤  │  ← Click this
                    └─────┘
```

**After clicking, you should see a menu like:**
```
┌─────────────────────┐
│ Profile             │
│ Settings      ← Click this
│ Billing            │
│ Logout             │
└─────────────────────┘
```

---

## 🖱️ Click 2: Settings

**In the dropdown menu, click "Settings"**

**You should now see a Settings page with tabs or sections**

**Common layouts:**

### Layout A: Tabs at Top
```
┌─────────────────────────────────────┐
│ [Profile] [API] [Billing] [Security]│
│         ↑                            │
│    Click this tab                    │
└─────────────────────────────────────┘
```

### Layout B: Sidebar on Left
```
┌──────┬──────────────────────────────┐
│      │                              │
│ API  │  Main content area           │
│      │                              │
│      │  ← Click "API" in sidebar    │
└──────┴──────────────────────────────┘
```

### Layout C: Sections on Page
```
┌─────────────────────────────────────┐
│ Settings                            │
│                                     │
│ Profile Settings                    │
│ API Settings  ← Scroll to this     │
│ Billing                             │
│ Security                            │
└─────────────────────────────────────┘
```

---

## 🔍 What to Look For on API Page

**Once you're on the API page, scan for these keywords:**

### Keywords to Search For:
- **AWS**
- **Access Key**
- **Secret Key**
- **IAM**
- **Credentials**
- **Generate**
- **Create**
- **Developer**

**Use your browser's search (Ctrl+F or Cmd+F) to find these words!**

---

## 📋 Common API Page Layouts

### Layout 1: Simple API Key Display
```
┌─────────────────────────────────────┐
│ API Settings                         │
│                                     │
│ API Key:                            │
│ ┌─────────────────────────────────┐ │
│ │ username:password               │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Copy] [Regenerate]                 │
└─────────────────────────────────────┘
```
**If you see this:** You only have basic key (not AWS credentials)

### Layout 2: Multiple Credential Types
```
┌─────────────────────────────────────┐
│ API Settings                         │
│                                     │
│ Credential Type:                    │
│ ┌─────────────────────────────────┐ │
│ │ Basic API Key          ▼        │ │ ← Dropdown
│ └─────────────────────────────────┘ │
│                                     │
│ [Generate New Key]                  │
└─────────────────────────────────────┘
```
**If you see this:** Click the dropdown, look for "AWS Credentials"

### Layout 3: Tabs for Different Keys
```
┌─────────────────────────────────────┐
│ [Basic] [AWS] [Production]           │
│         ↑                            │
│    Click "AWS" tab                   │
└─────────────────────────────────────┘
```
**If you see this:** Click the "AWS" tab

### Layout 4: Sections with Expand/Collapse
```
┌─────────────────────────────────────┐
│ API Settings                         │
│                                     │
│ ▶ Basic API Key                     │
│ ▶ AWS Credentials  ← Click to expand│
│ ▶ Webhook Settings                  │
└─────────────────────────────────────┘
```
**If you see this:** Click to expand "AWS Credentials"

---

## ✅ What AWS Credentials Look Like

**If you find AWS credentials, they'll look like this:**

```
┌─────────────────────────────────────┐
│ AWS Credentials                      │
│                                     │
│ AWS Access Key ID:                  │
│ ┌─────────────────────────────────┐ │
│ │ AKIAIOSFODNN7EXAMPLE             │ │ ← Starts with "AKIA"
│ └─────────────────────────────────┘ │
│                                     │
│ AWS Secret Access Key:              │
│ ┌─────────────────────────────────┐ │
│ │ wJalrXUtnFEMI/K7MDENG/bPxRfiCY   │ │ ← Long random string
│ └─────────────────────────────────┘ │
│                                     │
│ Region: us-west-2                  │
│                                     │
│ [Copy] [Show] [Hide]                │
└─────────────────────────────────────┘
```

**Key indicators:**
- ✅ Access Key starts with "AKIA"
- ✅ Secret Key is long (40+ characters)
- ✅ Both are shown (not just one)

---

## ❌ What You Might See Instead

### Only Basic API Key:
```
┌─────────────────────────────────────┐
│ API Key                             │
│ ┌─────────────────────────────────┐ │
│ │ am9obi5kb2V:Pa3ZdqTaPJf8chGx    │ │ ← username:password
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```
**This is what you already have - not AWS credentials**

### "Coming Soon" or Grayed Out:
```
┌─────────────────────────────────────┐
│ AWS Credentials (Coming Soon)       │
│                                     │
│ [Button is grayed out]              │
└─────────────────────────────────────┘
```
**This means AWS credentials aren't available yet**

### "Upgrade Required":
```
┌─────────────────────────────────────┐
│ AWS Credentials                      │
│                                     │
│ Available for Pro/Enterprise plans  │
│ [Upgrade Now]                       │
└─────────────────────────────────────┘
```
**This means you need a paid plan**

---

## 🔄 Step-by-Step Click Sequence

**Follow these exact clicks:**

```
1. Open browser
   ↓
2. Go to studio.d-id.com
   ↓
3. Log in (if needed)
   ↓
4. Click your profile icon (top-right) 👤
   ↓
5. Click "Settings" in dropdown
   ↓
6. Look for "API" tab/section
   ↓
7. Click "API"
   ↓
8. Scan page for "AWS" keywords
   ↓
9. Check all tabs/dropdowns
   ↓
10. Report what you find
```

---

## 🆘 If You Get Lost

**At any point, tell me:**

1. **What page are you on?**
   - "I'm on the dashboard"
   - "I'm on the settings page"
   - "I'm on the API page"

2. **What do you see?**
   - List all the text/buttons you see
   - Describe the layout

3. **What did you click?**
   - "I clicked my profile icon"
   - "I clicked Settings"
   - "I don't see Settings"

**I'll guide you from there!**

---

## 📸 Screenshot Guide

**If you want to take screenshots:**

1. **Press Windows key + Shift + S** (Windows)
   - Or use Snipping Tool
   - Or press Print Screen

2. **What to screenshot:**
   - The Settings page (all tabs visible)
   - The API page (entire page)
   - Any credential options

3. **Before sharing:**
   - **BLUR or COVER** any actual keys/passwords
   - Use Paint or any image editor
   - Draw black boxes over sensitive data

4. **Or just describe:**
   - "I see three tabs: Profile, API, Billing"
   - "On API page, I see one text box with my key"
   - "No AWS section anywhere"

---

## 🎯 Quick Test: Can You Find Settings?

**Before we go further, try this:**

1. **Go to:** https://studio.d-id.com
2. **Log in** (if needed)
3. **Look at top-right corner**
4. **Do you see your name or profile icon?**
   - YES → Click it, look for Settings
   - NO → Tell me what you see instead

**This tells us if we're on the right track!**

---

## 💡 Pro Tips

**Use browser search:**
- Press **Ctrl+F** (Windows) or **Cmd+F** (Mac)
- Type "AWS" or "API"
- Browser will highlight where these words appear

**Check all tabs:**
- Don't just look at the first tab
- Click through ALL tabs on the page
- Some dashboards hide AWS credentials in "Advanced" or "Developer" tabs

**Scroll down:**
- Don't just look at the top of the page
- Scroll all the way down
- Some settings are at the bottom

**Check for expandable sections:**
- Look for arrows (▶) or "Show More" buttons
- Click to expand sections
- AWS credentials might be hidden in collapsed sections

---

## 📝 Quick Checklist

**Use this while checking:**

```
□ I'm logged into studio.d-id.com
□ I can see my profile icon/name (top-right)
□ I clicked on it
□ I see a menu with "Settings"
□ I clicked "Settings"
□ I'm now on a Settings page
□ I can see an "API" tab or section
□ I clicked on "API"
□ I'm now on the API page
□ I searched for "AWS" (Ctrl+F)
□ I checked all tabs on the API page
□ I scrolled down the entire page
□ I expanded any collapsed sections
□ I documented what I found
```

---

## 🎬 Next Steps After Checking

**Once you've checked everything:**

**Tell me one of these:**

1. **"I found AWS credentials!"**
   → I'll help you add them to `.env` and test

2. **"I only see username:password"**
   → We'll use MockProvider or HeyGen instead

3. **"I can't find Settings/API section"**
   → I'll help you navigate or we'll use alternatives

4. **"I see something different"**
   → Describe it, I'll adapt the instructions

**Remember: There's no wrong answer!** Just checking is the goal. 🎯

