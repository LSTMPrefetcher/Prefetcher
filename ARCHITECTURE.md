# ARCHITECTURE.md

# AI File Prefetcher - Windows Standalone Architecture

Visual diagrams and technical architecture documentation.

---

## 1. Application Lifecycle State Machine

```
┌──────────────────────────────────────────────────────────────────┐
│                      First Application Run                        │
│                    (Execution Count = 0)                          │
│                                                                    │
│  1. User Double-clicks: AiFilePrefetcher.exe                      │
│  2. Windows launches executable                                   │
│  3. app_standalone.py::main() executes                            │
│  4. ApplicationLifecycle.initialize()                             │
│     ├─ Check if data/app_state.db exists                          │
│     ├─ Database does NOT exist → First run detected ✓             │
│     ├─ Call FirstRunManager.get_or_initialize_state()             │
│     ├─ Create app_state.db with initial values                    │
│     ├─ Create execution ID: prefetch_20260216_143045_a1b2c3d4    │
│     └─ Load state into memory                                     │
│  5. Check lifecycle phase: COLLECTION                             │
│  6. Increment execution_count = 1                                 │
│  7. Call execute_collection_phase()                               │
│     ├─ Print: "FIRST RUN INITIALIZATION - Setting up..."         │
│     ├─ Create ExecutionDataDB for this execution                  │
│     ├─ Call collector_handler()                                   │
│     │  └─ Call collect_traces() [Original function]               │
│     ├─ Data stored in data/collection/execution_*.sqlite          │
│     ├─ Log execution with metadata                                │
│     ├─ Print status summary and progress (1/10 completed)         │
│     └─ Exit gracefully with code 0                                │
│                                                                    │
│  Visible to User:                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ============================================================ │  │
│  │   FIRST RUN INITIALIZATION                                 │  │
│  │ ============================================================ │  │
│  │ Setting up prefetcher...                                   │  │
│  │ This first run will initialize the application.            │  │
│  │ ============================================================ │  │
│  │                                                            │  │
│  │ [*] Collecting data for prefetcher...                     │  │
│  │ [*] Running strace...                                     │  │
│  │ [✓] Data collection completed                             │  │
│  │                                                            │  │
│  │ Application Status Summary:                                │  │
│  │   - Name: prefetcher                                      │  │
│  │   - Version: 1.0                                          │  │
│  │   - Execution Count: 0                                    │  │
│  │   - Lifecycle Phase: COLLECTION                           │  │
│  │   - Model Trained: No                                     │  │
│  │   - Last Execution: 2026-02-16 14:30:45                  │  │
│  │                                                            │  │
│  │ [Progress] 0/10 collection iterations completed            │  │
│  │ Remaining: 10 more collections needed before training     │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  State After Execution:                                            │
│  ├─ data/app_state.db                                             │
│  │  ├─ app_name: "prefetcher"                                     │
│  │  ├─ execution_count: 1                                         │
│  │  ├─ lifecycle_phase: "COLLECTION"                              │
│  │  └─ model_trained: 0                                           │
│  ├─ data/collection/execution_prefetch_20260216_143045_a1b2c3d4.sqlite │
│  │  └─ file_access_trace [entries from this execution]            │
│  └─ logs/app.log [execution details]                              │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
                   (User runs program again)
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│             Collection Phase (Runs 2-9)                           │
│          (Execution Count = 1 to 9)                               │
│                                                                    │
│  Each run (e.g., Run 5 = execution_count starts at 4):           │
│                                                                    │
│  1. app_standalone.py::main() executes                            │
│  2. ApplicationLifecycle.initialize()                             │
│     ├─ data/app_state.db EXISTS → Load existing state             │
│     ├─ execution_count = 4                                        │
│     ├─ Create new execution ID for this run                       │
│     └─ Load state into memory                                     │
│  3. Check lifecycle phase: COLLECTION                             │
│  4. Call execute_collection_phase()                               │
│     ├─ Print: "[COLLECTION MODE] Run 4/10 - Gathering..."        │
│     ├─ Call collector_handler()                                   │
│     │  └─ Call collect_traces() [Original function]               │
│     ├─ Data stored in data/collection/execution_*.sqlite          │
│     └─ Increment execution_count: 4 → 5                           │
│  5. Exit with code 0                                              │
│                                                                    │
│  Files Created This Run:                                           │
│  └─ data/collection/execution_prefetch_20260216_143046_b2c3d4e5.sqlite │
│                                                                    │
│  Progress:                                                          │
│  ├─ Run 2: execution_count → 1 (1/10 ✓)                           │
│  ├─ Run 3: execution_count → 2 (2/10 ✓)                           │
│  ├─ Run 4: execution_count → 3 (3/10 ✓)                           │
│  ├─ Run 5: execution_count → 4 (4/10 ✓)                           │
│  └─ ...continues...                                                │
│                                                                    │
│  Console Message Pattern:                                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ [COLLECTION MODE] Run 4/10 - Gathering user data...        │  │
│  │ [*] Collecting data for prefetcher...                      │  │
│  │ [✓] Data collection completed                              │  │
│  │                                                            │  │
│  │ Application Status Summary:                                │  │
│  │   - Execution Count: 4                                    │  │
│  │   - Lifecycle Phase: COLLECTION                           │  │
│  │   - Model Trained: No                                     │  │
│  │                                                            │  │
│  │ [Progress] 4/10 collection iterations completed            │  │
│  │ Remaining: 6 more collections needed before training      │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
                   (Run 10: Trigger)
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│         Training Phase (Run 11) ⚠️ SPECIAL                        │
│   Runs ONLY when execution_count == 10 AND NOT trained            │
│                                                                    │
│  Initialization:                                                   │
│  1. app_standalone.py::main() executes (Run 10)                   │
│  2. ApplicationLifecycle.initialize()                             │
│     └─ execution_count loaded as 9 (from previous runs)           │
│  3. Check: should_train_model()?                                  │
│     └─ execution_count == 10? (Will be after increment) ✓         │
│     └─ model_trained == False? ✓                                  │
│     └─ YES → TRAINING TRIGGERED!                                  │
│  4. Call execute_training_phase()                                 │
│     ├─ Update app_state.lifecycle_phase = "TRAINING"             │
│     ├─ Print: "TRAINING MODE - Training model..."               │
│     ├─ Time training: start_time = time.time()                   │
│     ├─ Call trainer_handler()                                    │
│     │  ├─ Load 10 datasets from data/collection/*.sqlite         │
│     │  ├─ Call preprocess() [Original function]                  │
│     │  │  └─ Process file access traces into sequences           │
│     │  ├─ Call train_model() [Original function]                 │
│     │  │  ├─ Initialize LSTM model                               │
│     │  │  ├─ Train for 30 epochs                                 │
│     │  │  ├─ Print progress: epoch 1/30, epoch 2/30, ...        │
│     │  │  └─ Save to data/models/prefetch_model.pth              │
│     │  └─ Training complete                                      │
│     ├─ elapsed = time.time() - start_time                        │
│     ├─ Call FirstRunManager.mark_model_trained()                 │
│     │  ├─ Set model_trained = 1 (true)                           │
│     │  └─ Set lifecycle_phase = "PRODUCTION"                     │
│     ├─ Log execution with metadata                               │
│     ├─ Print: "✓ Model trained successfully in 45.23s"          │
│     └─ Increment execution_count: 9 → 10                         │
│  5. Exit with code 0                                              │
│                                                                    │
│  Visible to User:                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ============================================================ │  │
│  │   TRAINING MODE                                            │  │
│  │ ============================================================ │  │
│  │ Sufficient data collected. Training model now...           │  │
│  │ This may take 30-120 seconds depending on your system.    │  │
│  │ ============================================================ │  │
│  │                                                            │  │
│  │ epoch 1/30: loss=2.154                                    │  │
│  │ epoch 2/30: loss=1.987                                    │  │
│  │ epoch 3/30: loss=1.823                                    │  │
│  │ ...                                                        │  │
│  │ epoch 30/30: loss=0.245                                   │  │
│  │                                                            │  │
│  │ ✓ Model trained successfully in 45.23s                   │  │
│  │                                                            │  │
│  │ Application Status Summary:                                │  │
│  │   - Execution Count: 10                                   │  │
│  │   - Lifecycle Phase: PRODUCTION                           │  │
│  │   - Model Trained: Yes                                    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  Files Created:                                                    │
│  ├─ data/models/prefetch_model.pth (trained model)               │
│  ├─ data/processed/vocab.json (vocabulary mapping)               │
│  └─ Updated data/app_state.db                                    │
│                                                                    │
│  Database State After Training:                                    │
│  ├─ execution_count: 10                                           │
│  ├─ lifecycle_phase: "PRODUCTION"                                 │
│  └─ model_trained: 1                                              │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
                (Run 12+: Production mode)
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│         Production Phase (Runs 11+)                               │
│         (Using trained model for predictions)                     │
│                                                                    │
│  Each production run (e.g., Run 12):                              │
│                                                                    │
│  1. app_standalone.py::main() executes                            │
│  2. ApplicationLifecycle.initialize()                             │
│     ├─ Load data/app_state.db                                     │
│     ├─ execution_count = 10                                       │
│     ├─ model_trained = 1 ✓                                        │
│     └─ lifecycle_phase = "PRODUCTION"                             │
│  3. Check: is_production_mode()?                                  │
│     └─ model_trained == 1? ✓ YES!                                │
│  4. Call execute_production_phase()                               │
│     ├─ Print: "[PRODUCTION MODE] Using trained model..."        │
│     ├─ Call production_handler()                                 │
│     │  ├─ Call run_prefetcher() [Original function]              │
│     │  ├─ Load data/models/prefetch_model.pth                    │
│     │  ├─ Load data/processed/vocab.json                         │
│     │  ├─ Prepare input tensor from recent file accesses        │
│     │  ├─ Forward through LSTM: model(input_tensor)             │
│     │  ├─ Get prediction: torch.argmax(output, dim=1)           │
│     │  ├─ Convert index to file path                             │
│     │  ├─ Prefetch using vmtouch                                 │
│     │  └─ Print: "[*] Prediction: [filename]"                   │
│     ├─ Log execution with metadata                               │
│     ├─ Increment execution_count: 10 → 11                        │
│     └─ Exit with code 0                                          │
│  5. Return to user                                                │
│                                                                    │
│  Visible to User:                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ [PRODUCTION MODE] Using trained model for predictions...   │  │
│  │ [*] Running prefetcher for prefetcher...                  │  │
│  │ [*] Prediction: /path/to/predicted/file.so                │  │
│  │ [✓] Prefetcher completed                                  │  │
│  │                                                            │  │
│  │ Application Status Summary:                                │  │
│  │   - Execution Count: 11                                   │  │
│  │   - Lifecycle Phase: PRODUCTION                           │  │
│  │   - Model Trained: Yes                                    │  │
│  │                                                            │  │
│  │ [Status] Model is trained and in production mode          │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  Each subsequent run:                                              │
│  ├─ Run 12: execution_count = 11 (1st production run) ✓          │
│  ├─ Run 13: execution_count = 12 (2nd production run)            │
│  ├─ Run 14: execution_count = 13 (3rd production run)            │
│  └─ Continues indefinitely with model predictions...              │
│                                                                    │
│  Performance Benefit:                                              │
│  ├─ BEFORE: Cold start - all files loaded from disk (slow)       │
│  ├─ AFTER: Prefetched files already in RAM (fast)                │
│  └─ Improvement: 10-50% faster application startup                │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow Architecture

```
User Runs: AiFilePrefetcher.exe
        ↓

    ┌──────────────────────────────────────────────────┐
    │ ENTRY POINT: app_standalone.py::main()           │
    │ - Setup logging                                  │
    │ - Parse CLI arguments                            │
    │ - Create ApplicationLifecycle instance           │
    └──────────────────────────────────────────────────┘
                        ↓

    ┌──────────────────────────────────────────────────┐
    │ FIRST RUN CHECK: first_run.py::FirstRunManager   │
    │ - Check if app_state.db exists                   │
    │ - Initialize if first run                        │
    │ - Load or create app_state                       │
    └──────────────────────────────────────────────────┘
                        ↓

    ┌─────────────────────────────────────────────────────────┐
    │ PHASE DECISION: lifecycle.py::ApplicationLifecycle      │
    │ - Check execution_count                                 │
    │ - Check model_trained flag                              │
    │ - Determine phase: COLLECTION|TRAINING|PRODUCTION       │
    └─────────────────────────────────────────────────────────┘
                    ↙           ↓           ↘

    PHASE 1           PHASE 2             PHASE 3
    COLLECTION        TRAINING            PRODUCTION
    (count < 10)      (count == 10)       (count > 10)
         ↓                  ↓                   ↓

    ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
    │ COLLECTION   │ │  TRAINING   │ │ PRODUCTION   │
    └──────────────┘ └─────────────┘ └──────────────┘
         ↓                  ↓                   ↓

