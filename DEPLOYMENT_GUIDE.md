# AI File Prefetcher - Windows EXE Deployment Guide

## 1. PACKAGING TOOL RECOMMENDATION: **PyInstaller**

### Comparison Analysis

| Feature | PyInstaller | cx_Freeze | Nuitka |
|---------|-------------|-----------|--------|
| **Windows Support** | ✅ Excellent | ✅ Good | ✅ Good |
| **PyTorch Support** | ✅ Excellent | ⚠️ Requires manual hooks | ⚠️ Complex setup |
| **Bundle Size** | ~250-400MB | ~200-350MB | ~150-250MB |
| **Build Speed** | ✅ Fast (30-60s) | ⚠️ Slow (2-5min) | ❌ Slow (5-15min) |
| **Hidden Dependencies** | ✅ Auto-detection good | ⚠️ Manual config needed | ⚠️ Manual config needed |
| **PyYAML Support** | ✅ Built-in | ⚠️ Needs hooks | ⚠️ Needs hooks |
| **One-File EXE** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Code Obfuscation** | ⚠️ No (use pyarmor) | ⚠️ No | ✅ Compiles to binary |
| **First-Run Logic** | ✅ Easy to implement | ✅ Easy | ✅ Easy |
| **Learning Curve** | ✅ Easy | ⚠️ Medium | ❌ Steep |

### **Recommendation: PyInstaller**

#### Why PyInstaller?
1. **PyTorch Native Support**: PyInstaller has excellent PyTorch support with pre-built hooks
2. **Easy Configuration**: Simple spec file for complex projects
3. **Fast Build Times**: 30-60 seconds vs 5-15 minutes for Nuitka
4. **Mature Ecosystem**: Extensive documentation and StackOverflow support
5. **Hidden Imports**: Auto-detects most dynamic imports (important for your data loading)
6. **Windows-Optimized**: Official Windows support with no compatibility issues

#### Trade-offs:
- Bundle size is ~250-400MB (acceptable for enterprise distribution)
- Not compiled to binary (source discoverable with effort)
  - **Solution**: Use PyArmor ($49/license) if needed or accept as development trade-off

---

## 2. PROJECT STRUCTURE (RECOMMENDED)

```
ai-file-prefetcher/
├── src/
│   ├── __init__.py
│   ├── collector.py           (unchanged)
│   ├── preprocessor.py        (unchanged)
│   ├── trainer.py             (unchanged)
│   ├── prefetcher.py          (unchanged)
│   ├── evaluator.py           (unchanged)
│   ├── model.py               (unchanged)
│   ├── utils.py               (modify for standalone)
│   ├── lifecycle.py           ⭐ NEW - Application state management
│   ├── persistence.py         ⭐ NEW - SQLite data storage
│   └── first_run.py           ⭐ NEW - First-run initialization
├── config/
│   └── config.yaml            (unchanged)
├── data/
│   ├── app_state.db           ⭐ NEW - SQLite (first-run flags, execution count)
│   ├── collection/            ⭐ NEW - Raw execution data during collection phase
│   │   └── execution_*.sqlite
│   ├── models/
│   │   ├── chrome_model.pth
│   │   ├── gimp_model.pth
│   │   └── prefetch_model.pth
│   ├── processed/
│   │   ├── chrome_vocab.json
│   │   ├── gimp_vocab.json
│   │   └── vocab.json
│   └── raw/
│       ├── access_log.txt
│       └── ...
├── build/                     ⭐ NEW - PyInstaller build output
│   └── ai-file-prefetcher/
├── dist/                      ⭐ NEW - Final executable
│   └── AiFilePrefetcher.exe
├── main.py                    (modify for lifecycle management)
├── app_standalone.py          ⭐ NEW - Standalone entry point
├── requirements.txt           (unchanged)
├── pyinstaller.spec          ⭐ NEW - PyInstaller configuration
├── build_exe.ps1             (update for PyInstaller)
├── build_exe_standalone.ps1  ⭐ NEW - Final build script
└── DEPLOYMENT_GUIDE.md       (this file)
```

