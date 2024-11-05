# Robotic ASL Arm

## Setup Instructions

### Ubuntu Linux:
1. Open terminal and install Python if not already installed:
```bash
sudo apt update
sudo apt install python3-venv python3-pip
```

2. Clone and setup:
```bash
git clone https://github.com/ammarjmahmood/robotic-asl-arm.git
cd robotic-asl-arm
./setup.sh
```

### macOS:
1. Install Homebrew if not already installed:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install Python:
```bash
brew install python
```

3. Clone and setup:
```bash
git clone https://github.com/ammarjmahmood/robotic-asl-arm.git
cd robotic-asl-arm
chmod +x setup.sh  # Make script executable
./setup.sh
```

### Windows (WSL):
1. Install WSL if not already installed. Open PowerShell as Administrator and run:
```powershell
wsl --install
```
Restart your computer after installation.

2. Open Ubuntu WSL terminal and install Python:
```bash
sudo apt update
sudo apt install python3-venv python3-pip
```

3. Clone and setup:
```bash
git clone https://github.com/ammarjmahmood/robotic-asl-arm.git
cd robotic-asl-arm
chmod +x setup.sh
./setup.sh
```

## Manual Setup (All Platforms)
If the automated setup doesn't work:

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
- Ubuntu/macOS/WSL: `source venv/bin/activate`
- Windows Command Prompt: `venv\Scripts\activate`
- Windows PowerShell: `.\venv\Scripts\Activate.ps1`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Project
After setup is complete:

1. Ensure virtual environment is activated:
```bash
source venv/bin/activate  # on Ubuntu/macOS/WSL
```

2. Run the main script:
```bash
python asl/asl.py
```

## Troubleshooting

If you encounter permission issues with setup.sh:
```bash
chmod +x setup.sh  # Make script executable
```

If you see "command not found python":
```bash
# Ubuntu/WSL
sudo apt install python3

# macOS
brew install python

# Windows
# Download Python installer from python.org
```

## Note
- Make sure you have Git installed on your system before starting
- Python 3.8 or higher is recommended
- If you encounter any issues, please open an issue on GitHub
