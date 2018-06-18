#!/bin/bash

# upload_rc.sh: This script manages the uploading of the register tests.
#
# Author: Nesta Lenhert-Scholer
# Credits: Chris Madrid
# Date Created: 06/18/2018
##############################################################################

########################
# Initialize Variables #
########################

run_num=$1
runDir=/home/django/testing_database_hb/media/uploads/run_control/run${run_num}_output/    # location of run control tests
scriptLoc=$(readlink -f $(dirname $0) )    # location of this script
logLoc=$scriptLoc/log_files    # location of log files
qcDir=$runDir/QC_run${run_num}    # location of Quality Control data

# Colors
STATUS="\e[1;34m"   # color of status statements
ACTION="\e[1;33m"   # color of action statements
SUCCESS="\e[1;92m"  # color of success statements
FAIL="\e[1;91m"     # color of failure statements
DEF="\e[39;0m"      # default colors of text


# remove old error logs
rm -f ${logLoc}/*.log

echo -e "${STATUS}Initial data set"
echo ""
################################
# Upload Quality Control Tests #
################################
echo -e "${STATUS}Uploading Quality Control Tests"

# Check for directories in the run number
if ls $qcDir &> /dev/null; then
    for dir in $qcDir/0x*; do
        echo $dir
    #echo -e "Data found"
    done
else
    echo -e "No data found"
fi
