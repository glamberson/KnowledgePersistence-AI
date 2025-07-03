#!/bin/bash

# NVIDIA Driver Installation Script for Debian 12
# RTX 4060 GPU Setup for Local LLM

echo "Installing NVIDIA drivers for RTX 4060..."

# Step 1: Add non-free repository
echo "Adding non-free repository..."
sudo sed -i 's/main non-free-firmware/main non-free-firmware non-free/g' /etc/apt/sources.list

# Step 2: Update package list
echo "Updating package list..."
sudo apt update

# Step 3: Install NVIDIA driver and CUDA toolkit
echo "Installing NVIDIA driver..."
sudo apt install -y nvidia-driver nvidia-cuda-toolkit

# Step 4: Install additional tools
echo "Installing additional GPU tools..."
sudo apt install -y nvidia-smi nvidia-settings

# Step 5: Reboot reminder
echo "Installation complete! System reboot is required."
echo "After reboot, run 'nvidia-smi' to verify the installation."
echo ""
echo "To reboot now, run: sudo reboot"