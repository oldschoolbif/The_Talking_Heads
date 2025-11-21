# Quick Start: Push to GitHub

## One-Time Setup

### 1. Create GitHub Repository

Go to https://github.com/new and create a repository named `The_Talking_Heads`

### 2. Connect and Push

```bash
cd d:\dev\The_Talking_Heads

# Set remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/The_Talking_Heads.git

# Commit and push
git add .
git commit -m "Initial commit: Project setup"
git branch -M main
git push -u origin main
```

That's it! 🚀

See [GITHUB_SETUP.md](GITHUB_SETUP.md) for detailed instructions.

