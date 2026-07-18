# D-ID Troubleshooting: Step-by-Step Guide

## 🎯 Goal
Find AWS IAM credentials in your D-ID dashboard so we can authenticate with the D-ID API.

---

## 📋 Prerequisites

Before starting:
- ✅ You have a D-ID account (you have an API key, so you must have an account)
- ✅ You can log into https://studio.d-id.com
- ✅ You have a web browser (Chrome, Firefox, Edge, etc.)

---

## 🚀 Step-by-Step Instructions

### STEP 1: Open D-ID Studio

1. **Open your web browser** (Chrome, Firefox, Edge, etc.)

2. **Type or paste this URL** in the address bar:
   ```
   https://studio.d-id.com
   ```

3. **Press Enter** to go to the website

4. **You should see:** The D-ID Studio login page or dashboard

---

### STEP 2: Log In (If Needed)

1. **If you see a login page:**
   - Enter your email address
   - Enter your password
   - Click "Sign In" or "Log In" button

2. **If you're already logged in:**
   - Skip to Step 3

3. **If you forgot your password:**
   - Click "Forgot Password" link
   - Follow password reset instructions
   - Then log in

---

### STEP 3: Find Your Profile/Settings

**Look at the TOP-RIGHT corner of the page** for one of these:

#### Option A: Profile Icon (Most Common)
- Look for a **circle with your initials** or a **profile picture**
- It's usually in the top-right corner
- **Click on it**

#### Option B: Your Name
- Look for your name or email address in the top-right
- **Click on it**

#### Option C: Menu Button (Three Lines)
- Look for three horizontal lines (☰) or a hamburger menu
- **Click on it**

**What you should see after clicking:**
- A dropdown menu or sidebar appears
- Look for words like: "Settings", "Account", "Profile", "API", "Preferences"

---

### STEP 4: Navigate to Settings

**In the menu that appeared, look for and click on:**

1. **"Settings"** ← Most common name
   OR
2. **"Account Settings"**
   OR
3. **"API Settings"**
   OR
4. **"Developer Settings"**
   OR
5. **"Preferences"**

**What happens:**
- You'll be taken to a settings page
- The page might have tabs or sections

---

### STEP 5: Find the API Section

**On the settings page, look for:**

#### Option A: Tabs at the Top
- You might see tabs like: "Profile", "API", "Billing", "Security"
- **Click on the "API" tab**

#### Option B: Sections/List on the Left Side
- You might see a sidebar with options
- Look for "API" or "API Keys" in the list
- **Click on it**

#### Option C: Sections on the Main Page
- Scroll down the settings page
- Look for a section titled:
  - "API"
  - "API Keys"
  - "API Access"
  - "Developer API"
  - "Integrations"

**Click on the API section**

---

### STEP 6: Examine the API Page

**Once you're on the API page, look carefully for:**

#### What We're Looking For:

**✅ GOOD - What We Need:**
```
AWS Access Key ID: AKIA****************
AWS Secret Access Key: ****************************************
```

OR

```
[Generate AWS Credentials] button
```

OR

```
Credential Type: [Dropdown]
  - Basic API Key
  - AWS Credentials  ← Select this
  - Production API Key
```

**❌ NOT USEFUL - What You Might See:**
```
API Key: username:password
```
(This is what you already have - we need AWS credentials instead)

---

### STEP 7: Document What You See

**Take a screenshot or write down:**

1. **What sections are on the API page?**
   - List all the headings you see
   - Example: "API Keys", "Webhooks", "Usage", etc.

2. **What credential types are available?**
   - Do you see a dropdown or tabs?
   - What are the options?

3. **Do you see "AWS" anywhere?**
   - Look for words: "AWS", "IAM", "Access Key", "Secret Key"
   - Even if it's grayed out or says "Coming Soon"

4. **Are there any buttons?**
   - "Generate", "Create", "Add", "New API Key"
   - What do they say?

5. **Is there documentation?**
   - Links to "API Documentation"
   - "Getting Started" guides
   - Code examples

---

### STEP 8: Check for Multiple Pages/Tabs

**If you see tabs or multiple pages:**

1. **Click through each tab** one by one
2. **Look for:**
   - "Credentials"
   - "Authentication"
   - "AWS"
   - "Developer"
   - "Production"

3. **Check each page carefully**

---

### STEP 9: Look for Code Examples

**Many dashboards show code examples:**

1. **Look for sections like:**
   - "Quick Start"
   - "Code Examples"
   - "Integration Guide"
   - "Python SDK"

2. **Check what authentication they show:**
   - Do they use `Authorization: Basic ...`?
   - Do they use AWS credentials?
   - Do they use a different format?

3. **This tells us what D-ID actually expects**

---

### STEP 10: Check Account Type/Plan

**Some features are only for certain account types:**

1. **Look for:**
   - "Plan: Free", "Plan: Pro", "Plan: Enterprise"
   - "Account Type" or "Subscription"
   - Usually in Settings → Account or Billing

2. **Note your plan type**

3. **AWS credentials might only be available for:**
   - Pro plans
   - Enterprise plans
   - Paid accounts

---

### STEP 11: Look for Help/Support Links

**If you can't find AWS credentials:**

1. **Look for:**
   - "Help" button
   - "Support" link
   - "Contact Us"
   - "Documentation" link
   - Chat widget (usually bottom-right)

2. **These can help you:**
   - Ask where AWS credentials are
   - Get clarification on authentication

---

### STEP 12: Report Your Findings

**After checking everything, tell me:**

#### Scenario A: You Found AWS Credentials ✅
```
"I found AWS credentials! Here they are:
- AWS Access Key ID: AKIA...
- AWS Secret Access Key: ...
- Region: (if shown)"
```

