# IT / Enterprise Deployment Guide

For IT Administrators and Network Managers deploying to multiple systems.

---

## 🔐 Administrator Privilege Requirements

### Why Admin is Needed

The application requires elevated privileges for legitimate system operations:

| Operation | Privilege Level | Purpose |
|-----------|-----------------|---------|
| **Data Collection** | Admin | Monitor file system I/O operations |
| **File Prefetching** | Admin | Load files into memory cache |
| **Cache Management** | Admin | Manage system page cache |

### Which Privilege Level?

✅ **User-level Admin** (Standard user with UAC elevation)
- Sufficient for all operations
- What we recommend
- Safest approach

❌ **System-level Admin** (Not needed)
- More access than required
- Security risk
- Don't use

❌ **Domain Admin** (Not needed)
- Dangerous
- Creates audit trail
- Don't use

---

## 🪟 Windows Account & Permission Setup

### Standard User Account (Recommended)

For normal users:

```
User Account: Standard User
Admin Status: NO

How to run the app:
1. Double-click AiFilePrefetcher.exe
2. UAC dialog appears
3. User clicks "Yes"
4. App gains temporary elevation
5. App completes
6. Privileges drop back to user level
```

**Advantages:**
- ✅ Standard security practice
- ✅ Least privilege principle
- ✅ Safe for enterprise
- ✅ Full audit trail in Windows Event Viewer

### Power User Account (Alternative)

For power users / tech staff:

```
User Account: Power User (or local Admin)
Admin Status: YES

How to run the app:
1. Double-click AiFilePrefetcher.exe
2. No UAC dialog (user is already admin)
3. App runs immediately
```

**Advantages:**
- ✅ Faster (no UAC dialog)
- ✅ For trusted users
- ⚠️ Less secure

**Disadvantages:**
- ❌ Should only be for IT staff
- ❌ Higher risk

### Service Account (Not Recommended)

**Do NOT use:**
- NETWORK SERVICE
- LOCAL SYSTEM
- SYSTEM
- Anonymous

These are dangerous and unnecessary.

---

## 🔧 Deployment Methods

### Method 1: Self-Service (Users Download)

**Process:**
1. Upload ZIP to SharePoint/OneDrive
2. Users download and extract
3. Users run `.exe`
4. UAC appears, users click "Yes"

**Pros:**
- Simple for IT
- Self-service for users

**Cons:**
- Users may extract to wrong location
- Slower adoption

**Step-by-step for IT:**
```
1. Upload AiFilePrefetcher.zip to shared location
2. Send email to users with:
   - Download link
   - Extract instructions (right-click → Extract All)
   - Run location recommendation
   - "It's safe, click Yes on the UAC dialog" message
3. Done - users handle themselves
```

---

### Method 2: Pre-Installation (Recommended for Managed Networks)

**Process:**
1. IT extract on all machines
2. Create Desktop shortcut
3. Users just double-click shortcut
4. UAC appears, users click "Yes"

**Pros:**
- Users can't mess up folder location
- Faster deployment
- Simpler for users

**Cons:**
- Requires IT to deploy to each machine
- Scripting needed for scale

**Step-by-step for IT:**
```powershell
# 1. Define target location (example: C:\Applications\)
$targetPath = "C:\Applications\AiFilePrefetcher"

# 2. Ensure directory exists
New-Item -ItemType Directory -Path $targetPath -Force

# 3. Extract application
Expand-Archive -Path "AiFilePrefetcher.zip" `
               -DestinationPath $targetPath `
               -Force

# 4. Create Desktop shortcut for all users
$desktopPath = "$env:PUBLIC\Desktop"
$shortcutPath = "$desktopPath\AiFilePrefetcher.lnk"
$exePath = "$targetPath\AiFilePrefetcher\AiFilePrefetcher.exe"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exePath
$shortcut.Description = "AI File Prefetcher"
$shortcut.Save()

Write-Host "Deployed to: $targetPath"
Write-Host "Shortcut created on all users' desktops"
```

**Run on each machine via:**
- Group Policy Startup Scripts
- SCCM/Intune
- RDP/Batch deployment
- PowerShell Remoting

---

### Method 3: SCCM/Intune Deployment (Enterprise)

**Prerequisites:**
- SCCM or Intune configured
- Admin rights for package creation

**Steps:**
1. Create SCCM Application
2. Set executable path to `.exe`
3. Set "Run with administrative privileges" = YES
4. Deploy to device or user collection
5. System auto-installs on target machines

**SCCM Configuration:**

