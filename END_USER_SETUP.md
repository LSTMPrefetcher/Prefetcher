# END USER SETUP GUIDE - AI File Prefetcher

**TLDR: Download, extract, and run. That's it. No installation required.**

---

## ✅ What Users Need (Minimum)

### System Requirements
- **Windows 7 or later** (Windows 10/11 recommended)
- **2 GB RAM** (minimum)
- **500 MB free disk space** (for the application folder)
- **Internet connection?** NO - Not needed at all

### What Users Do NOT Need
- ❌ Python installation
- ❌ Visual C++ runtimes (bundled)
- ❌ Git or any development tools
- ❌ Command-line knowledge
- ❌ Administrator access (usually - see note below)
- ❌ Internet connection
- ❌ Any special libraries or dependencies

---

## 📥 Step-by-Step for End Users

### Step 1: Get the Application (2 minutes)

**Option A: Download from File Share**
1. Download `AiFilePrefetcher.zip` from your company's file share
2. Right-click → Extract All
3. Choose destination folder (e.g., `C:\Applications\AiFilePrefetcher`)
4. Click Extract

**Option B: Download from Email/Cloud**
1. Download the ZIP file
2. Right-click → Extract All
3. Choose location
4. Click Extract

**Option C: Copy from Network Drive**
1. Network administrator copies folder to shared drive
2. User copies entire `AiFilePrefetcher` folder locally
3. Ready to use

### Step 2: Run the Application (1 click)

1. Navigate to extracted folder
2. **Double-click**: `AiFilePrefetcher.exe`
3. A console window appears with an easy menu
4. Choose option `1` to run lifecycle now

**That's it!** The application will:
- Create necessary folders (data/, logs/)
- Create database on first run
- Start collecting data
- Continue automatically

### Step 3: Use Simple CLI Commands (Optional)

You can also run explicit commands from Command Prompt/PowerShell:

```powershell
# Run one iteration (collection/training/production based on current phase)
AiFilePrefetcher.exe run

# Show lifecycle status
AiFilePrefetcher.exe status

# Health checks
AiFilePrefetcher.exe doctor

# Reset lifecycle state
AiFilePrefetcher.exe reset

# Show quick manual inside app
AiFilePrefetcher.exe guide
```

---

## 📦 Dependencies (Important)

### For EXE Users (Default)
- ✅ No Python installation needed
- ✅ No pip commands needed
- ✅ All required libraries are already bundled with the EXE folder

### For Source-Code Users (Developer Mode)
If running `app_standalone.py` directly, install dependencies once:

```powershell
python app_standalone.py setup-deps
```

---

## 📋 What Happens on First Run

```
User double-clicks: AiFilePrefetcher.exe
        ↓
Console window appears
        ↓
[Console Output]
============================================================
  FIRST RUN INITIALIZATION
============================================================
Setting up prefetcher...
This first run will initialize the application.
============================================================

[*] Collecting data for prefetcher...
[*] Running strace...
[✓] Data collection completed

Application Status Summary:
  - Name: prefetcher
  - Version: 1.0
  - Execution Count: 0
  - Lifecycle Phase: COLLECTION
  - Model Trained: No

[Progress] 0/10 collection iterations completed
Remaining: 10 more collections needed before training
        ↓
[Console closes automatically]
        ↓
Application ready for next run
```

**User sees:** Startup messages, then normal operation
**User has to do:** Absolutely nothing - app handles everything

---

## 🔄 Complete Timeline for Users

### Iteration 1
- User runs: `AiFilePrefetcher.exe`
- Console shows: "FIRST RUN INITIALIZATION"
- Wait: ~1-5 seconds
- Result: Data collected, database created

### Iterations 2-9
- User runs: `AiFilePrefetcher.exe` eight more times
- Console shows: "COLLECTION MODE - Run X/10"
- Wait: ~1-5 seconds each
- Result: More data collected

### Iteration 10
- User runs: `AiFilePrefetcher.exe`
- Console shows: "COLLECTION MODE" + data collection
- Then: "TRAINING MODE" message appears
- Wait: **30-120 seconds** (this is the training)
- Result: Model gets trained

### Iteration 11+
- User runs: `AiFilePrefetcher.exe`
- Console shows: "PRODUCTION MODE"
- Wait: ~1-5 seconds
- Result: Using trained model for predictions
- **Repeat indefinitely** - app works normally