---

## 3. DLL & DEPENDENCY BUNDLING

### What Gets Bundled Automatically:
- ✅ All Python packages from `requirements.txt`
- ✅ PyTorch (CPU version recommended: 200MB vs 400MB GPU)
- ✅ NumPy, PyYAML, and all dependencies
- ✅ All files in `data/models/` and `data/processed/` (pre-trained models)

### What You Need to Manually Include:
- ⚠️ .pth model files (via `datas` in spec file)
- ⚠️ config.yaml (via `datas` in spec file)

### Spec File Will Include:
```
datas=[
    ('data/models', 'data/models'),
    ('data/processed', 'data/processed'),
    ('config/config.yaml', 'config'),
]
hiddenimports=[
    'torch',
    'torch.nn',
    'torch.optim',
    'yaml',
    'sqlite3',
]
```

---

## 4. FIRST-RUN DETECTION & LIFECYCLE

### Detection Logic Flow:

```
Application Start
    ↓
Check: app_state.db exists?
    ├─ NO  → First Run (execution_count = 0)
    │   └─ Initialize DB
    │   └─ Show "Setting up..." message
    │   └─ Enter DATA COLLECTION phase
    │
    └─ YES → Check execution_count in DB
        └─ execution_count <= 10?
            ├─ YES  → In COLLECTION phase
            │   └─ Collect data
            │   └─ Store to data/collection/
            │   └─ Update execution_count++
            │   └─ Run preprocessing
            │   └─ Check if ready to train (execution_count >= 10)
            │       └─ YES → Train model, move to PRODUCTION phase
            │       └─ NO  → Exit normally
            │
            └─ NO   → In PRODUCTION phase
                └─ Load trained model
                └─ Run prefetcher (normal operation)
                └─ Update usage_log
                └─ Exit normally
```

### Execution Count Thresholds:
- **0-1**: Initial setup, no model available yet
- **2-10**: Active data collection, incremental training at iteration 10
- **11+**: Production mode, use trained model

---

## 5. DATA PERSISTENCE STRATEGY

### SQLite Schema: `app_state.db`

```sql
-- Application state tracking
CREATE TABLE app_state (
    id INTEGER PRIMARY KEY,
    app_name TEXT UNIQUE,
    execution_count INTEGER DEFAULT 0,
    last_execution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lifecycle_phase TEXT DEFAULT 'COLLECTION',  -- COLLECTION | TRAINING | PRODUCTION
    model_trained INTEGER DEFAULT 0,
    version TEXT
);

-- Execution logs (for analytics)
CREATE TABLE execution_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT UNIQUE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    phase TEXT,  -- COLLECTION | PRODUCTION
    app_name TEXT,
    files_accessed INTEGER,
    files_prefetched INTEGER,
    accuracy REAL,
    data_file_path TEXT
);
```

### Raw Data Collection: `data/collection/execution_*.sqlite`

```sql
CREATE TABLE file_access_trace (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL,
    file_path TEXT,
    operation TEXT,  -- open, read, write, close
    process_name TEXT,
    file_size INTEGER
);
```

### Advantages:
- ✅ Structured data (queryable)
- ✅ No external dependencies for reading
- ✅ Atomic transactions (data integrity)
- ✅ Easy to backup and transfer
- ✅ Built-in (sqlite3 in Python stdlib)

---

## 6. BUILD COMMANDS

### Prerequisites:
```powershell
# 1. Install PyInstaller
pip install pyinstaller

# 2. Verify PyTorch installation
python -c "import torch; print(torch.__version__)"

# 3. Use CPU version (smaller bundle)
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Build Process:

```powershell
# Step 1: Clean previous builds
Remove-Item -Path ".\build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".\dist" -Recurse -Force -ErrorAction SilentlyContinue

