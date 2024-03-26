#!/bin/bash

# Check if the script is not sourced from another script
# If not sourced, source the config.sh file
[[ ! "${#BASH_SOURCE[@]}" -gt "1" ]] && { source ./scripts/config.sh; }

# Set versions for ErrorProne, Infer, and SpotBugs
EP_VER="2.3.1"
INF_VER="1.1.0"
SB_VER="4.8.2"

# Set URLs for downloading ErrorProne, Infer, and SpotBugs
EP_URL="https://repo1.maven.org/maven2/com/google/errorprone/error_prone_ant/${EP_VER}/error_prone_ant-${EP_VER}.jar"
SB_URL="https://github.com/spotbugs/spotbugs/releases/download/$SB_VER/spotbugs-$SB_VER.tgz"
INF_URL="https://github.com/facebook/infer/releases/download/v${INF_VER}/infer-linux64-v${INF_VER}.tar.xz"

# Remove existing checkers directory if it exists
if [ -d ${CHECKERS_ROOT} ]; then rm -rf ${CHECKERS_ROOT}; fi

# Create a new checkers directory
mkdir $CHECKERS_ROOT

echo ">>> Downloading and extracting static checkers <<<"

# Download ErrorProne JAR file and place it in the checkers directory
# echo ">>> Preparing Google's ErrorProne"
# cd $CHECKERS_ROOT
# wget -q $EP_URL

# Download and extract Infer to the checkers directory
echo ">>> Preparing Facebook's Infer"
curl -sSL $INF_URL | tar -C $CHECKERS_ROOT -xJ

# Download and extract SpotBugs to the checkers directory
# echo ">>> Preparing SpotBugs"
# cd $CHECKERS_ROOT
# curl -O -L $SB_URL
# tar -xzvf spotbugs-$SB_VER.tgz
# rm -rf spotbugs-$SB_VER.tgz