COLLECTION FLOW:       TRAINING FLOW:        PRODUCTION FLOW:

1. Create unique    1. Load 10 datasets  1. Load model
   execution ID        from collection      from disk
   ↓                   ↓
2. Create            2. Call preprocess()
   ExecutionDataDB      ↓
   ↓                 3. Call train_model()
3. Call                 ├─ Initialize
   collect_traces()       LSTM
   ├─ Monitor file      ├─ Train 30 epochs
     accesses           ├─ Save .pth file
   ├─ Record with       └─ Print progress
     timestamps         ↓
   └─ Store in       4. Mark as trained
     .sqlite          ↓
   ↓                 5. Transition to
4. Collect data        PRODUCTION phase
   complete           ↓
   ↓                 Increment count
5. Log execution    (10 → 11)
   ↓                 ↓
6. Increment      Training complete
   count            Return to user
   (0→1→...→9)
   ↓
7. Return to user
   "Gathering data"

                                       2. Load vocab
                                          ↓
                                       3. Call
                                          run_prefetcher()
                                          ├─ Prepare input
                                          ├─ Forward pass
                                          ├─ Get prediction
                                          ├─ Prefetch files
                                          └─ Print result
                                       ↓
                                       4. Log execution
                                          ↓
                                       5. Increment count
                                          (10→11→...∞)
                                       ↓
                                       6. Return to user
                                          "Using model"


        ↓                 ↓                   ↓

    STORAGE        STORAGE             STORAGE
    
