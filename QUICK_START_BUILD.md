# QUICK_START_BUILD.md

# Quick Start: Building the Standalone EXE

## One-Command Build (Windows PowerShell)

```powershell
# 1. Prerequisites (run once)
pip install pyinstaller torch pyyaml numpy

# 2. Build
cd d:\prefetcher\ai-file-prefetcher\ai-file-prefetcher
.\build_exe_standalone.ps1

# Output will be in: dist/AiFilePrefetcher/
```

## What Gets Created

```
dist/
└── AiFilePrefetcher/
    ├── AiFilePrefetcher.exe        ← Run this!
    ├── base_library.zip            ← Python runtime
    ├── torch/                      ← PyTorch files (200MB)
    ├── data/
    │   ├── models/                 ← Your .pth models
    │   └── processed/              ← Vocabularies
    ├── config/                     ← config.yaml
    ├── src/                        ← Application code
    └── ... (other dependencies)
```

**Total Size**: ~300-450 MB

## Testing

```powershell
# Run the executable
.\dist\AiFilePrefetcher\AiFilePrefetcher.exe

# With debugging (if needed)
.\dist\AiFilePrefetcher\AiFilePrefetcher.exe --debug

# Check logs
type logs/app.log
```

## Distribution

### Option A: Zip and Share
```powershell
Compress-Archive -Path ".\dist\AiFilePrefetcher" `
                -DestinationPath ".\AiFilePrefetcher.zip"
# Share AiFilePrefetcher.zip (300-450 MB)
```

### Option B: Network Share
```powershell
Copy-Item -Path ".\dist\AiFilePrefetcher" `
         -Destination "\\network\apps\AiFilePrefetcher" -Recurse
```

## Execution Phases (What Users See)

| Run | Phase | Duration | Status |
|-----|-------|----------|--------|
| 1 | COLLECTION | <1s | "Setting up..." |
| 2-9 | COLLECTION | 1-5s each | "Gathering data..." |
| 10 | COLLECTION | 1-5s | Last collection + triggers training |
| 11 | TRAINING | 30-120s | "Training model..." |
| 12+ | PRODUCTION | 1-5s each | "Using trained model..." |

## First-Run Flow Diagram

```
START
  ↓
Check app_state.db?
  ├─ NO  → Initialize DB (Run 1)
  │       ↓
  │       Collection Phase
  │       ↓
  │       Return to Step 2
  │
  └─ YES → Check execution_count
           ├─ < 10    → Collection Phase
           │           (runs 2-9)
           │           ↓
           │           Increment count
           │           ↓
           │           Return (data saved)
           │
           ├─ == 10   → Collection Phase (last collection)
           │           ↓
           │           Increment count to 11
           │           ↓
           │           TRIGGER TRAINING
           │           ↓
           │           Model Training Phase
           │           ↓
           │           Mark model_trained = true
           │           ↓
           │           Return
           │
           └─ > 10    → Production Phase (runs 12+)
                        ↓
                        Load trained model
                        ↓
                        Make predictions
                        ↓
                        Increment count
                        ↓
                        Return
```

## Key Files Created

| File | Purpose | Type |
|------|---------|------|
| `app_standalone.py` | Main entry point for EXE | Python |
| `src/first_run.py` | First-run detection | Python |
| `src/persistence.py` | SQLite data storage | Python |
| `src/lifecycle.py` | Phase orchestration | Python |
| `pyinstaller.spec` | Build configuration | Config |
| `build_exe_standalone.ps1` | Build automation | Script |

## Common Commands

```powershell
# Full clean rebuild
.\build_exe_standalone.ps1 -Clean

# Build with debug logging
.\build_exe_standalone.ps1 -Debug

# Reset application state (for testing)
.\dist\AiFilePrefetcher\AiFilePrefetcher.exe --reset

# View application logs
Get-Content logs/app.log -Tail 50

# Check build size
(Get-ChildItem ./dist/AiFilePrefetcher -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB

# Run from command line with debug
.\dist\AiFilePrefetcher\AiFilePrefetcher.exe --debug --app-name "prefetcher"
```

## Database Schema (For Developers)

### app_state.db (Tracking)
```sql
-- Global application state
app_state {
  id: INTEGER PRIMARY KEY
  app_name: TEXT UNIQUE
  execution_count: INTEGER        ← Increments each run
  lifecycle_phase: TEXT           ← COLLECTION|TRAINING|PRODUCTION
  model_trained: INTEGER BOOLEAN  ← 0 or 1
  last_execution: TIMESTAMP
  version: TEXT
}

-- Execution history
execution_log {
  id: INTEGER PRIMARY KEY
  execution_id: TEXT UNIQUE       ← Unique per run
  timestamp: TIMESTAMP
  phase: TEXT
  app_name: TEXT
  metadata: JSON
}
```

### execution_*.sqlite (Per-Run Data)
```sql
-- One file per execution run
file_access_trace {
  id: INTEGER PRIMARY KEY
  timestamp: REAL                 ← Epoch time
  file_path: TEXT
  operation: TEXT                 ← open|read|write|close
  process_name: TEXT
  file_size: INTEGER
  additional_data: JSON
}
```

## Customization

### Change Collection Count Threshold
Edit `src/lifecycle.py`:
```python
elif count < 10 and not state["model_trained"]:  # ← Change 10 to X
```

### Change Output EXE Name
Edit `pyinstaller.spec`:
```python
name='MyAppName'  # Instead of AiFilePrefetcher
```

### Hide Console Window (No Pop-up)
Edit `pyinstaller.spec`:
```python
console=False,  # Set to False instead of True
```

### Include Additional Data Files
Edit `pyinstaller.spec`:
```python
datas = [
    ('data/models', 'data/models'),
    ('data/processed', 'data/processed'),
    ('config/config.yaml', 'config/'),
    ('additional_file.txt', '.'),  ← Add like this
]
```

## Troubleshooting

**Build fails with "torch not found"**
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
pyinstaller --clean pyinstaller.spec --noconfirm
```

**EXE says "ModuleNotFoundError: No module named 'X'"**
1. Add to `hiddenimports` in `pyinstaller.spec`
2. Rebuild: `.\build_exe_standalone.ps1 -Clean`

**Build hangs for 5+ minutes**
- This is PyTorch bundling (100-200 MB file)
- Let it complete, don't interrupt

**Data files not included in EXE**
- Check `datas=[]` in `pyinstaller.spec`
- Verify paths are relative to project root
- Rebuild with `-Clean`

---

## Resources

- **Full Documentation**: `DEPLOYMENT_GUIDE.md`
- **User Guide**: `STANDALONE_APP_GUIDE.md`
- **Source Code**: `src/` directory
- **Logs**: `logs/app.log`

---

**Last Updated:** February 2026
