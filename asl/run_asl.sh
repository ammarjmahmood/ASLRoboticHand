#!/bin/bash

# Name of the virtual environment
VENV_NAME="temp_venv"

# Remove old venv if it exists
rm -rf $VENV_NAME

# Create new virtual environment
python3 -m venv $VENV_NAME

# Activate virtual environment
source $VENV_NAME/bin/activate

# Install required packages
pip install opencv-python mediapipe numpy

# Run the ASL detector
python asl.py

# Deactivate and clean up
deactivate
rm -rf $VENV_NAME