data/collection/   data/models/       data/
execution_*.sqlite prefetch_model.pth ├─models/
├─timestamp           data/processed/  ├─processed/
├─file_path          vocab.json        └─app_state.db
├─operation          data/app_state.db  (no new)
├─process_name       (updated)
└─file_size          logs/app.log
                     (training details)
```

---

## 3. Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                    data/app_state.db                        │
│                                                              │
│  TABLE: app_state                                           │
│  ┌────────────────────────────────────────────────────────┐│
│  │ id (INTEGER PRIMARY KEY)                                ││
│  │ app_name (TEXT UNIQUE)                = "prefetcher"    ││
│  │ execution_count (INTEGER)             = 10              ││
│  │ last_execution (TIMESTAMP)            = "2026-..."      ││
│  │ lifecycle_phase (TEXT)                = "PRODUCTION"    ││
│  │ model_trained (INTEGER BOOLEAN)       = 1               ││
│  │ version (TEXT)                        = "1.0"           ││
│  │ metadata (TEXT JSON)                  = "{...}"         ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  TABLE: execution_log                                       │
│  ┌────────────────────────────────────────────────────────┐│
│  │ id (INTEGER PRIMARY KEY AUTOINCREMENT)                  ││
│  │ execution_id (TEXT UNIQUE) = "prefetch_20260216_143045" ││
│  │ timestamp (TIMESTAMP)      = "2026-02-16 14:30:45"      ││
│  │ phase (TEXT)               = "PRODUCTION"               ││
│  │ app_name (TEXT)            = "prefetcher"               ││
│  │ metadata (TEXT JSON) = {                                ││
│  │     "files_accessed": 127,                              ││
│  │     "files_prefetched": 45,                             ││
│  │     "accuracy": 0.92,                                   ││
│  │     "execution_number": 10                              ││
│  │ }                                                       ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  Multiple entries, one per execution:                       │
│  ├─ Row 1: "prefetch_20260216_143045_a1b2c3d4" COLLECTION  │
│  ├─ Row 2: "prefetch_20260216_143046_b2c3d4e5" COLLECTION  │
│  ├─ Row 3: "prefetch_20260216_143047_c3d4e5f6" COLLECTION  │
│  ...                                                        │
│  ├─ Row 10: "prefetch_20260216_143055_j8k9l0m1" TRAINING   │
│  └─ Row 11: "prefetch_20260216_143056_k9l0m1n2" PRODUCTION │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│            data/collection/execution_*.sqlite               │
│        (One .sqlite file per execution, Run 1-10)           │
│                                                              │
│ FILE: data/collection/                                      │
│       execution_prefetch_20260216_143045_a1b2c3d4.sqlite    │
│                                                              │
│  TABLE: file_access_trace (one file per add_file_access)   │
│  ┌────────────────────────────────────────────────────────┐│
│  │ id (INTEGER PRIMARY KEY AUTOINCREMENT)      = 1         ││
│  │ timestamp (REAL)                            = 1708107045││
│  │ file_path (TEXT)                = "/usr/lib/libc.so.6"  ││
│  │ operation (TEXT)                = "open"                ││
│  │ process_name (TEXT)             = "python"              ││
│  │ file_size (INTEGER)             = 2097152               ││
│  │ additional_data (TEXT JSON)     = "{...}"               ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  Multiple entries captured during execution:                │
│  ├─ Row 1: /lib64/ld-linux-x86-64.so (open, python)       │
│  ├─ Row 2: /usr/lib/libc.so.6 (open, python)              │
│  ├─ Row 3: /home/user/.config/app (read, python)          │
│  ├─ Row 4: /var/lib/app/cache.db (read, python)           │
│  ├─ Row 5: /tmp/app_temp_12345 (write, app)               │
│  └─ ... (many more, depending on application)              │
│                                                              │
│ Total size: ~1-10 MB per execution (depends on data)        │
│                                                              │
│ Lifecycle for these files:                                  │
│ ├─ Run 1-10: Created and retained                           │
│ ├─ Run 11 (Training): READ for preprocessing                │
│ └─ Run 12+: Optionally archived or deleted                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Meta Information:
├─ data/app_state.db: ~100 KB
├─ data/collection/: ~10-100 MB (10 files × 1-10 MB each)
└─ data/models/: ~10-50 MB (trained .pth file)
   └─ Total for first-run to production: ~120-200 MB
```