---

## 🛑 Potential Issues & Solutions

### Issue 0: "User Account Control" Dialog (Normal & Expected) ⭐

**What User Sees:**
```
┌─────────────────────────────────────────────┐
│  User Account Control                       │
│                                             │
│  Do you want to allow this app to make      │
│  changes to your device?                    │
│                                             │
│  AiFilePrefetcher.exe                      │
│  Unknown publisher                          │
│                                             │
│  [Yes]  [No]                                │
└─────────────────────────────────────────────┘
```

**Why?** The application needs administrator privileges to:
- Monitor file system operations
- Load files into memory cache
- Optimize system performance

This is **completely normal and safe**.

**User's Solution:**
1. Click **"Yes"** to allow
2. Application starts
3. Done!

**Important Notes:**
- ✅ This is safe (code is open source)
- ✅ The app doesn't install anything
- ✅ Only happens once per session
- ✅ Standard for system utilities
- ❌ Don't click "No" - app won't work without it

---

### Issue 0.5: "Unknown Publisher" Warning

**What User Sees:**
```
"Unknown publisher" in the UAC dialog
```

**Why?** The application isn't code-signed (requires certificate)

**User's Solution:**
- Just click "Yes" anyway
- It's safe, just not commercially signed

**For IT:** If users are uncomfortable, you can:
- Code-sign the executable (costs $100-300/year)
- Or add to antivirus whitelist
- Or document as "approved application"

---

### Issue 1: "Windows protected your PC" SmartScreen Warning

**What User Sees:**
```
Windows Defender SmartScreen prevented an unrecognized app.
"AiFilePrefetcher.exe" is not recognized...
```

**Why?** The executable is unsigned. This is normal for free/open-source software.

**User's Solution:**
1. Click "More info"
2. Click "Run anyway"
3. App starts normally

**For Future Releases:** (5-10 minute fix)
- Sign .exe with code-signing certificate ($100-300/year)
- No SmartScreen warning will appear

---

### Issue 2: Permission Denied Error

**What User Sees:**
```
[ERROR] Permission denied when creating data/app_state.db
```

**Why?** User extracted to Program Files (restricted write access)

**User's Solution:**
1. Delete the folder from Program Files
2. Extract to: `C:\Users\YourUsername\AppData\Local\AiFilePrefetcher`
   - Or: `C:\Applications\AiFilePrefetcher`
   - Or: Desktop
3. Run again from new location

**Better Solution (for IT):** Pre-extract to user's home directory

---

### Issue 3: Antivirus Blocking

**What User Sees:**
```
[Antivirus alert: Threatening application detected]
```

**Why?** Over-aggressive antivirus scanning executable (false positive)

**User's Solution:**
1. Report to IT that it's safe
2. IT adds exe to antivirus whitelist
3. User runs again

**Prevention:**
- Code-sign the executable (mentioned above)
- Antivirus flags unsigned exes as potential

---

### Issue 4: Very Slow First Run

**What User Sees:**
```
First run takes 30+ seconds before anything displays
```

**Why?** PyTorch library is being extracted (~200 MB)

**User's Solution:**
- Wait for it - first run is special
- Subsequent runs start much faster

---

### Issue 5: "ModuleNotFoundError" Message

**What User Sees:**
```
[ERROR] ModuleNotFoundError: No module named 'torch'
```

**Why?** Build didn't include all dependencies properly

**User's Solution:**
- This shouldn't happen - it means developer didn't build correctly
- Have user report to developer
- Developer rebuilds with: `.\build_exe_standalone.ps1 -Clean`

---

## 📂 Folder Structure (What User Sees)

After extraction:

```
AiFilePrefetcher/
├── AiFilePrefetcher.exe          ← User double-clicks this
├── base_library.zip
├── torch/                         (PyTorch library)
├── data/
│   ├── models/                   (pre-trained models)
│   ├── processed/                (vocabularies)
│   └── [app_state.db created on first run]
├── config/
│   └── config.yaml
├── src/                          (application code)
└── ... (other files)
```

**Important for user:** 
- User only interacts with `AiFilePrefetcher.exe`
- Other files are automatically used by the application
- Can move entire folder anywhere (desktop, Downloads, network drive, etc.)
- **Don't delete files** - application needs them

