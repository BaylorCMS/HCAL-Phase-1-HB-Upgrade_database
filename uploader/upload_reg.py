"""
upload_reg.py:
    This script takes a json file location as an argument and processes the data to upload
    into the database. This script will be used to upload the data from the register tests. 
"""

__author__ = "Nesta Lenhert-Scholer"

import os
import sys
import json
import django
import shutil
from datetime import datetime
from card_stats import set_card_status

sys.path.insert(0, '/home/django/testing_database_hb/card_db')
django.setup()

from qie_cards.models import QieCard, Attempt, Channel, Test, Variable, Tester, Run
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from card_db.settings import MEDIA_ROOT
from django.db import transaction


CHANNEL_MAPPING= {"Top": {"0": 1, "1": 2, "2": 3, "3": 4, "4": 5, "5": 6, "6": 7, "7": 8},
                  "Bot": {"0": 9, "1": 10, "2": 11, "3": 12, "4": 13, "5": 14, "6": 15, "7": 16}}


def getUID(uid):
    """Gets the Unique ID to be used in finding the associated card"""
    
    split_id = uid.split("_")
    uniqueid = split_id[0][2:] + split_id[1][2:]
    while len(uniqueid) < 16:
        uniqueid = "0" + uniqueid

    return uniqueid.lower()


def makeOutputPath(uID, destination):
    path = os.path.join(destination, uID + "_REG")
    if os.path.exists(path):
        extension = 2
        while os.path.exists(destination + "/{0}_REG_v{1}".format(uID, extension)):
            extension += 1
        path = os.path.join(destination, "{0}_REG_v{1}".format(uID, extension))
    return path


@transaction.atomic
def uploadAttempt(attemptlist, json_file, cmd_file, run_file):    #, chan_passed, chan_failed):
    """This functions saves info in the attempt at saves it in the database"""
    for attempt in attemptlist:
        attempt.log_file = cmd_file
        attempt.hidden_log_file = json_file
        attempt.image = run_file
      #  attempt.num_channels_passed = chan_passed[test]
      #  attempt.num_channels_failed = chan_failed[test]
      #  attempt.result = bool(chan_failed[test] == 0)
        attempt.save()
    

@transaction.atomic
def getData(data, qiecard, tester_name, comments):
    """Main function to grab data from the JSON file"""
    attemptlist = []

    for test in data.keys():
        try:
            # Test is in the database
            temp_test = Test.objects.get(abbreviation=test)
        except:
            # Test is NOT in the database
            temp_test = Test(name=test, abbreviation=test)
            temp_test.save()
        
        prev_attempts = list(Attempt.objects.filter(card=qiecard, test_type=temp_test))
        attempt_num = len(prev_attempts) + 1
      #  if str(data[test]) == "true":
        temp_attempt = Attempt(card=qiecard,
                               date_tested=timezone.now(),
                               plane_loc="default",
                               attempt_number=attempt_num,
                               test_type=temp_test,
                               result=data[test][0],
                               times_passed=data[test][1],
                               times_failed=data[test][2],
                               # run=run_num,
                               tester=Tester.objects.get(username=tester_name),
                               comments=comments)

      #  else:
      #      temp_attempt = Attempt(card=qiecard,
      #                             date_tested=timezone.now(),
      #                             plane_loc="default",
      #                             attempt_number=attempt_num,
      #                             test_type=temp_test,
      #                             result=0,
      #                             # run=run_num,
      #                             tester=Tester.objects.get(username="hcaldaq"),
      #                             comments=comments) 
        temp_attempt.save()
        attemptlist.append(temp_attempt)

        for pa in prev_attempts:
            pa.revoked=True
            pa.save()
    
            
    return attemptlist

# load the json file
file_name = sys.argv[1]

#run_num = sys.argv[2]
# open the file and read it
try:
    inFile = open(file_name, "r")
except IOError:
    sys.exit("File not able to be found. Make sure there is a JSON file in the directory")

try:
    data = json.load(inFile)
except:
    sys.exit("Unable to load file. Make sure the file is formatted correctly as a JSON file.")

# Get card with given Unique ID
try:
    rawUID = data["uID"]    # UID as stored in the JSON file
    cardUID = getUID(data["uID"])    # UID as stored in the database
    qiecard = QieCard.objects.get(uid__contains=cardUID)    # Get the card with this specific UID
    del data["uID"]    # Remove the uID so only the data is left in the dictionary
except ObjectDoesNotExist:
    sys.exit("UID does not match a QIE Card in the database. Check that the UID is correct or that the QIE Card is in the database.")

# Get the run number
# run_num = data["RunNum"]
tester_name = data["Tester_Name"]
comments = data["Comments"]

if comments != "":
    comment = ""
    if not qiecard.comments == "":
        comment += "\n"
    comment += str(timezone.now().date()) + " " + str(timezone.now().hour) + "." + str(timezone.now().minute) + ": "
    comment += data["Comments"]
    qiecard.comments = comment
    qiecard.save()
del data["Tester_Name"]
del data["Comments"]

################
# Get the data #
################

attemptlist = getData(data, qiecard, tester_name, comments)


# If this is a new run, create a new run
#run_list = list(Run.objects.all())
#num_list = []
#for r in run_list:
#    num_list.append(r.number)
#
#if run_num not in num_list:
#    new_run = Run(number=run_num)
#    new_run.save()
#
###########################################
# Move the directory to permanent storage #
###########################################
#run = "run" + str(run_num)    # ex: run350
uploads = os.path.join(MEDIA_ROOT, "uploads/")    # path to the uploads directory
card_dir = os.path.join(uploads, "qieCards/")    # path to the qie cards
temp_card_dir = os.path.join(uploads, "temp_reg_test/")    # path to where the just installed cards are

destination = os.path.join(card_dir, qiecard.barcode)    # path to the destination directory i.e. 0700001/

#source_dir = os.path.join(run_control, (run + "_output/QC_" + run + "/"))    # temp directory for all the uploaded qie cards

new_dir_name = os.path.basename(makeOutputPath(rawUID, destination))    # permanent storage for qie card data. i.e media/uploads/0700001/0x1111111_0x1234567_v2 if this is the second upload

#new_dir_name = rawUID + "_QC_" + run    # what the new directories will be called i.e. 0x11111111_0x2124124124_QC_run350

old_src_name = os.path.join(temp_card_dir, rawUID)    # where the temporary storage is for the UID directories
new_src_name = os.path.join(temp_card_dir, new_dir_name)    # where the permanent storage will be for the UID directories

file_name = os.path.basename(file_name) # only grab the basename from the full path for the JSON file

# Rename the UID Directory name
os.renames(old_src_name, new_src_name)

# Move UID Directory to its permanent storage
shutil.move(new_src_name, destination)

mved_src_name = os.path.join(destination, new_dir_name)

new_file_name = os.path.join(mved_src_name, file_name)

#media = os.path.join("uploads/qieCards/", qiecard.barcode, os.path.basename(mved_src_name))
json_file = os.path.join("uploads/qieCards/", qiecard.barcode, os.path.basename(mved_src_name), file_name)
cmd_file = os.path.join("uploads/qieCards/", qiecard.barcode, os.path.basename(mved_src_name), "cmd.log")
run_file = os.path.join("uploads/qieCards/", qiecard.barcode, os.path.basename(mved_src_name), "run.log")

uploadAttempt(attemptlist, json_file, cmd_file, run_file)    #, channels_passed, channels_failed)

set_card_status(qiecard)

