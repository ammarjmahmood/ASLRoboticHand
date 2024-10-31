echo '#!/bin/bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt' > setup.sh

