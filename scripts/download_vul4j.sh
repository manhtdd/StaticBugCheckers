#!/bin/bash

# Author: Andrew Habib
# Created on: 31 August 2018

# NOTE: depending on which version is used, python/CheckoutD4j.py should be updated accordingly.
# as it now has the list of Defects projects identifiers and number of bugs encoded manually.

# Check if the script is not sourced from another script
[[ ! "${#BASH_SOURCE[@]}" -gt "1" ]] && { source ./scripts/config.sh; }

# # Clone the Defects4J repository quietly
# if [ -d ${D4J_ROOT} ]; then rm -rf ${D4J_ROOT}; fi
# echo ">>> Downloading the Defects4J framework <<<"
# git clone -q https://github.com/rjust/defects4j.git
# echo
# echo ">>> Initializing the framework"
# cd $D4J_ROOT && ./init.sh
# echo

echo ">>> Checking out and compiling the dataset"

# Run a Python script to check out buggy versions using Defects4J
python3 ${PY_SCRIPTS_ROOT}/CheckoutV4j.py
echo
