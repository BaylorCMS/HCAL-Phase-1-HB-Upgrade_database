scriptLoc=$(readlink -f $(dirname $0) )    # Current location of this script
tempDir=$scriptLoc/temp    # Location of the temp directory
logs=$scriptLoc/error_logs    # Location of the error log files

# Setting status colors
STATUS="\e[1;34m"   # color of status statements
ACTION="\e[1;33m"   # color of action statements
SUCCESS="\e[1;92m"  # color of success statements
FAIL="\e[1;91m"     # color of failure statements
DEF="\e[39;0m"      # default colors of text

rm -f ${logs}/*.log

echo -e "${STATUS}Initial data set"
echo ""
echo -e "${STATUS}Uploading Calibration Data${DEF}"

# Check that there are cards to be uploaded
if ls $tempDir/Card_* &> /dev/null; then
    for card in $tempDir/Card_*; do
        # Check that these are directories
        [ -d "${card}" ] || continue
        qieuid="$(basename "${card}")"
        qieuid=${qieuid:5}    # Only grab the unique id with no "Card_"
        echo -e "    ${ACTION}Processing Card with UID: ${DEF}${qieuid}"
        jsonFile=${card}/${qieuid}.json
        python $scriptLoc/calibration_uploader.py ${jsonFile} ${qieuid} 2> $logs/${qieuid}_cal.log

        # Erase log files if there was no error
        if [ $? -eq 0 ]; then
            echo -e "    ${SUCCESS}Card Uploaded Successfully"
            rm $logs/${qieuid}_cal.log
        else
            echo -e "    ${FAIL}ERROR: ${DEF}See log file: ${logs}/${qieuid}_cal.log"
        fi
    done
    echo -e "${STATUS}No More Cards to Upload. Check log file if there was an error.${DEF}"
else
    echo -e "${FAIL}No Calibration Data Found${DEF}"
fi

