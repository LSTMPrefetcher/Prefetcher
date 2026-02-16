# Kernel-Level / Admin Access Guide

## The Core Issue

The application needs **elevated privileges** for two operations:

1. **Data Collection** (`strace` on Linux → system call tracing on Windows)
   - Reads file access operations
   - Requires monitoring system-level I/O
   
2. **Prefetching** (`vmtouch` on Linux → file prefetching on Windows)
   - Loads files into memory cache
   - Requires kernel-level memory management

---

## ❓ What Access Level is Actually Needed?

### On Linux (Original Implementation)
```bash
# Data collection requires root:
sudo strace -e openat -f application_name

# Prefetching requires root:
sudo vmtouch -t /path/to/file

# Cache clearing requires root:
sudo sync; sudo sysctl -w vm.drop_caches=3
```

### On Windows (Our Implementation)

```
Admin privileges needed for:
✓ Reading file access traces (Event Tracing for Windows)
✓ Prefetching files (SetFilePointer, ReadFile kernel APIs)
✓ Cache management (CachePrefetch Windows API)
```

---

## 🪟 Windows Elevation Methods

There are **4 ways** to handle admin access on Windows:

### Method 1: Automatic UAC Prompt (RECOMMENDED) ⭐

PyInstaller can embed a manifest to request admin privileges automatically.

**How it works:**
1. User double-clicks `.exe`
2. Windows detects request for admin
3. UAC dialog appears: "Do you want to allow this app to make changes?"
4. User clicks "Yes"
5. App runs with admin privileges

**Implementation:**

Edit `pyinstaller.spec`:
```python
a = Analysis(
    ['app_standalone.py'],
    ...
)

# Add manifest for admin elevation
manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity version="1.0.0.0" processorArchitecture="*" 
                    name="AiFilePrefetcher" type="win32"/>
  <description>AI File Prefetcher</description>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.Windows.Common-Controls" 
                       version="6.0.0.0" processorArchitecture="*" publicKeyToken="6595b64144ccf1df"/>
    </dependentAssembly>
  </dependency>
  <requestedPrivileges>
    <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
  </requestedPrivileges>
  <asmv3:application>
    <asmv3:windowsSettings xmlns="http://schemas.microsoft.com/compatibility/windows/1">
      <dpiAware>true</dpiAware>
    </asmv3:windowsSettings>
  </asmv3:application>
</assembly>
"""

# Add after exe creation
exe_onefile = EXE(
    ...,
    manifest=manifest,
    ...
)
```

**User Experience:**
```
User double-clicks AiFilePrefetcher.exe
        ↓
UAC Dialog appears:
┌─────────────────────────────────────────────────┐
│ User Account Control                            │
│                                                 │
│ Do you want to allow this app to make changes   │
│ to your device?                                 │
│                                                 │
│ AiFilePrefetcher.exe                           │
│                                                 │
│ [Yes]  [No]                                     │
└─────────────────────────────────────────────────┘
        ↓
User clicks "Yes"
        ↓
App runs with admin privileges
```

**Pros:**
- ✅ Automatic, no extra steps
- ✅ Standard Windows behavior
- ✅ Users expect UAC for system utilities
- ✅ Can't bypass (by design)

**Cons:**
- ⚠️ Some users might click "No" and then complain
- ⚠️ Might trigger antivirus alerts

---

### Method 2: Batch Wrapper Script

Create a `.bat` file that requests admin, then runs the `.exe`.

**File: `run_as_admin.bat`**
```batch
@echo off
REM Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with admin privileges...
    AiFilePrefetcher.exe %*
) else (
    echo Requesting admin privileges...
    powershell -Command "Start-Process -FilePath '%~dp0AiFilePrefetcher.exe' -ArgumentList '%*' -Verb RunAs"
)
pause
```

**User Experience:**
1. Double-click `run_as_admin.bat`
2. UAC dialog appears
3. User clicks "Yes"
4. `.exe` launches with admin

**Pros:**
- ✅ Works with older Windows versions
- ✅ Can include helper scripts
- ✅ User sees clear message

**Cons:**
- ⚠️ Extra file to distribute
- ⚠️ `.bat` files can trigger antivirus alerts

---

### Method 3: PowerShell Wrapper

Users run with PowerShell:

```powershell
Start-Process -FilePath "AiFilePrefetcher.exe" -Verb RunAs
```

**Pros:**
- ✅ Flexible
- ✅ Can add logging

