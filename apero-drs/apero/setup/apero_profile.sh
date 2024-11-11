#!/bin/bash

# Set the path to profiles.ini
PROFILE_FILE="$HOME/.apero/profiles.ini"

# Check if profile name is provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <profile_name>"
  exit 1
fi


# Check if profiles.ini exists
if [ ! -f "$PROFILE_FILE" ]; then
  echo "Error: $PROFILE_FILE file not found. Please run apero_setup.py"
  exit 1
fi

# Read profiles.ini and find the path for the provided profile
PROFILE_PATH=$(grep "^$1=" $PROFILE_FILE | cut -d'=' -f2)

# Check if profile path exists
if [ -z "$PROFILE_PATH" ]; then
  echo "Profile $1 not found in $PROFILE_FILE."
  echo ""
  echo "Available profiles are:"
  grep -o '^[^=]*' $PROFILE_FILE
  echo "Or run apero_setup.py to create a new profile"
  exit 1
fi

# Determine the setup script to run based on OS
SETUP_SCRIPT=""
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
  SETUP_SCRIPT="${PROFILE_PATH}/setup.sh"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
  SETUP_SCRIPT="${PROFILE_PATH}/setup.bat"
else
  echo "Unsupported OS type: $OSTYPE"
  exit 1
fi

# Run the setup script if it exists
if [ -f "$SETUP_SCRIPT" ]; then
  bash "$SETUP_SCRIPT"
else
  echo "Setup script not found: $SETUP_SCRIPT"
  exit 1
fi