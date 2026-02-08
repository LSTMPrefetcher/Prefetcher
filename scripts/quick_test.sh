cat > scripts/quick_test.sh << 'EOF'
#!/bin/bash
# Quick test script - runs everything with minimal iterations

APP_NAME=${1:-gedit}
RUNS=${2:-5}

echo "=========================================="
echo "Quick Test Script"
echo "=========================================="
echo "Application: $APP_NAME"
echo "Data collection runs: $RUNS"
echo ""
echo "This will run the complete pipeline with minimal iterations"
echo "for quick testing purposes."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Activate venv
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

# Run pipeline
python main.py pipeline --app "$APP_NAME" --runs "$RUNS"

echo ""
echo "=========================================="
echo "Quick test complete!"
echo "=========================================="
echo ""
echo "Check results in:"
echo "  • Raw data: data/raw/"
echo "  • Processed data: data/processed/"
echo "  • Trained model: data/models/${APP_NAME}_model.h5"
echo ""
EOF

chmod +x scripts/quick_test.sh
