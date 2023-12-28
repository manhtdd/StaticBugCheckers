#!/bin/bash

# Author: Andrew Habib
# Created on: 31 August 2018

# Check if the script is not sourced from another script
[[ ! "${#BASH_SOURCE[@]}" -gt "1" ]] && { source ./scripts/config.sh; }

# Print empty lines for better readability
echo
echo ">>> Analyze outputs <<<"

# Change to the STUDY_ROOT directory
cd ${STUDY_ROOT}

python3 ${PY_SCRIPTS_ROOT}/CountDetectedBugs.py \
    -ep_diffs_warnings ep_diffs_warnings.json \
    -inf_diffs_warnings inf_diffs_warnings.json \
    -sb_diffs_warnings sb_diffs_warnings.json \
    -ep_removed_warnings ep_removed_warnings.json \
    -inf_removed_warnings inf_removed_warnings.json \
    -sb_removed_warnings sb_removed_warnings.json
