#!/bin/bash

# Author: Andrew Habib
# Created on: 31 August 2018

# Check if the script is not sourced from another script
[[ ! "${#BASH_SOURCE[@]}" -gt "1" ]] && { source ./scripts/config.sh; }

# Print empty lines for better readability
echo
echo ">>> Executing the Removed warnings-based methodology: find removed (a.k.a disappeared) warnings <<<"

# Change to the STUDY_ROOT directory
cd ${STUDY_ROOT}

# Compare warnings between buggy and fixed versions for Error Prone using a Python script
python3 ${PY_SCRIPTS_ROOT}/CompareBugToFixErrorprone.py ${OUT_BUGGY}/ep_parsed.json ${OUT_FIXED}/ep_parsed.json

# Compare warnings between buggy and fixed versions for Infer using a Python script
python3 ${PY_SCRIPTS_ROOT}/CompareBugToFixInfer.py ${OUT_BUGGY}/inf_parsed.json ${OUT_FIXED}/inf_parsed.json

# Compare warnings between buggy and fixed versions for SpotBugs using a Python script
python3 ${PY_SCRIPTS_ROOT}/CompareBugToFixSpotbugs.py ${OUT_BUGGY}/sb_parsed.json ${OUT_FIXED}/sb_parsed.json
