# STANDALONE_APP_GUIDE.md

# AI File Prefetcher - Standalone Windows Application Guide

## For End Users

### Installation

1. **Download the Application**
   - Download `AiFilePrefetcher.zip` from the distribution
   - Extract to your desired location (e.g., `C:\Applications\AiFilePrefetcher`)

2. **System Requirements**
   - Windows 7 or later (Windows 10/11 recommended)
   - No Python installation required
   - Minimum 2 GB RAM
   - At least 500 MB disk space available

3. **First Launch**
   - Double-click `AiFilePrefetcher.exe`
   - A console window will appear showing "Setting up..."
   - This is normal on first run

### Application Lifecycle

The application progresses through phases automatically:

#### Phase 1: Collection (Runs 1-10)
```
RUN 1: "FIRST RUN INITIALIZATION - Setting up..."
  ↓ Initializes local database
  
RUN 2-9: "COLLECTION MODE - Gathering user interaction data..."
  ↓ Records file accesses, system behavior
  
RUN 10: Same as above, but triggers training after completion
```

**What the app is doing:**
- Recording which files your applications access
- Noting the order and timing of file operations
- Building a dataset to train the predictive model

**You will see:**
```
Collection Mode - Run 5/10
[✓] Data collection completed
Application Status Summary:
  - Execution Count: 5
  - Lifecycle Phase: COLLECTION
  - Model Trained: No
[Progress] 5/10 collection iterations completed
Remaining: 5 more collections needed before training
```

#### Phase 2: Training (Run 11)
```
RUN 11: "TRAINING MODE - Training model from collected data..."
  ↓ Processes data
  ↓ Trains neural network (may take 30-120 seconds)
  ↓ Transitions to PRODUCTION phase
```

**What the app is doing:**
- Analyzing patterns in collected file access data
- Training an LSTM neural network
- Creating a predictive model

**You will see:**
```
TRAINING MODE
============================================================
Sufficient data collected. Training model now...
This may take 30-120 seconds depending on your system.
============================================================

[Training progress output...]

✓ Model trained successfully in 45.23s
```

#### Phase 3: Production (Runs 12+)
```
RUN 12+: "PRODUCTION MODE - Using trained model for predictions..."
  ↓ Loads trained model
  ↓ Makes predictions on next file accesses
  ↓ Prefetches predicted files
```

**What the app is doing:**
- Using the trained model to predict file accesses
- Pre-loading files before your applications need them
- Optimizing application startup and file access performance

**You will see:**
```
PRODUCTION MODE
============================================================
Using trained model for predictions...
[✓] Prefetcher completed

Application Status Summary:
  - Execution Count: 12
  - Lifecycle Phase: PRODUCTION
  - Model Trained: Yes
[Status] Model is trained and in production mode
```

### Data Storage

All data is stored locally on your machine:

```
C:\Users\YourUsername\AppData\Local\AiFilePrefetcher\  (typical location)
or where you extracted the application folder:

AiFilePrefetcher/
├── data/
│   ├── app_state.db              ← Application state & execution history
│   ├── collection/               ← Raw file access data (runs 1-10)
│   │   ├── execution_*.sqlite
│   │   ├── execution_*.sqlite
│   │   └── ...
│   ├── models/                   ← Trained neural network model
│   │   ├── prefetch_model.pth
│   │   └── ...
│   └── processed/                ← Processed training data
├── logs/
│   └── app.log                   ← Application activity logs
└── config/
    └── config.yaml               ← Configuration settings
```

**Privacy Note:** No data leaves your machine. Everything is stored locally.

### Common Questions

**Q: Why does the app display console messages?**
- The console shows what the application is doing behind the scenes
- It's normal and expected behavior
- You can close it when the application is done (safe to do so)

**Q: How long is training?**
- Training takes 30-120 seconds depending on:
  - Your CPU/GPU power
  - Amount of data collected (depends on application complexity)
  - System background processes
- You'll see a progress message during training

