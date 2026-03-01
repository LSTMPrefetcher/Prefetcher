# build_exe_standalone.ps1
<#
.SYNOPSIS
Build standalone Windows EXE for AI File Prefetcher

.DESCRIPTION
This PowerShell script automates the process of converting the Python application
into a standalone Windows executable using PyInstaller.

The process includes:
1. Clean previous builds
2. Install/verify PyInstaller
3. Verify dependencies
4. Run PyInstaller
5. Verify output
6. Provide distribution package info

.EXAMPLE
.\build_exe_standalone.ps1

.NOTES
Requires Python 3.8+ with PyTorch and other dependencies installed.
#>

param(
    [switch]$Clean,
    [switch]$Help,
    [string]$PythonExe = "python"
)

# Configuration
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$BUILD_DIR = Join-Path $PROJECT_ROOT "build"
$DIST_DIR = Join-Path $PROJECT_ROOT "dist"
$SPEC_FILE = Join-Path $PROJECT_ROOT "pyinstaller.spec"
$OUTPUT_NAME = "AiFilePrefetcher"

function Show-Help {
    Write-Host @"
AI File Prefetcher - Build Script
==================================

Usage: .\build_exe_standalone.ps1 [OPTIONS]

OPTIONS:
  -Clean        : Remove old build and dist folders before building
  -PythonExe    : Path to Python executable (default: python)
  -Help         : Show this help message

EXAMPLES:
  # Standard build
  .\build_exe_standalone.ps1

  # Clean build
  .\build_exe_standalone.ps1 -Clean

  # Using specific Python installation
  .\build_exe_standalone.ps1 -PythonExe "C:\Python311\python.exe" -Clean
"@
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[✓] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[✗] $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "[*] $Message" -ForegroundColor White
}

# Handle help flag
if ($Help) {
    Show-Help
    exit 0
}

# Change to project root
Set-Location $PROJECT_ROOT
Write-Info "Working directory: $PROJECT_ROOT"

# Step 1: Clean previous builds
Write-Section "Step 1: Cleaning Previous Builds"

if ($Clean -or (Test-Path $BUILD_DIR) -or (Test-Path $DIST_DIR)) {
    Write-Info "Removing old build artifacts..."
    
    if (Test-Path $BUILD_DIR) {
        Remove-Item -Path $BUILD_DIR -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed: $BUILD_DIR"
    }
    
    if (Test-Path $DIST_DIR) {
        Remove-Item -Path $DIST_DIR -Recurse -Force -ErrorAction SilentlyContinue
        Write-Success "Removed: $DIST_DIR"
    }
} else {
    Write-Info "No previous builds found (or not cleaning)"
}

# Step 2: Verify Python installation
Write-Section "Step 2: Verifying Python Installation"

try {
    $PythonVersion = & $PythonExe --version 2>&1
    Write-Success "Python found: $PythonVersion"
} catch {
    Write-Error-Custom "Python not found at: $PythonExe"
    exit 1
}

# Step 3: Verify required packages
Write-Section "Step 3: Verifying Required Packages"

$RequiredPackages = @('pyinstaller', 'torch', 'pyyaml', 'numpy', 'psutil')

foreach ($Package in $RequiredPackages) {
    Write-Info "Checking $Package..."
    
    $CheckCmd = "import $($Package.Replace('-', '_'))"
    & $PythonExe -c $CheckCmd 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "$Package is installed"
    } else {
        Write-Error-Custom "$Package is NOT installed"
        Write-Info "Install with: pip install $Package"
        exit 1
    }
}

# Step 4: Build with PyInstaller
Write-Section "Step 4: Building Executable with PyInstaller"

Write-Info "Running PyInstaller with spec file: $SPEC_FILE"
Write-Info "This may take 2-5 minutes depending on your system..."
Write-Host ""

# Run PyInstaller
$StartTime = Get-Date
& $PythonExe -m PyInstaller $SPEC_FILE --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "PyInstaller build failed!"
    exit 1
}

$EndTime = Get-Date
$Duration = ($EndTime - $StartTime).TotalSeconds
Write-Success "Build completed in $([Math]::Round($Duration, 2)) seconds"

# Step 5: Verify output
Write-Section "Step 5: Verifying Build Output"

$ExeFile = Join-Path $DIST_DIR "AiFilePrefetcher\AiFilePrefetcher.exe"
$ExeOneFile = Join-Path $DIST_DIR "AiFilePrefetcher.exe"

if (Test-Path $ExeFile) {
    $Size = [math]::Round((Get-Item $ExeFile).Length / 1MB, 2)
    Write-Success "Found executable: $ExeFile ($Size MB)"
} else {
    Write-Error-Custom "Executable not found at expected location"
}

if (Test-Path $DIST_DIR) {
    $FolderSize = [math]::Round((Get-ChildItem -Path $DIST_DIR -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
    Write-Success "Distribution folder: $FolderSize MB total"
} else {
    Write-Error-Custom "Distribution folder not found"
    exit 1
}

# Step 6: Show distribution info
Write-Section "Step 6: Distribution Package Information"

Write-Host @"
Build completed successfully!

EXECUTABLE LOCATION:
  $DIST_DIR\AiFilePrefetcher\

DISTRIBUTION FILES:
  - AiFilePrefetcher.exe         (executable)
  - AiFilePrefetcher/            (folder with dependencies)
    ├── base_library.zip         (Python runtime)
    ├── torch/                   (PyTorch library ~200MB)
    ├── data/                    (pre-trained models)
    ├── config/                  (configuration files)
    └── ... (other dependencies)

TOTAL SIZE: ~300-450 MB

TO RUN STANDALONE:
  1. Copy the entire 'AiFilePrefetcher' folder to target machine
  2. Run: AiFilePrefetcher\AiFilePrefetcher.exe
  3. No Python installation required on target machine!

DEPLOYMENT OPTIONS:

  Option A - Folder Distribution:
    - Zip the entire 'AiFilePrefetcher' folder
    - Share as compressed archive
    - Users extract and run AiFilePrefetcher.exe

  Option B - Single-File EXE (optional future improvement):
    - Modify pyinstaller.spec to use --onefile option
    - Creates single .exe file (~300-350MB)
    - Slower startup but easier distribution

  Option C - Professional Installer:
    - Use NSIS or Inno Setup to create .MSI
    - Add Windows registry entries for uninstall
    - Include license agreement
    - Professional appearance for enterprise deployment

TESTING:
  Run the executable:
    .\dist\AiFilePrefetcher\AiFilePrefetcher.exe

  First run will:
    1. Create data/app_state.db
    2. Enter COLLECTION phase
    3. Gather application data

  After 10+ runs:
    1. Automatically train model
    2. Enter PRODUCTION phase
    3. Use trained model for predictions

TROUBLESHOOTING:
  - Check logs/app.log for detailed error messages
  - For missing modules, see DEPLOYMENT_GUIDE.md
  - Ensure all dependencies in requirements.txt are installed

"@ -ForegroundColor Green

Write-Success "Build completed successfully!"
Write-Info "Next steps: Test the executable and prepare for distribution"