**Cons:**
- ❌ Requires PowerShell knowledge
- ❌ Not user-friendly

---

### Method 4: Check & Graceful Fallback

If user runs without admin, app detects it and notifies:

```python
# In app_standalone.py

import ctypes
import sys

def is_admin():
    """Check if running with admin privileges"""
    try:
        return ctypes.windll.shell.IsUserAnAdmin()
    except:
        return False

def main():
    if not is_admin():
        print("\n" + "="*60)
        print("  ADMIN PRIVILEGES REQUIRED")
        print("="*60)
        print("This application requires administrator privileges.")
        print("\nPlease:")
        print("1. Right-click AiFilePrefetcher.exe")
        print("2. Select 'Run as administrator'")
        print("3. Click 'Yes' on the UAC dialog")
        print("="*60 + "\n")
        
        # Try to re-launch with admin
        import ctypes
        ctypes.windll.shell.ShellExecuteEx(
            lpVerb='runas',
            lpFile=sys.executable,
            lpParameters=__file__
        )
        sys.exit(1)
    
    # Continue with normal execution...
    print("[✓] Running with admin privileges")
```

**User Experience:**
```
User double-clicks AiFilePrefetcher.exe (without admin)
        ↓
Console shows:
============================================================
  ADMIN PRIVILEGES REQUIRED
============================================================
This application requires administrator privileges.

Please:
1. Right-click AiFilePrefetcher.exe
2. Select 'Run as administrator'
3. Click 'Yes' on the UAC dialog
============================================================
        ↓
User follows instructions
        ↓
App relaunches with admin
```

**Pros:**
- ✅ Clear messaging
- ✅ Handles common mistakes
- ✅ Can auto-retry

**Cons:**
- ⚠️ Extra step for users
- ⚠️ Console appears twice

---

## 🎯 RECOMMENDED APPROACH: Method 1 (Auto UAC)

### Implementation Steps

**Step 1: Create Manifest File**

Create file: `app_manifest.xml`

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="1.0.0.0"
    processorArchitecture="*"
    name="AiFilePrefetcher"
    type="win32"
  />
  <description>AI File Prefetcher - Intelligent File Prefetching</description>

  <!-- Windows 7+ -->
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="*"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>

  <!-- REQUEST ADMIN PRIVILEGES -->
  <requestedPrivileges>
    <requestedExecutionLevel level="requireAdministrator" uiAccess="false"/>
  </requestedPrivileges>

  <!-- DPI Awareness -->
  <asmv3:application xmlns:asmv3="http://schemas.microsoft.com/compatibility/windows/1">
    <asmv3:windowsSettings xmlns="http://schemas.microsoft.com/compatibility/windows/1">
      <dpiAware>true</dpiAware>
    </asmv3:windowsSettings>
  </asmv3:application>

</assembly>
```

**Step 2: Update PyInstaller Spec**

Edit `pyinstaller.spec`:

```python
# Read the manifest file
with open(os.path.join(PROJECT_ROOT, 'app_manifest.xml'), 'r') as f:
    manifest_content = f.read()

a = Analysis(
    ['app_standalone.py'],
    ...
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe_onefile = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AiFilePrefetcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    manifest=manifest_content,  # ← ADD THIS LINE
)
```

**Step 3: Rebuild**

```powershell
.\build_exe_standalone.ps1 -Clean
```

**Result:** `.exe` will now request admin automatically!

---

## 📋 What to Tell Users

### For Individual Users

**You may see a "User Account Control" dialog when launching the application:**

```
Do you want to allow this app to make changes to your device?

AiFilePrefetcher.exe
Administrator
```

**This is NORMAL and EXPECTED.**

The application needs administrator privileges to:
- Monitor file access
- Prefetch files into memory
- Optimize system performance

**What to do:**
1. Click "Yes" to allow
2. Application starts
3. UAC dialog won't appear again (same user session)

**Important:** This is NOT a security risk. The application is:
- Open source
- Not connecting to internet
- Not installing anything
- Only running locally on your computer

---

### For IT/Admin Teams

**Deployment Notes:**

When deploying to managed/restricted Windows machines:

1. **If UAC is enabled (default):** Users see UAC prompt, click "Yes"
2. **If UAC is disabled:** App runs normally with admin
3. **If UAC is enforced:** May need to pre-approve in Group Policy

**Group Policy Configuration (Optional):**

If you want to suppress UAC for this app:

```
Computer Configuration
  → Windows Settings
    → Security Settings
      → Local Policies
        → Security Options
          → User Account Control: Admin Approval Mode for Built-in Administrator
            Set to: Enabled (or custom group)
