"""
qc_test.py:
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

from qie_cards.models import QieCard, Attempt, Channel, Test, Variable, Tester
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
def getData(data, rawUID, qiecard):
    """Main function to grab data from the JSON file"""
    #print "I'm in the main function"
    attemptlist = {}
    channels_passed = {}
    channels_failed = {}
    varlist = []
    first_channel = True

    for position in data[rawUID].keys():
    #    print "I'm in the main loop"
        for channel in data[rawUID][position].keys():
            newchannel = Channel(number=CHANNEL_MAPPING[position][channel[-1]], card=qiecard)
   #         print "New channel save"
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
  #                  print "New test save"
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
                                           tester=Tester.objects.get(username="Nesta Lenhert"))
                    temp_attempt.save()
                    attemptlist[test] = temp_attempt
                        
                    for pa in prev_attempts:
                        pa.revoked=True
         #               print "new prev_attempt save"
                        pa.save()
                            
                            
                else:
                    # Get the correct attempt
                    temp_attempt = attemptlist[test]
                        
                for variable in data[rawUID][position][channel][test].keys():
                    temp_value = data[rawUID][position][channel][test][variable][0]
                    temp_result = data[rawUID][position][channel][test][variable][1]
                                
                    temp_var = Variable(name=variable, value=temp_value, attempt=attemptlist[test], test_pass=temp_result)
                    varlist.append(temp_var)
 #                   print "new variable save"
                    #temp_var.save()
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
#        print "in varlist save loop"
        var.save()
    
    return attemptlist, channels_passed, channels_failed

# load the json file
file_name = sys.argv[1]
run_num = sys.argv[2]
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

#attemptlist = {}    # Hold Attempt objects with keys being the test names
#channels_passed = {}
#channels_failed = {}
#first_channel = True
#
################
# Get the data #
################

attemptlist, channels_passed, channels_failed = getData(data, rawUID, qiecard)
#print data
#print rawUID
#print qiecard
#print attemptlist
#print channels_passed
#print channels_failed

###########################################
# Move the directory to permanent storage #
###########################################
run = "run" + str(run_num)    # ex: run350
uploads = os.path.join(MEDIA_ROOT, "uploads/")    # path to the uploads directory
run_control = os.path.join(uploads, "run_control/")    # path to the run control directory

destination = os.path.join(uploads, qiecard.barcode)    # path to the destination directory i.e. 0700001/
source_dir = os.path.join(run_control, (run + "_output/QC_" + run + "/"))    # temp directory for all the uploaded qie cards
new_dir_name = rawUID + "_QC_" + run    # what the new directories will be called i.e. 0x11111111_0x2124124124_QC_run350

old_src_name = os.path.join(source_dir, rawUID)    # where the temporary storage is for the UID directories
new_src_name = os.path.join(source_dir, new_dir_name)    # where the permanent storage will be for the UID directories

mved_src_name = os.path.join(destination, new_dir_name)

file_name = os.path.basename(file_name) # only grab the basename from the full path for the JSON file

# Rename the UID Directory name
os.renames(old_src_name, new_src_name)

# Move UID Directory to its permanent storage
shutil.move(new_src_name, destination)

new_file_name = os.path.join(mved_src_name, file_name)

media = os.path.join("uploads/", qiecard.barcode, os.path.basename(mved_src_name))
json_file = os.path.join("uploads/", qiecard.barcode, os.path.basename(mved_src_name), file_name)

uploadAttempt(attemptlist, json_file, media, channels_passed, channels_failed)

# Save the media and url for the attempts
#for test in attemptlist.keys():
#    attemptlist[test].log_file = json_file
#    attemptlist[test].hidden_log_file = json_file
#    attemptlist[test].image = os.path.join(media, str(test))
#    attemptlist[test].num_channels_passed = channels_passed[test]
#    attemptlist[test].num_channels_failed = channels_failed[test]
#    attemptlist[test].result = bool(channels_failed[test] == 0)
#    attemptlist[test].save()

