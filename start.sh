#!/bin/bash

# Check if model exists, if not download it
if [ ! -f "models/checkpoint.pth" ]; then
    echo "Model not found. Downloading..."
    python -c "
import gdown
import os
os.makedirs('models', exist_ok=True)
gdown.download('https://drive.google.com/uc?id=1VaB9qmln89nWr74fhceatvvaTqUQMgqU', 'models/checkpoint.pth', quiet=False)
"
fi

# Start the application
exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --log-level debug app:app 