# IMPLEMENTATION_CHECKLIST.md

# Windows Standalone EXE - Implementation Checklist

Use this checklist to build and deploy your standalone Windows application.

---

## ✅ Pre-Build Checklist

### Environment Setup
- [ ] Python 3.8+ installed on development machine
- [ ] PyTorch, PyYAML, NumPy installed via requirements.txt
- [ ] PyInstaller installed (`pip install pyinstaller`)
- [ ] Windows PowerShell available (for build script)
- [ ] Administrator access (to run build script if needed)

### Project Setup
- [ ] All source files in `src/` directory
- [ ] Pre-trained models in `data/models/`
- [ ] Vocabularies in `data/processed/`
- [ ] Configuration in `config/config.yaml`
- [ ] Requirements.txt up to date

### Verify New Files Exist
- [ ] `src/persistence.py` ✅ Created
- [ ] `src/first_run.py` ✅ Created
- [ ] `src/lifecycle.py` ✅ Created
- [ ] `app_standalone.py` ✅ Created
- [ ] `pyinstaller.spec` ✅ Created
- [ ] `build_exe_standalone.ps1` ✅ Created

---

## 🔨 Build Process

### Step 1: Install PyInstaller
```powershell
# If not already installed
pip install pyinstaller

# Verify installation
pyinstaller --version
```

**Checklist:**
- [ ] PyInstaller version displayed
- [ ] No "command not found" errors

---

### Step 2: Run Build Script
```powershell
# Navigate to project root
cd d:\prefetcher\ai-file-prefetcher\ai-file-prefetcher

# Execute build
.\build_exe_standalone.ps1
```

**What the script does:**
1. Cleans previous builds
2. Verifies Python installation
3. Checks required packages
4. Runs PyInstaller
5. Verifies output

**Checklist:**
- [ ] Script runs without errors
- [ ] PyInstaller reports success
- [ ] Build completes in 2-5 minutes
- [ ] No "ModuleNotFoundError" messages

---

### Step 3: Verify Build Output
```powershell
# Check if executable created
Test-Path .\dist\AiFilePrefetcher\AiFilePrefetcher.exe

# Check folder structure
Get-ChildItem .\dist\AiFilePrefetcher\ | Select-Object Name

# Check total size
(Get-ChildItem .\dist\ -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
```

**Expected Output:**
```
True  (file exists)

data
config
torch
base_library.zip
...multiple files...

~350 MB (folder size)
```

**Checklist:**
- [ ] AiFilePrefetcher.exe exists
- [ ] At least 300 MB total size
- [ ] data/, config/, torch/ subdirectories present

---

## 🧪 Testing Phase

### Initial Test: Single Execution
```powershell
# Run the executable
.\dist\AiFilePrefetcher\AiFilePrefetcher.exe
```

**First Run Expected Output:**
```
==============================================================
  FIRST RUN INITIALIZATION
==============================================================
Setting up prefetcher...
This first run will initialize the application.
==============================================================

[*] Collecting data for prefetcher...
[collection output...]
[✓] Data collection completed

Application Status Summary:
  - Name: prefetcher
  - Version: 1.0
  - Execution Count: 0
  - Lifecycle Phase: COLLECTION
  - Model Trained: No
  - Last Execution: 2026-02-16 14:30:45

[Progress] 0/10 collection iterations completed
Remaining: 10 more collections needed before training
```

**Checklist:**
- [ ] Executable runs without crashing
- [ ] Correct startup message appears
- [ ] Data collection starts
- [ ] No error messages
- [ ] logs/app.log created
- [ ] data/app_state.db created

---

### Multiple Runs Test (Collection Phase)
```powershell
# Run 4 more times (runs 2-5)
for ($i = 1; $i -le 4; $i++) {
    .\dist\AiFilePrefetcher\AiFilePrefetcher.exe
    Write-Host "--- Run $($i+1) completed ---"
}
```

**Expected Output Pattern (Run 2):**
```
[COLLECTION MODE] Run 1/10 - Gathering user interaction data...
[*] Collecting data for prefetcher...
[collection output...]
[✓] Data collection completed

Application Status Summary:
  - Execution Count: 1
  - Lifecycle Phase: COLLECTION
  
[Progress] 1/10 collection iterations completed
Remaining: 9 more collections needed before training
```

