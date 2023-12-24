#!/bin/bash

# Author: Andrew Habib
# Created on: 31 August 2018

source ./scripts/config.sh

echo
echo "**********************************************************************************************"
echo "Running the study of static bug checkers and their effectiveness by Habib and Pradel [ASE2018]"
echo "**********************************************************************************************"

bash ./scripts/download_static_checkers.sh

bash ./scripts/download_defects4j.sh

echo
echo "*************************"
echo "Done performing the setup"
echo "*************************"
