#!/bin/bash

# Check if the user provided a filename as an argument
if [ -z "$1" ]; then
  echo "Error: Please provide a filename as an argument for the Python script."
  exit 1
fi

# Store the filename in a variable
FILENAME="$1"

# Define the path to the Python file (one directory above)
PYTHON_FILE="../lexical_analyzer.py"

# Check if the Python file exists
if [ ! -f "$PYTHON_FILE" ]; then
  echo "Error: The Python file '$PYTHON_FILE' does not exist."
  exit 1
fi

# Run the Python file and pass the filename as an argument
python3 "$PYTHON_FILE" "$FILENAME"