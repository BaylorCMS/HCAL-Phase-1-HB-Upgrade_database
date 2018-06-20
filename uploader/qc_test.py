"""
qc_test.py:
    This script takes a json file location as an argument and processes the data to upload
    into the database. This script will be used to upload the data from the quality control 
    testing.
"""

__author__ = "Nesta Lenhert-Scholer"

import sys
import json
import django

sys.path.insert(0, '/home/django/testing_database_hb/card_db')
django.setup()

from qie_cards.models import QieCard, Attempt, Channel, Test, Variable, Tester
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from card_db.settings import MEDIA_ROOT

print MEDIA_ROOT
CHANNEL_MAPPING= {"Top": {"0": 1, "1": 2, "2": 3, "3": 4, "4": 5, "5": 6, "6": 7, "7": 8},
                  "Bot": {"0": 9, "1": 10, "2": 11, "3": 12, "4": 13, "5": 14, "6": 15, "7": 16}}


def getUID(uid):
    uniqueid = uid[2:10] + uid[13:]
    carduid=str(uniqueid)
    return carduid.lower()


# load the json file
fileName = sys.argv[1]
run_num = sys.argv[2]
# open the file and read it
try:
    inFile = open(fileName, "r")
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

attemptlist = {}    # Hold Attempt objects with keys being the test names
channels_passed = {}
channels_failed = {}
first_channel = True

# Get the data
for position in data[rawUID].keys():
    for channel in data[rawUID][position].keys():
        newchannel = Channel(number=CHANNEL_MAPPING[position][channel[-1]], card=qiecard)
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
                                       tester=Tester.objects.get(username="Nesta Lenhert"))
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
                temp_var.save()
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

# Add the correct channels passed/failed to attempts
for test in attemptlist.keys():
    attemptlist[test].num_channels_passed = channels_passed[test]
    attemptlist[test].num_channels_failed = channels_failed[test]
    attemptlist[test].result = bool(channels_failed[test] == 0)
    attemptlist[test].save()

