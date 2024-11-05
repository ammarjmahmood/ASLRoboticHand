#!/bin/bash

# Update system packages
sudo apt-get update
sudo apt-get install -y \
    libgl1-mesa-glx \
    libarchive13 \
    wget \
    bzip2 \
    ca-certificates \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1

# Download and install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
rm ~/miniconda.sh

# Initialize conda for bash
eval "$($HOME/miniconda/bin/conda shell.bash hook)"

# Add conda to PATH
echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Configure conda
conda config --set auto_activate_base true
conda config --add channels defaults
conda config --set solver classic

# Create conda environment
conda create -y -n asl-env python=3.12

# Activate environment
conda activate asl-env

# Install required packages
conda install -y -c conda-forge opencv
pip install -r requirements.txt

# Add user to video group for camera access
sudo usermod -a -G video $USER

echo "Setup completed! Please log out and log back in for camera permissions to take effect."