---

## 💾 Data Storage (What User Needs to Know)

### Where is data stored?

**Inside the application folder:**
```
AiFilePrefetcher/
└── data/
    ├── app_state.db              ← Execution history
    ├── collection/               ← Raw data from Runs 1-10
    │   └── execution_*.sqlite    (deleted after training)
    ├── models/
    │   └── prefetch_model.pth    ← Trained model
    └── processed/
        └── vocab.json            ← File vocabulary
```

### Privacy & Data Security

✅ **All data is local** - Stays on user's computer
✅ **No internet required** - No data sent anywhere
✅ **User control** - User owns all data
✅ **Easy backup** - Copy `data/` folder to backup
✅ **Easy deletion** - Delete app = delete all data

### Backup Instructions (Optional)

If user wants to backup their collected data:
1. Navigate to: `AiFilePrefetcher/data/`
2. Copy entire `data/` folder to backup location
3. Can restore by copying back

---

## 🔧 Advanced Options (Optional for Power Users)

### Option 1: Reset Application State

User can reset the app to act like first-run again:

```powershell
AiFilePrefetcher.exe --reset
```

**Effect:**
- Clears trained model
- Returns to COLLECTION phase
- Keeps execution history for reference

**Use Case:** Testing, retraining with different parameters

### Option 2: Enable Debug Logging

User can see detailed logs:

```powershell
AiFilePrefetcher.exe --debug
```

**Effect:**
- More verbose console output
- Detailed entries in `logs/app.log`

**Use Case:** Troubleshooting issues

### Option 3: View Application Logs

User can check what the application did:

```
AiFilePrefetcher/logs/app.log
```

Open with Notepad and see all execution details

---

## ⚠️ Important Warnings for Users

### DO
✅ Keep the entire `AiFilePrefetcher` folder together
✅ Run regularly (at least once daily for best results)
✅ Check `logs/app.log` if something seems wrong
✅ Back up `data/` folder if data is important
✅ Contact IT if getting SmartScreen warnings

### DON'T
❌ Delete individual files from the folder
❌ Modify files in the `data/` folder
❌ Run from network drives (copy locally first)
❌ Run with old versions alongside new (delete old first)
❌ Assume data is backed up automatically

---

## 🆘 Troubleshooting for Users

### "App crashes immediately"
1. Check if extracted to writeable location (not Program Files)
2. Check logs/app.log for error messages
3. Try: `AiFilePrefetcher.exe --debug`
4. Report error from log to IT

### "Nothing happens when I click .exe"
1. Wait 10 seconds (first run is slow)
2. Try running again
3. Check antivirus isn't blocking it
4. Try: `AiFilePrefetcher.exe --debug`

### "Data folder gets very large"
1. This is normal after 10 runs (~50-100 MB)
2. After training at run 11, can delete `data/collection/` if needed
3. Contact IT if space is critical

### "Multiple computers - can I share?"
1. Each computer needs its own copy
2. Copy folder to each machine
3. Each will build its own database
4. No sharing between machines

### "I accidentally deleted something"
1. If deleted `data/` - can run again, will rebuild
2. If deleted `config.yaml` - restore from backup
3. If deleted application files - extract ZIP again
4. Original data might be lost - check backups

---

## 📞 Support Information Template

**Share this with your users:**

```
==============================================================
         AI FILE PREFETCHER - USER SUPPORT
==============================================================

QUICK SETUP:
1. Extract AiFilePrefetcher.zip
2. Double-click AiFilePrefetcher.exe
3. Let it run (11 times for setup)
4. Done!

NO INSTALLATION NEEDED!
No Python, no downloads, nothing else.

GETTING HELP:
1. Check logs/app.log for error details
2. Run: AiFilePrefetcher.exe --debug (for more info)
3. Contact IT with the error message

COMMON ISSUES:
- "Windows protected PC": Click "Run anyway"
- "Permission denied": Move to C:\Applications\
- "Very slow first time": Wait, first run is special

DATA SECURITY:
✓ All data stored locally on your computer
✓ No internet connection required
✓ No data sent anywhere
✓ Safe to use with sensitive files

FOR HELP:
Email: [your-support-email]
Wiki: [internal-wiki-link]
Phone: [phone-number]

==============================================================
```

