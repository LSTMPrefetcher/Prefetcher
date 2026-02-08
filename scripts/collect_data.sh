#!/bin/bash
# Runs the collector multiple times to build a larger dataset
ITERATIONS=5

echo "Starting Batch Data Collection ($ITERATIONS runs)..."

for i in $(seq 1 $ITERATIONS)
do
   echo "Run $i/$ITERATIONS"
   python3 main.py collect
   sleep 2 # Cooldown
done

echo "Batch collection finished."