```
Name: AI File Prefetcher
Version: 1.0
Publisher: Your Organization

Installation Program:
  Command Line: AiFilePrefetcher.exe
  
Installation Behavior:
  ☑ Run with Administrative Privileges
  
Uninstall Program:
  Command Line: rmdir /s /q "C:\Applications\AiFilePrefetcher"
```

---

### Method 4: Group Policy (Alternative for Domain-Joined)

**Using Group Policy to auto-elevate:**

```
Group Policy Editor (gpedit.msc)
  → Computer Configuration
    → Windows Settings
      → Security Settings
        → Local Policies
          → User Rights Assignment
            → "Deny log on as a service"
              Add user/group to exclude from denial
```

**Not recommended - instead use Method 2 or 3**

---

## 🛡️ Security Considerations

### Application Security Profile

**Code Review:**
- ✅ Open source (reviewable)
- ✅ No network communication
- ✅ No persistence (doesn't stay installed)
- ✅ Local data only
- ✅ Easy to uninstall
- ✅ No registry modifications
- ✅ No system services installed

**Audit Trail:**
- ✅ User Account Audit logs
- ✅ Application creates logs/app.log
- ✅ Data stored in local folder (queryable)

**Attack Surface:**
- ✅ Minimal (single .exe + data folder)
- ✅ No background services
- ✅ No privilege escalation
- ✅ No persistence mechanisms

### Antivirus Whitelisting

**Recommended:** Add `.exe` to antivirus whitelist

**Process (varies by AV product):**

**Windows Defender:**
```powershell
Add-MpPreference -ExclusionPath "C:\Applications\AiFilePrefetcher"
```

**Third-party AV (example: McAfee):**
```
ePO Console
  → Computers
    → [Select computer]
      → Policies
        → Exclusions
          → Add: C:\Applications\AiFilePrefetcher\AiFilePrefetcher.exe
```

**Generally:**
1. Open AV console
2. Find "Exclusions" or "Whitelist"
3. Add path to AiFilePrefetcher.exe
4. Push policy to all machines

---

## 📊 Deployment Scenarios

### Scenario 1: Small Office (5-20 Users)

**Recommended Method:** Self-Service (Method 1)

```
1. Upload ZIP to shared drive
2. Send email with instructions
3. Users download/extract/run
4. Support via email if questions
```

**Time: 1 hour setup + 2 hours first-round support**

---

### Scenario 2: Medium Enterprise (20-500 Users)

**Recommended Method:** Pre-Installation (Method 2)

```
1. Test on 5-10 pilot users
2. Create deployment script
3. Deploy to departments progressively
4. IT support team handles issues
5. Monitor logs/deployment success
```

**Time: 1 day implementation + 1 week rollout**

---

### Scenario 3: Large Enterprise (500+ Users)

**Recommended Method:** SCCM/Intune (Method 3)

```
1. Create SCCM application package
2. Set auto-elevation = YES
3. Deploy to device collection
4. System automatically deploys
5. Helpdesk escalation for issues
```

**Time: 2 days preparation + auto-deployment**

---

### Scenario 4: Non-Domain (Standalone Machines)

**Recommended Method:** Self-Service or USB (Method 1)

```
1. Distribute via USB or downloads
2. Users extract and run
3. UAC handles elevation
4. Each machine independent
```

**Time: 30 minutes per machine + user execution**

---

## 🔍 Monitoring & Troubleshooting

### Check Deployment Success

```powershell
# Check if folder exists
Test-Path "C:\Applications\AiFilePrefetcher\AiFilePrefetcher.exe"

# Check recent execution
Get-ChildItem "C:\Applications\AiFilePrefetcher\logs\" | 
  Sort-Object LastWriteTime -Descending | 
  Select-Object -First 1

# Check data folder
Get-ChildItem "C:\Applications\AiFilePrefetcher\data\" | 
  Measure-Object -Property Length -Sum
```

### User Support Escalation

**Tier 1 (Helpdesk):**
- UAC dialog? → Click Yes
- SmartScreen warning? → Click "More info" → "Run anyway"
- Permission denied? → Ensure extracted to user home folder
- General issues? → Check logs/app.log

**Tier 2 (IT):**
- Antivirus blocking? → Whitelist in AV console
- Network issues? → Not applicable (offline app)
- File system issues? → Check disk space and permissions
- Escalate app bugs to developer

**Tier 3 (Developer Support):**
- Complex errors or bugs
- Performance issues
- Feature requests

---

## 📋 Pre-Deployment Checklist

- [ ] Application tested on Windows 10
- [ ] Application tested on Windows 11
- [ ] UAC dialog verified
- [ ] Admin elevation works
- [ ] File creation verified (logs/, data/)
- [ ] Database creation verified
- [ ] No known issues in current version
- [ ] Antivirus whitelisting configured
- [ ] User documentation prepared
- [ ] IT support team trained
- [ ] Deployment method chosen
- [ ] Rollback plan documented
- [ ] Ready for production deployment

---

## 📄 Sample IT Communication

**For IT Staff:**

```
═════════════════════════════════════════════════════════════════
         AI FILE PREFETCHER - IT DEPLOYMENT INFORMATION
═════════════════════════════════════════════════════════════════

WHAT IT IS:
AI File Prefetcher is a standalone Windows application that monitors
and optimizes file prefetching for faster application startup.

REQUIREMENTS:
- Windows 7 or later (10/11 recommended)
- 2 GB RAM
- 500 MB disk space
- Administrator privileges (automatic, via UAC elevation)

ADMIN ACCESS:
The application requires temporary admin elevation via UAC.
Standard users will see "Do you want to allow this app..." dialog.
- Safe: Application is open-source and non-persistent
- Normal: Standard Windows behavior for system utilities
- Whitelisting recommended but not required

DEPLOYMENT:
Choose from:
1. Self-service (users download and extract)
2. Pre-installation (IT deploys to all machines)
3. SCCM/Intune (auto-deployment on enterprise)

DEFAULT LOCATION:
C:\Applications\AiFilePrefetcher

ANTIVIRUS:
- Whitelist: C:\Applications\AiFilePrefetcher\AiFilePrefetcher.exe
- May require IT approval on first run
- No network communication (safe)

SUPPORT:
- Check logs: C:\Applications\AiFilePrefetcher\logs\app.log
- User guide: [contact admin for guide link]
- For bugs: [contact developer]

SECURITY:
✓ No network communication
✓ No persistence (easy to remove)
✓ Local data only
✓ No system modifications
✓ Full audit trail available

═════════════════════════════════════════════════════════════════
```

**For End Users:**

```
═════════════════════════════════════════════════════════════════
         WHEN YOU RUN AI FILE PREFETCHER
═════════════════════════════════════════════════════════════════

YOU WILL SEE: "User Account Control" Dialog

DO THIS: Click "Yes"

WHY: The application needs temporary admin privileges to work
     properly. This is normal for system utilities.

IS IT SAFE: YES - The application is open-source and only runs
            locally. No installation, no persistence.

═════════════════════════════════════════════════════════════════
```

---

## 🔄 Troubleshooting Matrix

| Issue | Cause | Solution |
|-------|-------|----------|
| UAC dialog keeps appearing | Normal behavior | One-time per session, expected |
| "Access Denied" error | Missing admin | Right-click → Run as administrator |
| SmartScreen warning | Unsigned .exe | Click "More info" → "Run anyway" |
| Antivirus quarantine | HIPS/heuristics | Whitelist in AV console |
| "Can't create data/app_state.db" | Wrong folder | Move to user home, not Program Files |
| Very slow startup on first run | PyTorch extraction | Wait 30-60 seconds, normal first-run |

---

## 📈 Recommended Rollout Timeline

```
Week 1: Pilot Testing
  Mon-Tue: Test on 5-10 machines
  Wed: Resolve any issues
  Thu: IT approval for rollout
  Fri: Review & prepare for wider deployment

Week 2: Phase 1 Rollout
  Mon-Wed: Deploy to Department A (50 users)
  Thu-Fri: Monitor, handle support tickets

Week 3: Phase 2 Rollout
  Mon-Wed: Deploy to Department B (50 users)
  Thu-Fri: Monitor, handle support

Week 4: Full Rollout
  Mon-Tue: Deploy to remaining departments
  Wed-Fri: Handle support, finalize
```

---

## 🎯 Success Metrics

Track these metrics post-deployment:

- % of users with successful deployment
- # of support tickets (aim: <5% of users)
- Average time to first successful run
- User satisfaction (optional survey)
- Data collection success rate (>95%)
- Model training success rate (>90%)

---

## 📞 Support Contacts

Create a support structure:

```
TIER 1 - Desktop Support (Helpdesk)
  Email: helpdesk@company.com
  Phone: ext. 1234
  Hours: 8AM-5PM weekdays
  
TIER 2 - Systems Administrator
  Email: sysadmin@company.com
  Hours: 9AM-5PM weekdays
  
TIER 3 - Application Developer
  Email: [developer contact]
  Hours: As needed for escalations
```

---

**Last Updated:** February 16, 2026

**Status:** Ready for Enterprise Deployment