---

## 🎯 Installation Summary for IT/Admin

### Pre-Installation
- [ ] Download/build AiFilePrefetcher.zip (~350 MB)
- [ ] Verify 350 MB+ size
- [ ] Test: Extract and run on test machine
- [ ] Verify console output appears

### Deployment Options

**Option A: Self-Service Download**
1. Upload to SharePoint/file share
2. Users download and extract
3. Users run from their own folder

**Option B: Pre-Installed (Recommended)**
1. Extract to: `C:\Application\AiFilePrefetcher\` (all computers)
2. Create shortcut on Desktop pointing to `.exe`
3. Users just double-click shortcut

**Option C: Network Share (Not Recommended)**
- Slower startup (network latency)
- More dependency on network
- Better: Copy to local machine first

### Post-Installation
- [ ] Test on 2-3 machines
- [ ] Verify first-run database creation
- [ ] Verify training at run 11
- [ ] Check logs/app.log for errors
- [ ] Document known issues
- [ ] Create user guide (use this document)

---

## Size Check (What Users Download)

```
Application folder: ~350 MB
  - PyTorch library: ~200 MB (largest)
  - Python runtime: ~40 MB
  - Other libraries: ~30 MB
  - Source code: <5 MB
  - Models/config: ~10 MB

After extraction:
  - Folder stays same size: ~350 MB
  - Additional data per run: ~1-10 MB (Runs 1-10 only)
  - Trained model: ~10-50 MB (created at Run 11)

Total user space needed: ~500 MB
```

---

## ✅ Success Checklist for End Users

After downloading/extracting, user should verify:

- [ ] Folder extracted to desired location
- [ ] Can see `AiFilePrefetcher.exe` in folder
- [ ] Can see subfolders: `data/`, `config/`, `torch/`, `src/`
- [ ] Can double-click `.exe` without error
- [ ] Console window appears with startup message
- [ ] Application runs without crashing
- [ ] `logs/app.log` file created
- [ ] `data/app_state.db` file created after run 1
- [ ] Ready to use!

---

## 🎓 User Training Materials

### For Individual User (5 minutes)
1. Show them where to download
2. Show them how to extract
3. Show them to double-click .exe
4. Show them logs/app.log location for troubleshooting
5. Done!

### For Group Training (15 minutes)
1. Demo extraction process
2. Demo first run (show console output)
3. Explain the 11-run setup period
4. Show where logs are
5. Show support contacts
6. Q&A

### For IT Department (30 minutes)
1. Review architecture (minimal)
2. Explain bundle contents
3. Show test deployment
4. Discuss troubleshooting
5. Escalation procedures
6. Q&A

---

## 📋 Pre-Distribution Checklist

Before sharing with users:

- [ ] Tested on Windows 10
- [ ] Tested on Windows 11
- [ ] Tested SmartScreen warning handling
- [ ] Verified extraction works
- [ ] Verified first run works
- [ ] Created user guide (this document)
- [ ] Created support contacts document
- [ ] Created IT deployment guide
- [ ] Ready for distribution!

---

## 🚀 Distribution Methods

### Method 1: Email
- [ ] Attach AiFilePrefetcher.zip to email
- [ ] Include extraction instructions
- [ ] Include getting-started guide
- [ ] Good for small groups

### Method 2: File Share
- [ ] Upload to SharePoint/OneDrive
- [ ] Share download link
- [ ] Include documentation link
- [ ] Good for medium groups

### Method 3: Network Drive
- [ ] Copy to shared network location
- [ ] Users copy to their local machine
- [ ] Create shortcut on desktop
- [ ] Good for managed networks

### Method 4: USB Drive
- [ ] Copy folder to USB
- [ ] Users copy from USB to computer
- [ ] Good for offline distribution

### Method 5: Internal App Store / Software Center
- [ ] Package as .MSI installer (advanced)
- [ ] Users auto-deploy from software center
- [ ] IT can manage updates
- [ ] Good for enterprise

---

**Bottom Line for Users:**
# Download → Extract → Run

**That's literally all they have to do.** No installs, no downloads, no configuration. Perfect for non-technical users.

---

**Last Updated:** February 16, 2026
