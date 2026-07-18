# Installation Guide for Build Tools
# This script provides step-by-step instructions

Write-Host "=== Build Tools Installation Guide ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "You need to install TWO tools:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Visual Studio Build Tools (for C++ compilation)" -ForegroundColor White
Write-Host "2. CUDA Toolkit 12.x (for CUDA compilation)" -ForegroundColor White
Write-Host ""

Write-Host "=== STEP 1: Visual Studio Build Tools ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option A: Build Tools (Recommended - Smaller, ~3-4 GB)" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Download:" -ForegroundColor White
Write-Host "   https://visualstudio.microsoft.com/downloads/" -ForegroundColor Cyan
Write-Host "   Scroll to 'Tools for Visual Studio' section" -ForegroundColor Gray
Write-Host "   Click 'Build Tools for Visual Studio 2022'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run installer:" -ForegroundColor White
Write-Host "   - Select 'C++ build tools' workload" -ForegroundColor Gray
Write-Host "   - Under 'Installation details', ensure:" -ForegroundColor Gray
Write-Host "     ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools" -ForegroundColor Green
Write-Host "     ✅ Windows 10/11 SDK (latest)" -ForegroundColor Green
Write-Host "     ✅ C++ CMake tools for Windows" -ForegroundColor Green
Write-Host "   - Click 'Install' (takes 15-30 minutes)" -ForegroundColor Gray
Write-Host ""
Write-Host "Option B: Visual Studio Community (Full IDE, ~6-8 GB)" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Download:" -ForegroundColor White
Write-Host "   https://visualstudio.microsoft.com/vs/community/" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Run installer:" -ForegroundColor White
Write-Host "   - Select 'Desktop development with C++' workload" -ForegroundColor Gray
Write-Host "   - Install (takes 30-60 minutes)" -ForegroundColor Gray
Write-Host ""

Write-Host "=== STEP 2: CUDA Toolkit 12.x ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your PyTorch expects CUDA 12.1" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Download CUDA Toolkit 12.4 (or 12.1):" -ForegroundColor White
Write-Host "   https://developer.nvidia.com/cuda-downloads" -ForegroundColor Cyan
Write-Host "   Select:" -ForegroundColor Gray
Write-Host "   - Operating System: Windows" -ForegroundColor Gray
Write-Host "   - Architecture: x86_64" -ForegroundColor Gray
Write-Host "   - Version: Windows 10/11" -ForegroundColor Gray
Write-Host "   - Installer Type: exe (local)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run installer:" -ForegroundColor White
Write-Host "   - Choose 'Express Installation'" -ForegroundColor Gray
Write-Host "   - Takes 10-15 minutes" -ForegroundColor Gray
Write-Host ""

Write-Host "=== STEP 3: After Installation ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. CLOSE this PowerShell window" -ForegroundColor Yellow
Write-Host "2. Open a NEW PowerShell window (to get updated PATH)" -ForegroundColor Yellow
Write-Host "3. Run verification:" -ForegroundColor Yellow
Write-Host "   cd d:\dev\The_Talking_Heads" -ForegroundColor Gray
Write-Host "   .\scripts\check_build_tools.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "=== Quick Links ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Visual Studio Build Tools:" -ForegroundColor White
Write-Host "https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022" -ForegroundColor Cyan
Write-Host ""
Write-Host "CUDA Toolkit:" -ForegroundColor White
Write-Host "https://developer.nvidia.com/cuda-downloads" -ForegroundColor Cyan
Write-Host ""

$openLinks = Read-Host "Open download pages in browser? (Y/N)"
if ($openLinks -eq "Y" -or $openLinks -eq "y") {
    Start-Process "https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022"
    Start-Sleep -Seconds 2
    Start-Process "https://developer.nvidia.com/cuda-downloads"
    Write-Host ""
    Write-Host "[INFO] Download pages opened in browser" -ForegroundColor Green
}

Write-Host ""
Write-Host "After installing both tools, restart PowerShell and run:" -ForegroundColor Yellow
Write-Host "  .\scripts\check_build_tools.ps1" -ForegroundColor White

