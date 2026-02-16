# AI-Based File Prefetcher

**Intelligent File Prefetching using Deep Learning for Cold-Start Latency Reduction**

## Overview

This project uses LSTM neural networks to predict and preload files into RAM before applications need them, significantly reducing cold-start launch times for heavy applications like MatLab, Android Studio, GIMP, and more.

### The Problem

When you launch an application after a system reboot, it experiences "cold-start latency" because all necessary files must be loaded from slow storage (SSD/HDD) into fast RAM. Traditional OS prefetching algorithms use simple sequential read-ahead strategies that don't work well with modern applications' complex, non-sequential file access patterns.

### The Solution

We train an LSTM model on real file access traces to predict which files an application will need next. Our system then proactively loads these predicted files into the Linux page cache before the application requests them.

## 🎯 Windows Standalone Executable

New! We now provide a **Windows standalone EXE** that requires no Python installation:

### For End Users
Simply download and run `AiFilePrefetcher.exe`:
- **First 10 runs**: Automatically collects file access data
- **Run 11**: Automatically trains the model (30-120 seconds)
- **Run 12+**: Uses trained model for predictions

All data stored locally on your machine. See [STANDALONE_APP_GUIDE.md](STANDALONE_APP_GUIDE.md) for details.

### For Developers
Build your own Windows EXE:

```powershell
# Prerequisites
pip install pyinstaller torch pyyaml numpy

# Build
.\build_exe_standalone.ps1

# Output: dist/AiFilePrefetcher/AiFilePrefetcher.exe
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) and [QUICK_START_BUILD.md](QUICK_START_BUILD.md) for complete build instructions.

## Features

- **Automated Data Collection**: Uses `strace` to capture file access patterns
- **LSTM Neural Network**: Learns temporal sequences of file accesses
- **Real-time Prefetching**: Daemon that predicts and preloads files using `vmtouch`
- **Performance Evaluation**: Compares cold-start vs prefetched launch times
- **Configurable**: Easy YAML-based configuration for multiple applications

## Requirements

- **OS**: Ubuntu 20.04+ (or similar Linux distribution)
- **RAM**: 4GB minimum
- **Python**: 3.8+
- **Root Access**: Required for cache management and vmtouch operations

## Installation

### Quick Install

```bash
git clone <your-repo-url>
cd ai-file-prefetcher
./scripts/setup.sh
source venv/bin/activate
```

### Manual Install

```bash
# Install system dependencies
sudo apt update
sudo apt install -y strace vmtouch python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Create directories
mkdir -p data/{raw,processed,models}
```

## Quick Start

### 1. Collect Training Data

Collect file access patterns from your target application:

```bash
python main.py collect --app firefox --runs 20
```

This will:
- Launch Firefox 20 times
- Clear system cache before each run
- Capture all file accesses using strace
- Save logs to `data/raw/`

### 2. Preprocess Data

Clean and prepare the data for training:

```bash
python main.py preprocess --app firefox
```

This creates:
- `data/processed/firefox_sequences.csv` - Training sequences
- `data/processed/firefox_vocab.csv` - File vocabulary

### 3. Train the Model

Train the LSTM neural network:

```bash
python main.py train --app firefox
```

Model will be saved to `data/models/firefox_model.h5`

### 4. Run the Prefetcher

Start the prefetching daemon (requires sudo):

```bash
sudo -E env PATH=$PATH python main.py prefetch --app firefox
```

### 5. Evaluate Performance

Compare launch times:

```bash
python main.py evaluate --app firefox --iterations 10
```

## Complete Pipeline

Run all steps automatically:

```bash
python main.py pipeline --app firefox --runs 20
```

## Configuration

Edit `config/config.yaml` to customize:

```yaml
applications:
  firefox:
    command: "firefox"
    warmup_time: 5
  
  your-app:
    command: "/path/to/your-app"
    warmup_time: 3

model:
  sequence_length: 10
  lstm_units: 128
  epochs: 50
  batch_size: 32

prefetching:
  max_predictions: 10
  confidence_threshold: 0.3
```

## Project Structure

```
ai-file-prefetcher/
├── data/
│   ├── raw/              # strace logs
│   ├── processed/        # cleaned CSV files
│   └── models/           # trained models
├── src/
│   ├── collector.py      # data collection
│   ├── preprocessor.py   # data cleaning
│   ├── model.py          # LSTM architecture
│   ├── trainer.py        # training logic
│   ├── prefetcher.py     # real-time daemon
│   └── evaluator.py      # performance testing
├── config/
│   └── config.yaml       # configuration
├── main.py               # CLI entry point
└── requirements.txt      # Python dependencies
```

## How It Works

### 1. Data Collection Phase
```
Application Launch → strace intercepts → File Access Log
```

### 2. Training Phase
```
Raw Logs → Preprocessing → Sequences → LSTM Training → Model
```

### 3. Prefetching Phase
```
Monitor App → Predict Next Files → vmtouch Load to RAM
```

## Performance Tips

### For Better Accuracy
- Collect more training data (30+ runs)
- Increase sequence length in config
- Try different LSTM architectures

### For Faster Training
- Reduce batch size if running out of memory
- Use GPU if available (TensorFlow will auto-detect)
- Enable early stopping (already configured)

## Troubleshooting

### Permission Denied Errors

The prefetcher needs root access:
```bash
sudo -E env PATH=$PATH python main.py prefetch --app firefox
```

### No Module Named 'src'

Make sure you're in the project root:
```bash
cd ai-file-prefetcher
python main.py ...
```

### Model Not Training Well

1. Collect more data: `--runs 30` or more
2. Check if application behavior is consistent
3. Increase model capacity: edit `lstm_units` in config

### vmtouch Not Found

Install vmtouch:
```bash
sudo apt install vmtouch
```

## Advanced Usage

### Add New Application

1. Edit `config/config.yaml`:
```yaml
applications:
  gimp:
    command: "gimp"
    warmup_time: 4
```

2. Collect data:
```bash
python main.py pipeline --app gimp --runs 25
```

### Custom Model Architecture

Edit `src/model.py` to modify the LSTM architecture.

### Export Model for Production

```python
from tensorflow import keras
model = keras.models.load_model('data/models/firefox_model.h5')
model.save('production_model', save_format='tf')
```

## Research Background

This project implements concepts from:
- **Time-Series Prediction**: File access as sequential data
- **Deep Learning**: LSTM for capturing long-term dependencies
- **Operating Systems**: Linux page cache management

### Why AI?

**Static Analysis Limitations:**
- Developers don't control implicit dependencies (shared libraries)
- Application behavior varies by user context
- Manual file lists waste RAM on unused files

**AI Advantages:**
- Learns hidden correlations between files
- Adapts to dynamic execution paths
- Probability-based predictions optimize RAM usage

## Contributing

Contributions welcome! Areas for improvement:
- Multi-application models
- Real-time monitoring integration
- GUI for configuration
- Support for other OS (macOS, Windows)

## License

MIT License - feel free to use for research or commercial projects

## Citation

If you use this in research, please cite:
```
AI-Based File Prefetching for Cold-Start Latency Reduction
[Your Name], 2024
```

## Contact

Questions? Issues? Open a GitHub issue or contact [your-email]

---

**Note**: This is a research project. Test thoroughly before production use.
