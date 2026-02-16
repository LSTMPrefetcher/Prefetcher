<#
build_exe.ps1 - Build a single-file Windows executable for this project using PyInstaller.

Usage: Run from the repository root in PowerShell:
  powershell -ExecutionPolicy Bypass -NoProfile -File .\build_exe.ps1

This script will install PyInstaller (if needed) and run it to create a one-file exe.
#>

Write-Host "Starting build: installing PyInstaller (if missing) and building exe..."

# Upgrade pip and install PyInstaller
python -m pip install --upgrade pip
python -m pip install pyinstaller

# Name the executable
$exeName = "ai-file-prefetcher"

# Build command: include project data folders so the exe can access config and data
python -m PyInstaller --noconfirm --onefile --name $exeName --add-data "config;config" --add-data "data;data" --add-data "scripts;scripts" main.py

Write-Host "Build finished. Check the 'dist' folder for the executable: dist\$exeName.exe"
