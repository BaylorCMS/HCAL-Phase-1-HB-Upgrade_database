"""
upload_qc.py:
    This script takes a json file location as an argument and processes the data to upload
    into the database. This script will be used to upload the data from the quality control 
    testing.
"""

__author__ = "Nesta Lenhert-Scholer"

import os
import sys
import json
import django
import shutil
from datetime import datetime

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
    uniqueid = uid[2:10] + uid[13:]
    carduid=str(uniqueid)
    return carduid.lower()


def makeOutputPath(uID, destination):
    path = os.path.join(destination, uID + "_QC")
    if os.path.exists(path):
        extension = 2
        while os.path.exists(destination + "/{0}_QC_v{1}".format(uID, extension)):
            extension += 1
        path = os.path.join(destination, "{0}_QC_v{1}".format(uID, extension))
    return path


@transaction.atomic
def uploadAttempt(attemptdict, json_file, media, chan_passed, chan_failed):
    """This functions saves info in the attempt at saves it in the database"""
    for test in attemptdict.keys():
        attemptdict[test].log_file = json_file
        attemptdict[test].hidden_log_file = json_file
        attemptdict[test].image = os.path.join(media, str(test))
        attemptdict[test].num_channels_passed = chan_passed[test]
        attemptdict[test].num_channels_failed = chan_failed[test]
        attemptdict[test].result = bool(chan_failed[test] == 0)
        attemptdict[test].save()
    

@transaction.atomic
def getData(data, rawUID, qiecard, run_num, tester_name):
    """Main function to grab data from the JSON file"""
    attemptlist = {}
    channels_passed = {}
    channels_failed = {}
    varlist = []
    first_channel = True
    

    for position in data[rawUID].keys():
        for channel in data[rawUID][position].keys():
            newchannel = Channel(number=CHANNEL_MAPPING[position][channel[-1]], card=qiecard)
            if newchannel not in list(qiecard.channel_set.all()):
                newchannel.save()
            failed_channel = {}
            for test in data[rawUID][position][channel].keys():
                failed_test = False
                try:
                    # Test is in the database
                    temp_test = Test.objects.get(abbreviation=test)
                    if test not in channels_passed.keys() and test not in channels_failed.keys():
                        channels_passed[test] = 0
                        channels_failed[test] = 0
                    if test not in failed_channel:
                        failed_channel[test] = False
                except ObjectDoesNotExist:
                    # Test is not in the database and can be created
                    temp_test = Test(name=test, abbreviation=test)
                    temp_test.save()
                    channels_passed[test] = 0
                    channels_failed[test] = 0
                    
                if first_channel:
                    # Only get/create attempts once per card
                    prev_attempts = list(Attempt.objects.filter(card=qiecard, test_type=temp_test))
                    attempt_num = len(prev_attempts) + 1
                    temp_attempt = Attempt(card=qiecard, 
                                           date_tested=timezone.now(), 
                                           plane_loc="default", 
                                           attempt_number=attempt_num, 
                                           test_type=temp_test,
                                           run=run_num,
                                           tester=Tester.objects.get(username=tester_name),
                                           comments=data["Comments"])
                    temp_attempt.save()
                    attemptlist[test] = temp_attempt
                        
                    for pa in prev_attempts:
                        pa.revoked=True
                        pa.save()
                            
                            
                else:
                    # Get the correct attempt
                    temp_attempt = attemptlist[test]
                        
                for variable in data[rawUID][position][channel][test].keys():
                    temp_value = data[rawUID][position][channel][test][variable][0]
                    temp_result = data[rawUID][position][channel][test][variable][1]
                                
                    temp_var = Variable(name=variable, value=temp_value, attempt=attemptlist[test], test_pass=temp_result)
                    varlist.append(temp_var)
                    if temp_result == 0.0:
                        # If the test failed, set a flag that the channel failed 
                        failed_test = True
                                    
                                    
                if failed_test:
                    failed_channel[test] = True
                    channels_failed[test] += 1
                else:
                    failed_channel[test] = False
                    channels_passed[test] += 1
                                
                                
            if first_channel:
                first_channel = False
    
    for var in varlist:
        var.save()
    
    return attemptlist, channels_passed, channels_failed

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
    rawUID = data["Unique_ID"]    # UID as stored in the JSON file
    cardUID = getUID(data["Unique_ID"])    # UID as stored in the database
    qiecard = QieCard.objects.get(uid=cardUID)    # Get the card with this specific UID
except ObjectDoesNotExist:
    sys.exit("UID does not match a QIE Card in the database. Check that the UID is correct or that the QIE Card is in the database.")


# Get the run number
run_num = data["RunNum"]
tester_name = data["Tester_Name"]

comment = ""
if not qiecard.comments == "":
    comment += "\n"
comment += str(timezone.now().date()) + " " + str(timezone.now().hour) + "." + str(timezone.now().minute) + ": "
comment += data["Comments"]
qiecard.comments = comment
qiecard.save()

################
# Get the data #
################

attemptlist, channels_passed, channels_failed = getData(data, rawUID, qiecard, run_num, tester_name)


# If this is a new run, create a new run
run_list = list(Run.objects.all())
num_list = []
for r in run_list:
    num_list.append(r.number)

if run_num not in num_list:
    new_run = Run(number=run_num)
    new_run.save()

###########################################
# Move the directory to permanent storage #
###########################################
#run = "run" + str(run_num)    # ex: run350
uploads = os.path.join(MEDIA_ROOT, "uploads/")    # path to the uploads directory
card_dir = os.path.join(uploads, "qieCards/")    # path to the qie cards
temp_card_dir = os.path.join(uploads, "run_control/cards/")    # path to where the just installed cards are

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

media = os.path.join("uploads/qieCards/", qiecard.barcode, os.path.basename(mved_src_name))
json_file = os.path.join("uploads/qieCards/", qiecard.barcode, os.path.basename(mved_src_name), file_name)


uploadAttempt(attemptlist, json_file, media, channels_passed, channels_failed)


