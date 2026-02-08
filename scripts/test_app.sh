cat > scripts/test_app.sh << 'EOF'
#!/bin/bash
# Test application launch times

if [ "$#" -lt 1 ]; then
    echo "Usage: ./test_app.sh <app_name> [iterations]"
    echo "Example: ./test_app.sh firefox 10"
    exit 1
fi

APP_NAME=$1
ITERATIONS=${2:-5}

echo "=========================================="
echo "Application Launch Time Testing"
echo "=========================================="
echo "Application: $APP_NAME"
echo "Test iterations: $ITERATIONS"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Function to clear cache
clear_cache() {
    echo "Clearing system cache..."
    sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
    sleep 2
}

# Function to measure launch time
measure_launch() {
    local app_command=$1
    local start_time=$(date +%s.%N)
    
    # Launch application
    $app_command &> /dev/null &
    local pid=$!
    
    # Wait for app to start
    sleep 5
    
    # Kill application
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
    
    local end_time=$(date +%s.%N)
    local elapsed=$(echo "$end_time - $start_time" | bc)
    
    echo $elapsed
}

# Get app command from config
APP_COMMAND=$(grep -A 1 "^  $APP_NAME:" config/config.yaml | grep "command:" | cut -d'"' -f2)

if [ -z "$APP_COMMAND" ]; then
    echo "Error: Application $APP_NAME not found in config.yaml"
    exit 1
fi

echo "Testing application: $APP_COMMAND"
echo ""

# Array to store times
declare -a times

echo "Running tests..."
for i in $(seq 1 $ITERATIONS); do
    echo -n "[Test $i/$ITERATIONS] "
    
    # Clear cache before each test
    clear_cache > /dev/null 2>&1
    
    # Measure launch time
    launch_time=$(measure_launch "$APP_COMMAND")
    times+=($launch_time)
    
    printf "Launch time: %.2f seconds\n" $launch_time
    
    sleep 2
done

echo ""
echo "=========================================="
echo "Test Results"
echo "=========================================="

# Calculate average
total=0
for time in "${times[@]}"; do
    total=$(echo "$total + $time" | bc)
done
average=$(echo "scale=2; $total / $ITERATIONS" | bc)

# Find min and max
min=${times[0]}
max=${times[0]}
for time in "${times[@]}"; do
    if (( $(echo "$time < $min" | bc -l) )); then
        min=$time
    fi
    if (( $(echo "$time > $max" | bc -l) )); then
        max=$time
    fi
done

printf "Average: %.2f seconds\n" $average
printf "Minimum: %.2f seconds\n" $min
printf "Maximum: %.2f seconds\n" $max
echo "=========================================="
EOF

chmod +x scripts/test_app.sh