# Step 2: Run PyInstaller with spec file
pyinstaller pyinstaller.spec --noconfirm

# Step 3: Verify outputs
Get-Item .\dist\AiFilePrefetcher.exe
Get-Item .\dist\AiFilePrefetcher\  # One-folder mode (faster load)
```

### Expected Build Output:
```
dist/
├── AiFilePrefetcher.exe          (15-30 MB executable wrapper)
└── AiFilePrefetcher/             (folder with all bundles)
    ├── base_library.zip          (Python runtime)
    ├── torch/                    (200-300 MB)
    ├── data/                     (pre-trained models)
    ├── config/
    ├── _internal/                (dependencies)
    └── ... (other libraries)
```

**Total Size**: ~300-450 MB

---

## 7. FIRST-RUN DETECTION IMPLEMENTATION

### `src/first_run.py`

Key responsibilities:
- Check if `app_state.db` exists
- Initialize DB if needed
- Return lifecycle phase (COLLECTION, TRAINING, PRODUCTION)

### `src/persistence.py`

Key responsibilities:
- SQLite connection management
- Data insertion (append-only pattern)
- Query execution count and phase
- Update execution counters

### `src/lifecycle.py`

Key responsibilities:
- Orchestrate the application flow
- Route to collection, training, or prediction
- Update state transitions
- Log execution metadata

---

## 8. DEPLOYMENT WORKFLOW

### For Developers (Building):
```powershell
.\build_exe_standalone.ps1
# Produces: dist/AiFilePrefetcher.exe (standalone, shareable)
```

### For End Users (Using):
1. Download `AiFilePrefetcher.exe`
2. Double-click to run
   - First run: Initializes collection
   - Runs 1-2: Data collection starts (appears to work normally)
   - Run 10-11: Automatic training happens (may take 30-60 seconds)
   - Run 12+: Uses trained model (normal operation)

### User Experience:
```
Iteration 1: "Initializing application... This may take a moment"
Iteration 2-9: "Prefetcher ready" (normal operation)
Iteration 10: "Training model from collected data... (may take 30-60s)"
Iteration 11+: "Using trained model for predictions" (fast operation)
```

---

## 9. HIDDEN IMPORTS CONFIGURATION

Add these to `pyinstaller.spec` to prevent missing module errors:

```python
hiddenimports=[
    'torch.nn',
    'torch.optim',
    'torch.utils.data',
    'yaml',
    'numpy',
    'sqlite3',
    'json',
    'os',
    'sys',
    'subprocess',
]
```

---

## 10. TROUBLESHOOTING

### Issue: "ModuleNotFoundError: No module named 'torch'"
**Solution**: Add `torch` to `hiddenimports` in spec file

### Issue: "FileNotFoundError: config/config.yaml not found"
**Solution**: Ensure `datas` in spec includes config path, and reference as relative path

### Issue: "Database locked" error
**Solution**: Implement connection timeout and retry logic in persistence.py

### Issue: EXE starts but immediately closes
**Solution**: Add console window, check `console=True` in spec, run with debugging

### Issue: .pth model files not included in EXE
**Solution**: Add to `datas=[]` in spec file (do NOT rely on sys._MEIPASS)

---

## 11. SECURITY & DISTRIBUTION NOTES

### For Production Release:
1. **Code Obfuscation** (Optional): Use PyArmor or similar (~$50)
2. **Digital Signing**: Sign EXE with Code Signing Certificate to prevent SmartScreen warning
3. **Installer**: Use NSIS or Inno Setup to create professional installer
4. **Versioning**: Embed version in EXE properties

### Local Data Privacy:
- ✅ All data stays on user's machine
- ✅ No cloud communication by default
- ✅ SQLite database at: `%APPDATA%\AiFilePrefetcher\` or local folder
- ✅ Models trained locally from user's data

---

## Next Steps:
See individual implementation files for code details.
