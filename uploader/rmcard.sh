#!/bin/bash

# rmcard.sh - used to remove a card from the local machine and a database

# ONLY NESTA SHOULD USE THIS SCRIPT. IF ANYONE NEEDS TO USE IT, PLEASE CONTACT HIM
############################################################################################

# Colors
STATUS="\e[1;34m"   # color of status statements
ACTION="\e[1;33m"   # color of action statements
SUCCESS="\e[1;92m"  # color of success statements
FAIL="\e[1;91m"     # color of failure statements
DEF="\e[39;0m"      # default colors of text

########################
# Paths and variables  #
########################

SCRIPTPATH=$(readlink -f $(dirname $0) )    # Local directory where script is located
JSONPATH=$SCRIPTPATH/temp_json              # Where temporary json files are stored
CARDPATH=/home/django/testing_database_hb/media/uploads    # Where the QIE Card directories are located

# Get the barcode as the second argument
if [ $# -eq 0 ]; then
    echo -e "${FAIL}ERROR: ${DEF}Please enter barcode to be deleted."
    exit 1
else
    barcode=$1
fi

# Set paths to temp_json files and directory 
BARCODEJSONPATH=$JSONPATH/$barcode*.json
BARCODECARDPATH=$CARDPATH/$barcode

###################################
# Remove the temporary json files #
###################################

if find $BARCODEJSONPATH &> /dev/null; then
    rm -rf $BARCODEJSONPATH
    echo -e "${SUCCESS}JSON file(s) found and succesfully deleted"
else
    echo -e "${STATUS}Unable to locate json file for card ${barcode}"
fi

#######################################################
# Find and remove the directory for the specific card #
#######################################################

if find $BARCODECARDPATH &> /dev/null; then
    rm -rf $BARCODECARDPATH
    echo -e "${SUCCESS}Card directory found and succesfully deleted"
else
    echo -e "${STATUS}Unable to locate directory for card ${barcode}"
fi

######################################################
# Calling python script to delete card from database #
######################################################
