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
runDir=/home/django/testing_database_hb/media/uploads/run_control/run${run_num}_output    # location of run control tests
scriptLoc=$(readlink -f $(dirname $0) )    # location of this script
logLoc=$scriptLoc/log_files/    # location of log files
qcDir=$runDir/QC_run${run_num}    # location of Quality Control data

# Colors
STATUS="\e[1;34m"   # color of status statements
ACTION="\e[1;33m"   # color of action statements
SUCCESS="\e[1;92m"  # color of success statements
FAIL="\e[1;91m"     # color of failure statements
DEF="\e[39;0m"      # default colors of text


# remove old error logs
rm -f ${logLoc}*.log

echo -e "${STATUS}Initial data set"
echo ""

################################
# Upload Quality Control Tests #
################################
echo -e "${STATUS}Uploading Quality Control Tests"

# Check for directories in the run number
if ls $qcDir &> /dev/null; then
    for dir in $qcDir/0x*; do
        [ -d "${dir}" ] || continue
        qieuid="$(basename "${dir}")"    # list of uid directories
        echo -e "    ${ACTION}Processing Card with UID: ${DEF}${qieuid}"
        uidjsonFile=${dir}/${qieuid}_QC.json
        python $scriptLoc/upload_qc.py $uidjsonFile $run_num #2> $logLoc${qieuid}.log 1> $logLoc${qieuid}.txt    # call python script
       #for barcode in $logLoc*.txt; do
       ## move files to their associated barcode directories
       #done
    done
else
    echo -e "${FAIL}No Quality Control Data Found${DEF}"
fi