**Checklist:**
- [ ] Each run completes successfully
- [ ] Execution count increments (0→1→2→3→4)
- [ ] Same console messages appear
- [ ] data/collection/ folder gets new .sqlite files
- [ ] logs/app.log appends entries

---

### Collection Completion Test
```powershell
# Run 6 more times to reach 10 collections
for ($i = 1; $i -le 6; $i++) {
    .\dist\AiFilePrefetcher\AiFilePrefetcher.exe
    Write-Host ""
}
```

**After Run 10, Expected Output:**
```
==============================================================
  TRAINING MODE
==============================================================
Sufficient data collected. Training model now...
This may take 30-120 seconds depending on your system.
==============================================================

epoch 1/30 - [training progress...]
epoch 2/30 - [training progress...]
...
epoch 30/30 - [training progress...]

✓ Model trained successfully in 45.23s

Application Status Summary:
  - Execution Count: 10
  - Lifecycle Phase: PRODUCTION
  - Model Trained: Yes

[Status] Model is trained and in production mode
```

**Checklist:**
- [ ] Training starts automatically at execution 10
- [ ] Training progress displayed
- [ ] Training completes successfully
- [ ] Duration: 30-120 seconds (acceptable)
- [ ] No errors during training
- [ ] model_trained flag set to true in database
- [ ] Phase transitioned to PRODUCTION

---

### Production Mode Test
```powershell
# Run in production mode (run 11+)
.\dist\AiFilePrefetcher\AiFilePrefetcher.exe
```

**Expected Output (Run 11+):**
```
[PRODUCTION MODE] Using trained model for predictions...
[*] Running prefetcher for prefetcher...
[*] Prediction: [predicted files...]
[✓] Prefetcher completed

Application Status Summary:
  - Execution Count: 11
  - Lifecycle Phase: PRODUCTION
  - Model Trained: Yes

[Status] Model is trained and in production mode
```

**Checklist:**
- [ ] Consistent "PRODUCTION MODE" message
- [ ] No training occurs
- [ ] Fast execution (1-5 seconds)
- [ ] Predictions appear in console
- [ ] Execution count continues incrementing

---

### Database Verification
```powershell
# Check database structure
# Install SQLite tool if needed: choco install sqlite or use PowerShell
# Or open in VS Code with SQLite extension

# View app_state.db content
sqlite3 data/app_state.db "SELECT * FROM app_state;"

# Expected output after run 11:
# 1|prefetcher|11|PRODUCTION|1|2026-02-16 14:35:20|1.0|{}
```

**Checklist:**
- [ ] data/app_state.db file accessible
- [ ] app_state table contains correct data
- [ ] execution_count is 11
- [ ] lifecycle_phase is "PRODUCTION"
- [ ] model_trained is 1 (true)

---

### Log File Verification
```powershell
# View recent log entries
Get-Content .\logs\app.log -Tail 30

# Expected content:
# 2026-02-16 14:30:45 - src.first_run - INFO - Initialized app state...
# 2026-02-16 14:30:46 - src.lifecycle - INFO - Starting COLLECTION phase...
# ... (more entries)
```

**Checklist:**
- [ ] logs/app.log file created
- [ ] Contains INFO level messages
- [ ] Contains timestamp for each event
- [ ] No ERROR messages (if test passed)

---

## 📦 Distribution Preparation

### Option A: ZIP Distribution
```powershell
# Create zip file for distribution
Compress-Archive -Path ".\dist\AiFilePrefetcher" `
                 -DestinationPath ".\AiFilePrefetcher.zip"

# Verify zip file
Test-Path .\AiFilePrefetcher.zip
Get-Item .\AiFilePrefetcher.zip | Select-Object Length
```

**Checklist:**
- [ ] ZIP file created successfully
- [ ] Size: ~350 MB
- [ ] Contains AiFilePrefetcher/ folder
- [ ] Can extract without errors

---

### Option B: Network Share
```powershell
# Copy to network share
Copy-Item -Path ".\dist\AiFilePrefetcher" `
         -Destination "\\network\share\apps\" -Recurse -Force

# Verify copy
Test-Path "\\network\share\apps\AiFilePrefetcher\AiFilePrefetcher.exe"
```

**Checklist:**
- [ ] Files copied to network location
- [ ] All subdirectories present
- [ ] Executable file accessible

---

### Option C: Cloud Upload
If using cloud storage (OneDrive, Google Drive, Dropbox):