**Q: Can I use the app while collecting data?**
- Yes! The collection phase is passive
- The app monitors your normal application usage
- No special actions needed

**Q: What happens if I uninstall the app?**
- All local data is removed (unless you back it up)
- The next install will be a fresh first-run
- No registry entries or system files are left behind

**Q: How do I reset the application?**
- To start over as if it's a first-run:
  - Open command prompt in the AiFilePrefetcher folder
  - Run: `AiFilePrefetcher.exe --reset`
  - Next execution will be treated as run 1

**Q: What if there was an error?**
- Check `logs/app.log` for detailed error messages
- Common issues:
  - Insufficient disk space: Free up 500MB
  - Permission denied: Run as Administrator
  - Missing dependencies: Reinstall the application

**Q: Can multiple users use this?**
- Yes, each user gets their own isolated database
- Data is not shared between users
- Perfect for shared computers or labs

### Advanced Usage (Command Line)

You can run the application with command-line options:

```powershell
# Interactive menu (default)
AiFilePrefetcher.exe

# Run one lifecycle iteration
AiFilePrefetcher.exe run

# Show lifecycle status
AiFilePrefetcher.exe status

# Run health checks
AiFilePrefetcher.exe doctor

# Reset application state (start over)
AiFilePrefetcher.exe reset

# Show built-in quick manual
AiFilePrefetcher.exe guide

# Enable debug logs for any command
AiFilePrefetcher.exe --debug run

# Optional profile selection
AiFilePrefetcher.exe --app-name "chrome" run
```

Dependency behavior:
- EXE mode: dependencies are bundled; no pip needed.
- Source mode: run `python app_standalone.py setup-deps` once.

Linux-first usage:
- Use `./run_prefetcher_cli.sh run` for normal lifecycle execution.
- Script auto-relaunches with `sudo` when root privileges are required.

---

## For Developers / System Administrators

### Build Process

See `DEPLOYMENT_GUIDE.md` for:
- Tool recommendation (PyInstaller)
- Building the standalone executable
- Customizing bundle contents
- Creating professional installers

### Directory Structure

```
ai-file-prefetcher/
├── src/                          ← Python source code
│   ├── __init__.py
│   ├── collector.py             ← Data collection module
│   ├── preprocessor.py          ← Data preprocessing
│   ├── trainer.py               ← Model training
│   ├── prefetcher.py            ← Prediction/prefetching
│   ├── model.py                 ← LSTM model definition
│   ├── first_run.py             ⭐ First-run detection
│   ├── persistence.py           ⭐ SQLite data layer
│   └── lifecycle.py             ⭐ Lifecycle orchestration
├── config/
│   └── config.yaml              ← Configuration
├── data/
│   ├── models/                  ← .pth files (bundled)
│   ├── processed/               ← Vocabularies (bundled)
│   └── raw/                     ← Sample data
├── app_standalone.py            ⭐ Standalone entry point
├── pyinstaller.spec             ⭐ PyInstaller configuration
├── build_exe_standalone.ps1     ⭐ Build script
├── DEPLOYMENT_GUIDE.md          ⭐ Build & deployment guide
└── STANDALONE_APP_GUIDE.md      ← This file

⭐ = Files created for standalone packaging
```

### Building the Executable

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Run the build script:**
   ```powershell
   .\build_exe_standalone.ps1
   ```

3. **Verify output:**
   ```powershell
   ls .\dist\AiFilePrefetcher\AiFilePrefetcher.exe
   Get-Item .\dist\* | Measure-Object -Property Length -Sum
   ```

4. **Test:**
   ```powershell
   .\dist\AiFilePrefetcher\AiFilePrefetcher.exe
   ```

### Distribution

**Option 1: Folder Distribution**
```powershell
# Compress the distribution
Compress-Archive -Path ".\dist\AiFilePrefetcher" -DestinationPath ".\AiFilePrefetcher.zip"

# Share AiFilePrefetcher.zip with users
# Users extract and run AiFilePrefetcher.exe
```

