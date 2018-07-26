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

#run_num=$1
uploads=/home/django/testing_database_hb/media/uploads
cardDir=$uploads/run_control/cards    # temporary location of the qie card qc data
#runDir=/home/django/testing_database_hb/media/uploads/run_control/run${run_num}_output    # location of run control tests
regCardDir=$uploads/temp_reg_test    # Where the qie card data for the register tests will be initially stored
scriptLoc=$(readlink -f $(dirname $0) )    # location of this script
logLoc=$scriptLoc/log_files    # location of log files
#qcDir=$cardDir    # location of Quality Control data

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

if [ "$1" -eq 3 ] || [ "$1" -eq 1 ]; then
################################
# Upload Quality Control Tests #
################################
    echo -e "${STATUS}Uploading Quality Control Tests"

    # Check if there are any cards to upload
    if ls $cardDir/0x* &> /dev/null; then
        for dir in $cardDir/0x*; do
            [ -d "${dir}" ] || continue
            qieuid="$(basename "${dir}")"    # list of uid directories
            echo -e "    ${ACTION}Processing Card with UID: ${DEF}${qieuid}"
            uidjsonFile=${dir}/${qieuid}_QC.json
            sleep 1s
            python $scriptLoc/upload_qc.py $uidjsonFile 2> $logLoc/${qieuid}_qc.log
            # Erase log files if there was no error
            if [ $? -eq 0 ]; then
                echo -e "    ${SUCCESS}Card Uploaded Successfully"
                rm $logLoc/${qieuid}_qc.log 
            else
                echo -e "    ${FAIL}ERROR: ${DEF} See log file: ${logLoc}/${qieuid}_qc.log"
            fi
        done
        echo -e "${STATUS}No More Cards to Upload. Check log file if there was an error.${DEF}"
    else
        echo -e "${FAIL}No Quality Control Data Found${DEF}"
    fi
    echo -e ""
fi

if [ "$1" -eq 3 ] || [ "$1" -eq 2 ]; then
#########################
# Upload Register Tests #
#########################

    echo -e "${STATUS}Uploading Register Tests${DEF}"

    if ls $regCardDir/0* &> /dev/null; then
        for dir in $regCardDir/0*; do
            [ -d "${dir}" ] || continue
            qieuid="$(basename "${dir}")"    # list of UID directories
            echo -e "    ${ACTION}Processing Card with UID: ${DEF}${qieuid}"
            regjsonFile=${dir}/results.json
            sleep 1s
            python $scriptLoc/upload_reg.py $regjsonFile 2> $logLoc/${qieuid}_reg.log
            # Erase log files if there was no error
            if [ $? -eq 0 ]; then
                echo -e "    ${SUCCESS}Card Uploaded Succesfully"
                rm $logLoc/${qieuid}_reg.log
            else
                echo -e "    ${FAIL}ERROR: ${DEF}See log file ${logLoc}/${qieuid}_reg.log"
            fi
        done
        echo -e "${STATUS}No More Cards to Upload. Check log file if there was an error.${DEF}"
    else
        echo -e "${FAIL}No Register Test Data Found${DEF}"
    fi
    echo -e ""
fi