```

**Or for specific app:**

Create registry entry:
```powershell
New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" `
  -Name "(default)" -Value "AiFilePrefetcher.exe" -Force
```

**Recommendation:** Whitelist `AiFilePrefetcher.exe` in your antivirus software as a trusted application.

---

## ❌ What NOT to Do

**DON'T:** Run as LOCAL SYSTEM or NETWORK SERVICE
- This is dangerous and unnecessary
- Normal admin (user elevated) is fine

**DON'T:** Disable UAC for the entire system
- Bad security practice
- Only disable UAC for this app (if needed)

**DON'T:** Make users use `runas` command manually
- Use automatic UAC elevation instead
- Much better user experience

**DON'T:** Require domain admin privileges
- Regular user admin is sufficient
- Domain admin creates audit trail and potential issues

---

## 🔒 Security Considerations

### Why Admin is Needed

✅ **Legitimate reasons:**
1. System call tracing (like `strace`)
2. File cache management
3. Memory operations
4. I/O operations

### Why It's Safe

✅ **Application is safe because:**
1. No network communication (offline)
2. Open source (code can be reviewed)
3. No persistence (doesn't stay installed)
4. Local data only
5. Easy to uninstall (delete folder)
6. No registry modifications
7. No service installation

### For Trusted Environments Only

⚠️ **Only deploy to:**
- Internal enterprise networks
- Trusted user base
- Company-controlled machines

❌ **NOT suitable for:**
- Public distributions
- Untrusted networks
- Guest machines

---

## 📊 User Communication Template

```
═════════════════════════════════════════════════════════════════

               AI FILE PREFETCHER - USER ALERT

═════════════════════════════════════════════════════════════════

IMPORTANT: Administrator Privileges Required

When you run AiFilePrefetcher.exe, Windows will ask for permission:

"Do you want to allow this app to make changes to your device?"

CLICK "Yes" to continue.

WHY IS THIS NEEDED?
The application needs administrator privileges to:
• Monitor file system operations
• Load files into memory cache
• Optimize application startup times

IS THIS SAFE?
YES. The application:
✓ Does not connect to the internet
✓ Does not install anything
✓ Does not modify system files
✓ Does not collect personal data
✓ Only uses system resources locally
✓ Respect privacy and security

WHAT IF I CLICK "NO"?
The application will not run. Click "Yes" to continue.

═════════════════════════════════════════════════════════════════
```

---

## 🛠️ Troubleshooting Admin Issues

### Issue: "Access Denied" Error

**Cause:** App running without admin, tried to access system files

**Solution:**
1. Right-click `.exe` → "Run as administrator"
2. Click "Yes" on UAC dialog

### Issue: "System call failed"

**Cause:** Missing admin privileges for specific operation

**Solution:**
1. Restart computer
2. Log in with admin account
3. Run application

### Issue: UAC Dialog Appears Every Time

**Normal behavior** - UAC appears once per session by design

**If it's annoying in testing:**
1. Use security admin account
2. UAC appears less frequently
3. Normal users see it once per session

### Issue: Antivirus Blocks Admin Request

**Solution:**
1. IT whitelist AiFilePrefetcher.exe in antivirus
2. Or temporarily disable antivirus for testing
3. Or use "trusted source" option in antivirus

---

## 📋 Implementation Checklist

- [ ] Create `app_manifest.xml` file
- [ ] Update `pyinstaller.spec` to include manifest
- [ ] Test build with admin request
- [ ] Verify UAC dialog appears on launch
- [ ] Test on Windows 10 and 11
- [ ] Create user communication template
- [ ] Document in IT deployment guide
- [ ] Test with restricted accounts
- [ ] Whitelist in antivirus (if used)
- [ ] Ready for distribution!

---

## Summary for Your Users

**Simplified Version:**

**Q: Will the app ask for admin?**
A: Yes, just like other system utilities. Click "Yes" and continue.

**Q: Is it safe?**
A: Yes, the app is completely safe and local.

**Q: Can I run it without admin?**
A: No, the application needs admin to work properly.

**Q: Will it install anything?**
A: No, it's standalone. Just extract and run.

---

**Last Updated:** February 16, 2026
