#!/bin/bash
# Create a new virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages from requirements.txt
pip install -r backend/requirements.txt