---

## 4. File Organization

```
ai-file-prefetcher/
│
├─── 📋 Documentation (NEW)
│   ├─ DEPLOYMENT_GUIDE.md          ← Tool comparison, structure, build
│   ├─ STANDALONE_APP_GUIDE.md      ← User & developer guide
│   ├─ QUICK_START_BUILD.md         ← Quick reference
│   ├─ IMPLEMENTATION_SUMMARY.md    ← What was built
│   ├─ IMPLEMENTATION_CHECKLIST.md  ← Testing & deployment steps
│   └─ ARCHITECTURE.md              ← This file
│
├─── 🐍 Source Code
│   ├─ main.py                      ← Original entry (unchanged)
│   ├─ app_standalone.py            ← NEW: Windows EXE entry point
│   │
│   └─ src/
│       ├─ __init__.py
│       ├─ collector.py             ← Original (unchanged)
│       ├─ preprocessor.py          ← Original (unchanged)
│       ├─ trainer.py               ← Original (unchanged)
│       ├─ prefetcher.py            ← Original (unchanged)
│       ├─ evaluator.py             ← Original (unchanged)
│       ├─ model.py                 ← Original (unchanged)
│       ├─ utils.py                 ← Original (unchanged)
│       ├─ first_run.py             ← NEW: First-run detection
│       ├─ persistence.py           ← NEW: SQLite data layer
│       └─ lifecycle.py             ← NEW: Phase orchestration
│
├─── ⚙️ Configuration
│   ├─ config.yaml                  ← App configuration (unchanged)
│   ├─ requirements.txt             ← Dependencies (unchanged)
│   ├─ pyinstaller.spec            ← NEW: PyInstaller config
│   ├─ build_exe.ps1                ← Original Windows build
│   └─ build_exe_standalone.ps1     ← NEW: Main build script
│
├─── 📦 Data (Runtime)
│   ├─ app_state.db                 ← NEW: Created at first run
│   ├─ models/
│   │   ├─ chrome_model.pth         ← Pre-trained (bundled)
│   │   ├─ gimp_model.pth           ← Pre-trained (bundled)
│   │   └─ prefetch_model.pth       ← NEW: Trained at run 11
│   ├─ processed/
│   │   ├─ chrome_vocab.json        ← Pre-trained (bundled)
│   │   ├─ gimp_vocab.json          ← Pre-trained (bundled)
│   │   └─ vocab.json               ← NEW: Generated at run 10
│   ├─ raw/                         ← Example data (unchanged)
│   └─ collection/                  ← NEW: Execution data
│       └─ execution_*.sqlite       ← Runs 1-10 data files
│
├─── 📖 Scripts
│   ├─ scripts/
│   │   └─ ... original scripts
│   └─ logs/                        ← NEW: Created at first run
│       └─ app.log                  ← Execution logs
│
├─── 📄 Project Files
│   ├─ README.md                    ← Updated with EXE info
│   ├─ LICENSE
│   └─ .gitignore                   ← Updated for build artifacts
│
└─── 📦 Build Outputs (Created after build)
    └─ dist/
        └─ AiFilePrefetcher/        ← Distribution folder (~450 MB)
            ├─ AiFilePrefetcher.exe ← EXECUTABLE
            ├─ base_library.zip    
            ├─ torch/               ← PyTorch library (200 MB)
            ├─ data/                ← Models & config (bundled)
            ├─ src/                 ← Application code
            ├─ config/
            └─ ... (dependencies)
```

