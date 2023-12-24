#!/bin/bash

# Author: Andrew Habib
# Created on: 31 August 2018

# Check if the script is not sourced from another script
[[ ! "${#BASH_SOURCE[@]}" -gt "1" ]] && { source ./scripts/config.sh; }

echo
echo ">>> Parsing and serializing output from the static checkers <<<"

# Change to the OUT_BUGGY directory
cd $OUT_BUGGY

# Parse and serialize output from Error Prone on buggy versions
python3 ${PY_SCRIPTS_ROOT}/ParseAndSerializeErrorprone.py ep_output/
# Parse and serialize output from Infer on buggy versions
python3 ${PY_SCRIPTS_ROOT}/ParseAndSerializeInfer.py inf_output_json/
# Parse and serialize output from SpotBugs on buggy versions
python3 ${PY_SCRIPTS_ROOT}/ParseAndSerializeSpotbugs.py sb_output/

# Change to the OUT_FIXED directory
cd $OUT_FIXED

# Parse and serialize output from Error Prone on fixed versions
python3 ${PY_SCRIPTS_ROOT}/ParseAndSerializeErrorprone.py ep_output/
# Parse and serialize output from Infer on fixed versions
python3 ${PY_SCRIPTS_ROOT}/ParseAndSerializeInfer.py inf_output_json/
# Parse and serialize output from SpotBugs on fixed versions
python3 ${PY_SCRIPTS_ROOT}/ParseAndSerializeSpotbugs.py sb_output/
