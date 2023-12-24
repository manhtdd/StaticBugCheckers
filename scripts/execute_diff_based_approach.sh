#!/bin/bash

# Author: Andrew Habib
# Created on: 31 August 2018

# Check if the script is not sourced from another script
[[ ! "${#BASH_SOURCE[@]}" -gt "1" ]] && { source ./scripts/config.sh; }

echo
echo ">>> Computing diffs between buggy and fixed versions in the Defects4j <<<"

# Change to the STUDY_ROOT directory
cd ${STUDY_ROOT}

# Compute and serialize the differences between buggy and fixed versions using a Python script
python3 ${PY_SCRIPTS_ROOT}/ExtractAndSerializeDiffs.py $D4J_BUGGY $D4J_FIXED
echo
echo ">>> Executing the Diff-based methodology: intersect diffs with flagged lines <<<"

# Change to the STUDY_ROOT directory
cd ${STUDY_ROOT}

# Compare diffs to Error Prone parsed output
python3 ${PY_SCRIPTS_ROOT}/CompareDiffsToErrorprone.py $DIFFS_FILE ${OUT_BUGGY}/ep_parsed.json

# Compare diffs to Infer parsed output
python3 ${PY_SCRIPTS_ROOT}/CompareDiffsToInfer.py $DIFFS_FILE ${OUT_BUGGY}/inf_parsed.json

# Compare diffs to SpotBugs parsed output
python3 ${PY_SCRIPTS_ROOT}/CompareDiffsToSpotbugs.py $DIFFS_FILE ${OUT_BUGGY}/sb_parsed.json