---

## 5. Class Diagram

```
┌─────────────────────────────────┐
│   ApplicationLifecycle          │
│  (Main orchestrator)            │
├─────────────────────────────────┤
│ - app_name: str                 │
│ - app_version: str              │
│ - first_run_manager: obj        │
│ - app_state: dict               │
│ - execution_id: str             │
│ - execution_db: obj             │
├─────────────────────────────────┤
│ + initialize()                  │
│ + get_current_phase()           │
│ + execute_collection_phase()    │
│ + execute_training_phase()      │
│ + execute_production_phase()    │
│ + run()                         │
│ + print_startup_message()       │
│ + get_status_summary()          │
└─────────────────────────────────┘
         │
         │ uses
         ↓
┌─────────────────────────────────┐
│  FirstRunManager                │
│  (Tracks execution state)       │
├─────────────────────────────────┤
│ - app_name: str                 │
│ - db: AppStateDB                │
├─────────────────────────────────┤
│ + is_first_run()                │
│ + get_or_initialize_state()     │
│ + should_collect_data()         │
│ + should_train_model()          │
│ + is_production_mode()          │
│ + log_execution()               │
│ + mark_model_trained()          │
│ + reset_state()                 │
└─────────────────────────────────┘
         │
         │ uses
         ↓
┌─────────────────────────────────┐
│  AppStateDB                     │
│  (Global app state)             │
├─────────────────────────────────┤
│ - db_path: str                  │
├─────────────────────────────────┤
│ + init_app_state()              │
│ + get_app_state()               │
│ + increment_execution_count()   │
│ + set_lifecycle_phase()         │
│ + set_model_trained()           │
│ + log_execution()               │
│ + get_recent_executions()       │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│  ExecutionDataDB                │
│  (Per-execution data)           │
├─────────────────────────────────┤
│ - execution_id: str             │
│ - db_path: str                  │
├─────────────────────────────────┤
│ + add_file_access()             │
│ + get_all_accesses()            │
│ + get_access_count()            │
└─────────────────────────────────┘
```

