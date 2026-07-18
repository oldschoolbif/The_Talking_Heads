# How to Get DreamTalk Checkpoints

DreamTalk checkpoints are **not publicly available** due to social impact considerations. You must request access from the maintainers.

## Step-by-Step Process

### Step 1: Send Email Request

**Email Address:** `mayf18@mails.tsinghua.edu.cn`

**Subject:** Request for DreamTalk Checkpoints

**Email Template:**

```
Dear DreamTalk Team,

I am requesting access to DreamTalk checkpoints for academic research purposes.

I understand and agree to use the provided checkpoints solely for academic research purposes, as stated in your terms.

[Your Name]
[Your Affiliation/University]
[Your Email]
```

**Important:** By sending this email, you are agreeing to use the checkpoints **solely for academic research purposes**.

### Step 2: Wait for Response

- The maintainers will review your request
- Response time is typically a few days to a week
- They will provide download instructions if approved

### Step 3: Download Checkpoints

Once approved, you'll receive instructions to download:

- **`denoising_network.pth`** - Main diffusion model checkpoint
- **`renderer.pt`** - Video renderer checkpoint

These files are typically large (several GB each).

### Step 4: Place Checkpoint Files

Place the downloaded checkpoint files in the DreamTalk checkpoints directory:

**Windows:**
```
C:\Users\<username>\dreamtalk\checkpoints\
```

**Linux/WSL:**
```
~/dreamtalk/checkpoints/
```

**Required files:**
- `checkpoints/denoising_network.pth`
- `checkpoints/renderer.pt`

### Step 5: Verify Installation

Run the smoke test to verify DreamTalk is now available:

```bash
cd D:\dev\The_Talking_Heads
python scripts/smoke_test_avatar_providers.py
```

You should see:
```
[OK] DreamTalk provider initialized
[OK] DreamTalk is available
```

## Important Notes

### Usage Restrictions

- ✅ **Allowed:** Academic research purposes only
- ❌ **Not Allowed:** Commercial use (without separate licensing)
- ❌ **Not Allowed:** Public distribution of checkpoints

### File Sizes

- Checkpoints are typically **several GB each**
- Ensure you have sufficient disk space (~10-20 GB recommended)
- Download may take time depending on your connection

### Alternative Options

If you cannot obtain checkpoints:

1. **Use other avatar providers:**
   - HeyGen (cloud API, requires subscription)
   - D-ID (cloud API, requires subscription)
   - SadTalker (open source alternative, may have different quality)

2. **Contact maintainers:**
   - If you have specific research needs, explain them in your email
   - They may provide additional guidance or alternatives

## Troubleshooting

### "Checkpoints not found" error

**Check:**
1. Files are in the correct directory: `dreamtalk/checkpoints/`
2. File names are exactly: `denoising_network.pth` and `renderer.pt`
3. Files are not corrupted (check file sizes match expected)

### Email not responded to

**Wait:**
- Response can take 1-2 weeks
- Check spam/junk folder
- Consider following up after 2 weeks if no response

### Commercial use

**Contact:**
- If you need checkpoints for commercial purposes, explicitly state this in your email
- You may need to negotiate separate licensing terms

## Current Status

**Checkpoint Location:** `C:\Users\dpipe\dreamtalk\checkpoints\`

**Required Files:**
- ❌ `denoising_network.pth` - **MISSING**
- ❌ `renderer.pt` - **MISSING**

**Next Step:** Send email request to `mayf18@mails.tsinghua.edu.cn`

## Resources

- **DreamTalk GitHub:** https://github.com/ali-vilab/dreamtalk
- **DreamTalk Project Page:** https://dreamtalk-project.github.io/
- **Setup Documentation:** `docs/DREAMTALK_SETUP.md`
- **dlib Installation:** `docs/DREAMTALK_DLIB_INSTALL.md`

## Summary

1. 📧 Email: `mayf18@mails.tsinghua.edu.cn`
2. ⏳ Wait for approval and download instructions
3. 📥 Download checkpoint files
4. 📁 Place in `dreamtalk/checkpoints/`
5. ✅ Run smoke test to verify

Once checkpoints are in place, DreamTalk will be fully functional for local GPU-based avatar generation!

