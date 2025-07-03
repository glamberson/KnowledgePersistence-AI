#!/bin/bash

# Ollama LLM Installation Script for Local GPU-Accelerated LLM
# After NVIDIA drivers are installed

echo "Installing Ollama for local LLM deployment..."

# Step 1: Install Ollama
echo "Downloading and installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Step 2: Start Ollama service
echo "Starting Ollama service..."
sudo systemctl enable ollama
sudo systemctl start ollama

# Step 3: Install a small test model
echo "Installing a test model (llama3.2:1b)..."
ollama pull llama3.2:1b

# Step 4: Test installation
echo "Testing Ollama installation..."
ollama list

echo ""
echo "Ollama installation complete!"
echo "To run a model: ollama run llama3.2:1b"
echo "To install larger models: ollama pull llama3.2:8b"
echo "To see available models: ollama list"
echo ""
echo "GPU acceleration will be automatically used if NVIDIA drivers are properly installed."