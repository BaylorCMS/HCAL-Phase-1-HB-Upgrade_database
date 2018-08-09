#!/bin/bash

# step12.sh: This script manages the upload of Test Stand 1 json files.
#
# Author:   Andrew Baas
# Credits:  Shaun Hogan, Mason Dorseth, John Lawrence, Jordan Potarf,
#                Andrew Baas
# 
# Version:  1.02
# Maintainer:   Caleb Smith
# Email:    caleb_smith2@baylor.edu
# Status:   Live

###################################################
#               Set Initial Data                  #
###################################################

osOption=$1
stepNumber=$2

if [[ $osOption = "-w" ]]; then 
    colors=false
else
    colors=true
fi


if $colors ; then
    echo -e "\e[1;34mSetting initial data"
else
    echo -e "Setting initial data"
fi

# local locations
scriptLoc=$(readlink -f $(dirname $0) ) # location of this script
jsonStore=$scriptLoc/temp_json          # location of json files
logLoc=$scriptLoc/log_files             # location of error logs
hrLogLoc=$scriptLoc/../media/human_readable_logs    # location of HR logs
uhtrLoc=$scriptLoc/uhtr_results         # location of uhtr plots

if $colors ; then
    STATUS="\e[1;34m"   # color of status statements
    ACTION="\e[1;33m"   # color of action statements
    SUCCESS="\e[1;92m"  # color of success statements
    FAIL="\e[1;91m"     # color of failure statements
    DEF="\e[39;0m"      # default colors of text
else
    STATUS=
    ACTION=
    SUCCESS=
    FAIL=
    DEF=
fi    
# remove old error logs
rm -f $logLoc/*.log

echo -e "${STATUS}Initial data set"
echo ""

echo "script location: $scriptLoc"
echo "json location: $jsonStore"
echo "json files: $(ls $jsonStore/*.json)"

###########################################################
#           Register Tests for Steps 1, 2, 3              #
###########################################################
#for i in `seq 1 3`;
#do
# no longer loop over steps 1,2,3; now only upload specified step
i=$stepNumber
jsonTag="step"$i"_raw.json" # quotes for "$i" are required
script="step$i.py"
echo -e "${STATUS}Uploading step $i tests"

echo "json files for step $i: $(ls $jsonStore/*$jsonTag)"

# detemine if there are step$i_raw.json files
if ls $jsonStore/*$jsonTag &> /dev/null
then
    # upload each step$i_raw.json file to the database
    fileList=$(ls $jsonStore/*$jsonTag)   # list of step$i_raw.json
    for file in $fileList
    do
        echo -e "    ${ACTION}Processing${DEF} $(basename $file)"
        python $scriptLoc/$script $file 2> $file.log
        

        if [ $? -eq 0 ]
        then
            echo -e "      ${SUCCESS}Success"
            rm $file*
        else
            echo -e "      ${FAIL}ERROR${DEF} (see $(basename $file).log)"
            error_log=$( cat $file.log )
            echo -e "      ${FAIL}${error_log}${DEF}"
        fi
    done
else
    echo -e "    ${SUCCESS}No step $i tests to upload"
fi

echo -e "${STATUS}New step $i tests uploaded"
echo ""


# Move log files to proper folder
mv $jsonStore/*.log $logLoc 2> /dev/null

echo -e "${STATUS}Finished${DEF}"

