#!/bin/bash

# Author: Andrew Habib
# Created on: 31 August 2018

# Check if the script is not sourced from another script
[[ ! "${#BASH_SOURCE[@]}" -gt "1" ]] && { source ./scripts/config.sh; }

# Function to get the absolute path of a file or directory
get_abs_path() {
    readlink -f $1
}

# Get the absolute paths of Infer, Error Prone, and SpotBugs binaries
INF_BIN="$(get_abs_path `find ${CHECKERS_ROOT} -maxdepth 1 -type d -name infer-linux*`)/bin/infer"
EP_BIN=$(get_abs_path `find ${CHECKERS_ROOT} -name error_prone*.jar`)
SB_BIN="$(get_abs_path `find ${CHECKERS_ROOT} -maxdepth 1 -type d -name spotbugs*`)/lib/spotbugs.jar"

# If STUDY_ROOT directory exists, remove it and recreate it
if [ -d ${STUDY_ROOT} ]; then rm -rf ${STUDY_ROOT}; fi
mkdir -p $OUT_BUGGY && mkdir -p $OUT_FIXED

echo ">>> Running the static checkers on the buggy versions from the Defects4j <<<"
cd $OUT_BUGGY

# Run Error Prone on buggy versions
echo ">>> Running Error Prone" && python3 ${PY_SCRIPTS_ROOT}/RunErrorprone.py ${EP_BIN} ${D4J_BUGGY}
echo ">>> Done"
# Run Infer on buggy versions
echo ">>> Running Infer" && python3 ${PY_SCRIPTS_ROOT}/RunInfer.py ${INF_BIN} ${D4J_BUGGY}
echo ">>> Done"
# Run SpotBugs on buggy versions
echo ">>> Running SpotBugs" && python3 ${PY_SCRIPTS_ROOT}/RunSpotbugs.py ${SB_BIN} ${D4J_BUGGY}
echo ">>> Done"

echo
echo ">>> Running the static checkers on the fixed versions from the Defects4j <<<"
cd $OUT_FIXED

# Run Error Prone on fixed versions
echo ">>> Running Error Prone" && python3 ${PY_SCRIPTS_ROOT}/RunErrorprone.py ${EP_BIN} ${D4J_FIXED}
echo ">>> Done"
# Run Infer on fixed versions
echo ">>> Running Infer" && python3 ${PY_SCRIPTS_ROOT}/RunInfer.py ${INF_BIN} ${D4J_FIXED}
echo ">>> Done"
# Run SpotBugs on fixed versions
echo ">>> Running SpotBugs" && python3 ${PY_SCRIPTS_ROOT}/RunSpotbugs.py ${SB_BIN} ${D4J_FIXED}
echo ">>> Done"