**Option 2: Cloud/Network Share**
```powershell
# Copy folder to shared location
Copy-Item -Path ".\dist\AiFilePrefetcher" -Destination "\\network\share\applications\" -Recurse
```

**Option 3: Professional Installer**
Consider using NSIS or Inno Setup to create `.msi` or `.exe` installer.

### Customization

#### Change Application Name

**In `config.yaml`:**
```yaml
system:
  app_name: "gimp"           # Change this to your app
  target_app: "gimp --no-splash"
```

**In `app_standalone.py`:**
```python
# Change default in argparse
parser.add_argument("--app-name", default="gimp")
```

**In `pyinstaller.spec`:**
```python
# Change output name
name='GimpPrefetcher'  # Instead of AiFilePrefetcher
```

#### Modify First-Run Behavior

Edit `src/lifecycle.py`:
- Change `execution_count` thresholds (currently 10)
- Modify training trigger conditions
- Add custom messages for different phases

#### Add Custom Data Collection

Edit `app_standalone.py`, function `create_collection_wrapper()`:
```python
def collection_handler(execution_db):
    # Call original collector
    collect_traces()
    
    # Add custom collection logic
    execution_db.add_file_access(
        timestamp=time.time(),
        file_path="/path/to/file",
        operation="custom",
        process_name="your_process"
    )
```

#### Change Database Location

Edit `src/persistence.py`:
```python
# Default location: data/app_state.db
# Change db initialization:
db = AppStateDB(db_path="C:\\Users\\YourUsername\\AppData\\Local\\AiFilePrefetcher\\app_state.db")
```

### Troubleshooting Build Issues

**PyInstaller not found:**
```powershell
pip install pyinstaller
```

**Missing torch module:**
```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Build hangs at PyTorch:**
- This is normal - PyTorch is large and can take time to bundle
- Give the build process 5-10 minutes to complete

**File permissions error:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**EXE produces "ModuleNotFoundError":**
- Add the module name to `hiddenimports` in `pyinstaller.spec`
- Rebuild

### Performance Optimization

**Reduce Bundle Size:**
1. Use CPU-only PyTorch (already configured)
2. Remove pre-trained models not needed
3. Update `datas` in `pyinstaller.spec`

**Faster Startup:**
1. Use one-folder mode (already configured)
2. Add `-y` flag: `pyinstaller pyinstaller.spec -y`
3. Disable console window if not needed: change `console=False`

### Security Considerations

**If distributing to external users:**
1. **Code Obfuscation**: Consider PyArmor (~$50 license)
2. **Digital Signing**: Sign EXE with code signing certificate
3. **Installer**: Use professional installer (NSIS/Inno Setup)
4. **SmartScreen**: Large publishers sign to prevent warning

**Local Data Security:**
- All data stored locally (no cloud upload)
- Users have full control of their data
- No telemetry or external communication

### Updating the Application

1. Update source code
2. Rebuild: `.\build_exe_standalone.ps1 -Clean`
3. Users replace old folder with new folder
4. State database (app_state.db) persists across updates

---

## Troubleshooting Reference

### Issue: "Execution count stuck at 10"
**Solution**: Model completed training. Check `data/models/` for trained `.pth` file.

### Issue: "Very slow first run"
**Solution**: First run downloads/initializes PyTorch (~200MB). Expected on first execution.

### Issue: "Data folder not found"
**Solution**: Ensure `data/models/` and `data/processed/` directories are in bundle.

### Issue: "Can't find config.yaml"
**Solution**: Verify `datas` section in `pyinstaller.spec` includes config path.

---

## Support & Documentation

- **Build Guide**: See `DEPLOYMENT_GUIDE.md`
- **Logs**: Check `logs/app.log` for detailed execution traces
- **Source Code**: See individual files in `src/` for implementation details
- **Database Schema**: See `src/persistence.py` for database structure

---

Last Updated: February 2026
