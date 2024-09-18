if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Python is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install python3
fi

if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "pip is not installed. Installing..."
    sudo apt-get install python3-pip
fi

echo "Installing required Python packages..."
pip3 install -r requirements.txt

clear && echo "Running main.py..."
python3 main.py