**Checklist:**
- [ ] dist/AiFilePrefetcher folder uploaded
- [ ] All files present after upload
- [ ] Shareable link created
- [ ] Shared with intended users

---

## 🚀 User Deployment Testing

### Test 1: Fresh User (First-Time Use)
Have a test user:
1. Download the zip OR get the folder from network share
2. Extract to a folder (e.g., C:\Apps\AiFilePrefetcher)
3. Run AiFilePrefetcher.exe
4. Verify startup message and data collection

**Checklist:**
- [ ] User can download/extract without issues
- [ ] Executable runs on first attempt
- [ ] Creates data/ and logs/ directories
- [ ] Passes first-run initialization

---

### Test 2: Multiple Users (Same Machine)
Test with two different Windows user accounts:

**Checklist:**
- [ ] Each user has own data/app_state.db
- [ ] Execution counts are independent
- [ ] No data mixing between users
- [ ] Both can run simultaneously without conflicts

---

### Test 3: Various Windows Versions
If possible, test on:
- [ ] Windows 10
- [ ] Windows 11
- [ ] Older Windows versions (if applicable)

**Checklist:**
- [ ] Executable runs on target Windows versions
- [ ] No dependency errors
- [ ] Performance acceptable

---

## ✨ Final Quality Checks

### Code Quality
- [ ] No hardcoded paths in app_standalone.py
- [ ] All imports work correctly
- [ ] Error handling is robust
- [ ] Logging is comprehensive

### Performance
- [ ] First run: < 10 seconds
- [ ] Collection runs: 1-5 seconds each
- [ ] Training: 30-120 seconds (acceptable)
- [ ] Production runs: 1-5 seconds each

### Documentation
- [ ] DEPLOYMENT_GUIDE.md is complete
- [ ] STANDALONE_APP_GUIDE.md is clear
- [ ] QUICK_START_BUILD.md is accurate
- [ ] README.md links to docs

### Security
- [ ] No credential leaks in code
- [ ] No external network calls (without user consent)
- [ ] Data stays local
- [ ] No telemetry without notification

---

## 🎯 Final Checklist (Before Release)

- [ ] All tests passed ✅
- [ ] No error messages in logs ✅
- [ ] Database schema correct ✅
- [ ] Model training successful ✅
- [ ] Production inference working ✅
- [ ] Documentation complete ✅
- [ ] Distribution package created ✅
- [ ] File permissions correct ✅
- [ ] Tested on target systems ✅
- [ ] README updated ✅
- [ ] Version number set ✅

---

## 📋 Build & Release Notes Template

```markdown
# AI File Prefetcher v1.0 - Release Notes

## What's New
- ✅ Standalone Windows executable (no Python required)
- ✅ Automatic data collection (first 10 runs)
- ✅ Automatic model training (run 11)
- ✅ Automatic predictions (runs 12+)
- ✅ Local data storage (no cloud upload)

## System Requirements
- Windows 7 or later (10/11 recommended)
- 2GB RAM minimum
- 500MB disk space
- No Python installation required

## Installation
1. Download AiFilePrefetcher.zip
2. Extract to desired location
3. Run AiFilePrefetcher.exe

## First Run
- Runs 1-10: Data collection (5-60 seconds total)
- Run 11: Model training (30-120 seconds)
- Runs 12+: Production mode (normal operation)

## Known Limitations
- Training time depends on CPU speed
- Works best with 10+ application executions

## Support
- Check logs/app.log for errors
- See STANDALONE_APP_GUIDE.md for troubleshooting
```

---

## Next Steps After Successful Build

1. **Document Customization**
   - Note any configuration changes
   - Update config.yaml version in build

2. **Create Installer** (Optional)
   - Use NSIS or Inno Setup for professional installer
   - Add uninstall capability
   - Register file associations if needed

3. **Code Signing** (Optional for Enterprise)
   - Sign executable with code signing certificate
   - Prevents SmartScreen warnings
   - Cost: ~$100-300/year

4. **Update Distribution Website/Portal**
   - Upload release notes
   - Provide download link
   - Document system requirements
   - Include troubleshooting tips

5. **User Communication**
   - Send out release announcement
   - Include installation instructions
   - Provide support contact info
   - Share documentation links

---

**Build Date:** _______________

**Tester:** _______________

**Notes:**

```
_________________________________________
_________________________________________
_________________________________________
```

**Sign-off:** _______________  Date: _______________

---

**Last Updated:** February 16, 2026
