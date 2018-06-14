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
echo -e "\e[1;34mSetting initial data"

# local locations
scriptLoc=$(readlink -f $(dirname $0) ) # location of this script
jsonStore=$scriptLoc/temp_json          # location of json files
logLoc=$scriptLoc/log_files             # location of error logs
hrLogLoc=$scriptLoc/../media/human_readable_logs    # location of HR logs
uhtrLoc=$scriptLoc/uhtr_results         # location of uhtr plots

STATUS="\e[1;34m"   # color of status statements
ACTION="\e[1;33m"   # color of action statements
SUCCESS="\e[1;92m"  # color of success statements
FAIL="\e[1;91m"     # color of failure statements
DEF="\e[39;0m"      # default colors of text

# remove old error logs
rm -f $logLoc/*.log

echo -e "${STATUS}Initial data set"
echo ""
###################################################
#           Register Step 1 Tests                 #
###################################################
echo -e "${STATUS}Uploading step 1 tests"

# detemine if there are step1_raw.json files
if ls $jsonStore/*step1_raw.json &> /dev/null
then
    # upload each step1_raw.json file to the database
    fileList=$(ls $jsonStore/*step1_raw.json)   # list of step1_raw.json
    for file in $fileList
    do
        echo -e "    ${ACTION}Processing${DEF} $(basename $file)"
        python $scriptLoc/step1.py $file 2> $file.log
        

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
    echo -e "    ${SUCCESS}No step 1 tests to upload"
fi

echo -e "${STATUS}New step 1 tests uploaded"
echo ""
###################################################
#           Register Step 2 Tests                 #
###################################################
echo -e "${STATUS}Uploading step 2 tests"

# detemine if there are step2_raw.json files
if ls $jsonStore/*step2_raw.json &> /dev/null
then
    # upload each step2_raw.json file to the database
    fileList=$(ls $jsonStore/*step2_raw.json)   # list of step2_raw.json
    for file in $fileList
    do
        echo -e "    ${ACTION}Processing${DEF} $(basename $file)"
        python $scriptLoc/step2.py $file 2> $file.log

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
    echo -e "    ${SUCCESS}No step 2 tests to upload"
fi

echo -e "${STATUS}New step 2 tests uploaded"
echo ""


# Move log files to proper folder
mv $jsonStore/*.log $logLoc 2> /dev/null

echo -e "${STATUS}Finished${DEF}"