**Then I'll help you:**
1. Add them to `.env` file
2. Test authentication
3. Update the code to use them

#### Scenario B: You Only See Basic API Key ❌
```
"I only see the username:password API key.
No AWS credentials anywhere.
I checked Settings → API and all tabs."
```

**Then we'll:**
1. Use MockProvider for smoke testing
2. Contact D-ID support
3. Or use HeyGen instead

#### Scenario C: You See Multiple Options 🤔
```
"I see a dropdown with:
- Basic API Key
- Production API Key
- Developer Token
But no AWS option"
```

**Then we'll:**
1. Try the Production API Key
2. Check if it works differently
3. Test alternative authentication

#### Scenario D: You Can't Find API Settings 😕
```
"I can't find API settings anywhere.
I see: Profile, Billing, Security
But no API section"
```

**Then we'll:**
1. Check if you need to enable API access
2. Look for "Developer" or "Integrations" section
3. Contact D-ID support

---

## 📸 What to Screenshot (Optional but Helpful)

**If you can, take screenshots of:**

1. **The Settings page** (with all tabs visible)
2. **The API page** (if you find it)
3. **Any credential options** you see
4. **Any code examples** shown

**IMPORTANT:** Before sharing screenshots:
- **Blur or cover** any actual API keys or passwords
- **Show the structure** but hide sensitive data
- Or just describe what you see

---

## 🆘 Troubleshooting Common Issues

### Issue: "I can't log in"
**Solution:**
- Check if you're using the correct email
- Try password reset
- Check if account is active
- Contact D-ID support

### Issue: "I don't see Settings"
**Solution:**
- Look for your name/profile icon (top-right)
- Try clicking on your account name
- Check if there's a menu button (☰)
- Look for "Account" or "Profile" instead

### Issue: "I see Settings but no API section"
**Solution:**
- Scroll down the settings page
- Check all tabs at the top
- Look in sidebar (if present)
- Check "Developer" or "Integrations" sections
- Your account type might not have API access

### Issue: "I see API but only username:password"
**Solution:**
- This is what we expected
- Check if there are tabs or dropdowns
- Look for "Advanced" or "Developer" options
- Check if you need to upgrade plan
- Report this to me - we'll use alternatives

### Issue: "The page looks different than described"
**Solution:**
- D-ID may have updated their interface
- Describe what you actually see
- Take a screenshot (hide sensitive data)
- We'll adapt the instructions

---

## 📝 Checklist - Use This While Checking

**Print this or keep it open while you check:**

- [ ] Logged into https://studio.d-id.com
- [ ] Found profile/settings menu (top-right)
- [ ] Clicked on Settings
- [ ] Found API section/tab
- [ ] Checked all tabs on API page
- [ ] Looked for "AWS" or "IAM" keywords
- [ ] Checked for credential type dropdown
- [ ] Looked for "Generate" or "Create" buttons
- [ ] Checked code examples (if shown)
- [ ] Checked account type/plan
- [ ] Looked for help/support links
- [ ] Documented what I found

---

## 🎯 Quick Decision Tree

**While checking, follow this:**

```
Are you logged in?
├─ NO → Log in first
└─ YES → Continue

Can you find Settings?
├─ NO → Look for profile icon or menu
└─ YES → Continue

Can you find API section?
├─ NO → Check all tabs, scroll down, look for "Developer"
└─ YES → Continue

Do you see AWS credentials?
├─ YES → Copy them, report to me ✅
└─ NO → Continue

Do you see multiple credential types?
├─ YES → List all options, report to me
└─ NO → Continue

Do you only see username:password?
├─ YES → Report this, we'll use alternatives
└─ NO → Describe what you see, report to me
```

---

## 💬 What to Tell Me

**After checking, send me a message like this:**

```
"I checked the D-ID dashboard. Here's what I found:

1. I can log in: YES/NO
2. I found Settings: YES/NO
3. I found API section: YES/NO
4. What I see on API page:
   - [List everything you see]
5. Credential types available:
   - [List all options]
6. Do I see AWS credentials: YES/NO
7. My account type/plan: [Free/Pro/Enterprise/Unknown]
8. Any code examples shown: [Describe]
9. Any buttons I see: [List them]
10. Screenshots: [If you took any]
```

**Even if you find nothing, that's valuable information!**

---

## 🚀 Alternative: Skip D-ID for Now

**If this is too complicated or taking too long:**

**You can skip D-ID and use MockProvider for smoke testing:**

1. **Edit** `config/config.yaml`
2. **Find line 21:** `engine: "heygen"`
3. **Change to:** `engine: "mock"`
4. **Save the file**
5. **Run:** `python scripts/generate_with_progress.py`

**This will:**
- ✅ Test your entire pipeline
- ✅ Cost $0
- ✅ Work immediately
- ✅ Validate everything except real avatar generation

**You can always come back to D-ID later!**

---

## 📞 Need More Help?

**If you're stuck at any step:**

1. **Describe exactly where you are:**
   - "I'm on the dashboard page"
   - "I clicked Settings but I see..."
   - "I don't see any API section"

2. **Tell me what you DO see:**
   - List all menu items
   - List all tabs
   - Describe the page layout

3. **I'll give you specific next steps** based on what you see

---

## 🎓 Remember

**There's no wrong answer!**

- ✅ Finding AWS credentials = Great! We'll use them
- ✅ Not finding them = Also fine! We'll use alternatives
- ✅ Getting confused = Tell me, I'll help you

**The goal is to check, not to stress!**

Take your time, follow the steps, and report back what you find (or don't find). Either way, we'll get your smoke test working! 🚀

