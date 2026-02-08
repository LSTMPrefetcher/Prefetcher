#!/bin/bash
echo "[*] Installing System Dependencies..."
sudo apt update
sudo apt install -y strace vmtouch python3-pip

echo "[*] Installing Python Libraries..."
pip3 install torch numpy pyyaml

echo "[*] Creating Directories..."
mkdir -p data/raw data/processed data/models
mkdir -p src config scripts

echo "[*] Setup Complete! You are ready to run main.py."
