cat > src/__init__.py << 'EOF'
"""
AI File Prefetcher Package
"""

__version__ = "1.0.0"

from .collector import DataCollector
from .preprocessor import DataPreprocessor
from .model import FilePredictionModel
from .trainer import ModelTrainer
from .prefetcher import FilePrefetcher
from .evaluator import PerformanceEvaluator

__all__ = [
    'DataCollector',
    'DataPreprocessor',
    'FilePredictionModel',
    'ModelTrainer',
    'FilePrefetcher',
    'PerformanceEvaluator'
]
EOF