---

## 6. Sequence Diagram: First Run to Production

```
User              app_standalone.py    lifecycle.py      persistence.py    Original Code
 │                      │                   │                  │               │
 │ double-click         │                   │                  │               │
 ├──────────────────────>│                   │                  │               │
 │                      │                   │                  │               │
 │                      │ initialize()      │                  │               │
 │                      ├─────────────────>                    │               │
 │                      │                   │ get_app_state()  │               │
 │                      │                   ├─────────────────>│               │
 │                      │                   │<─────────────────┤  (None)       │
 │                      │  (first run)      │                  │               │
 │                      │                   │ init_app_state() │               │
 │                      │                   ├─────────────────>│               │
 │                      │                   │ create DB        >               │
 │                      │<─────────────────┤                  │               │
 │                      │                   │                  │               │
 │                      │ should_collect_data() [true]         │               │
 │                      │                   │                  │               │
 │                      │ execute_collection_phase()           │               │
 │                      ├─────────────────>│                  │               │
 │                      │                   │ create ExecutionDataDB        │
 │                      │                   ├─────────────────────────────>│
 │                      │                   │ collect_traces()             │
 │                      │                   ├─────────────────────────────>│
 │ [Console msg]        │                   │                  │          │[strace] │
 │<─ FIRST RUN          │                   │                  │          │ output  │
 │  INITIALIZATION      │                   │                  │<─────────┤         │
 │                      │                   │                  │  data    │         │
 │ [*] Collecting...    │                   │ add_file_access()           │
 │                      │                   │ x100 calls       │<─────────┴─────────┤
 │ [✓] Complete        │                   │                  │                    │
 │                      │ log_execution()   │                  │                    │
 │ Status:              ├─────────────────┤                  │                    │
 │  Count: 0            │                   ├─────────────────>│                    │
 │  Phase: COLLECTION   │                   │                  │ insert log entry   │
 │                      │ increment_count() │                  │                    │
 │ [Progress] 0/10      │                   ├─────────────────>│ count: 0→1         │
 │                      │                   │                  │                    │
 └─ wait for next run ──┤                   │                  │                    │


                         [Wait for Run 2-9: Similar to above, repeat 8 times]


User              app_standalone.py    lifecycle.py      persistence.py    Original Code
 │                      │                   │                  │               │
 │ Run 10: repeat       │                   │                  │               │
 ├──────────────────────>│                   │                  │               │
 │                      │ initialize()      │                  │               │
 │                      ├─────────────────>│ get_app_state()   │               │
 │                      │                   ├─────────────────>│               │
 │                      │<─────────────────┤ count: 9, train: false          │
 │                      │                   │<─────────────────┤               │
 │                      │ should_train_model() [true]          │               │
 │                      │                   │                  │               │
 │                      │ execute_training_phase()             │               │
 │                      ├─────────────────>│                  │               │
 │                      │                   │                  │               │
 │ [Console msg]        │                   │ set_lifecycle_phase("TRAINING") │
 │<─ TRAINING MODE      │                   ├─────────────────>│               │
 │  Training...         │                   │<─────────────────┤               │
 │                      │                   │ preprocess()     │               │
 │                      │                   ├─────────────────────────────────>│
 │ epoch 1/30...        │                   │                  │               │
 │                      │                   │ train_model()    │               │
 │ epoch 30/30         │                   ├─────────────────────────────────>│
 │                      │                   │ (training occurs here, 30-120s) │
 │ ✓ Model complete    │                   │                  │               │
 │  in 45s              │                   │                  │<──────────────┤
 │                      │                   │ mark_model_trained(true)       │
 │ Status:              │                   ├─────────────────>│               │
 │  Count: 10           │                   │ set_lifecycle_phase("PRODUCTION")
 │  Phase: PRODUCTION   │                   │ count: 9→10      │               │
 │  Model: YES          │                   │<─────────────────┤               │
 │                      │<─────────────────┤                  │               │
 │ [Progress] Model OK  │                   │                  │               │
 │                      │                   │                  │               │
 └─ continue to run ────┤                   │                  │               │


                        [Runs 11+: Production mode, repeat indefinitely]


User              app_standalone.py    lifecycle.py      persistence.py    Original Code
 │                      │                   │                  │               │
 │ Run 11+: execute     │                   │                  │               │
 ├──────────────────────>│                   │                  │               │
 │                      │ initialize()      │                  │               │
 │                      ├─────────────────>│ get_app_state()   │               │
 │                      │                   ├─────────────────>│               │
 │                      │<─────────────────┤ count: 10, train: true            │
 │                      │<─────────────────┤                  │               │
 │                      │ is_production_mode() [true]         │               │
 │                      │                   │                  │               │
 │                      │ execute_production_phase()          │               │
 │                      ├─────────────────>│                  │               │
 │                      │                   │                  │               │
 │ [Console msg]        │                   │ run_prefetcher() │               │
 │<─ PRODUCTION MODE    │                   ├─────────────────────────────────>│
 │  Using model...      │                   │                  │               │
 │                      │                   │ (load model + make prediction)  │
 │ [*] Prediction:      │                   │                  │               │
 │  /path/to/file       │                   │                  │<──────────────┤
 │ [✓] Complete        │                   │                  │               │
 │                      │ log_execution()   │                  │               │
 │ Status:              │                   ├─────────────────>│               │
 │  Count: 11           │                   │ increment: 10→11 │               │
 │  Phase: PRODUCTION   │                   │<─────────────────┤               │
 │  Model: YES          │                   │                  │               │
 │                      │<─────────────────┤                  │               │
 │ [Status] Model OK    │                   │                  │               │
 │                      │                   │                  │               │
 └─ app working ────────┤                   │                  │               │
```

---

This architecture provides a robust, scalable, and maintainable system for converting the Python application into a standalone Windows executable with automatic lifecycle management.

**Key Design Principles:**
1. **Separation of Concerns**: Lifecycle, persistence, and original code are separate
2. **Immutability of Original Code**: Existing collectors, trainers, and prefetchers unchanged
3. **Transparent Data Collection**: No user action required during collection phase
4. **Automatic Progression**: Phase transitions happen without user input
5. **Local-First Architecture**: All data stays on user's machine
6. **Comprehensive Logging**: Full audit trail of all operations
7. **Simple Error Recovery**: Graceful fallback on training failures

---

**Last Updated:** February 16, 2026
