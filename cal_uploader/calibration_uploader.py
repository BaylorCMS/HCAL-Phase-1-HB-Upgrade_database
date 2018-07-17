import sqlite3
import os
import sys
import time
import json
from shutil import copyfile
import django

sys.path.insert(0, '/home/django/testing_database_hb/card_db')
django.setup()

from qie_cards.models import QieCard, QieShuntParams, Test, Attempt, Tester
from card_db.settings import MEDIA_ROOT

def getUID(uid):
    """Gets the Unique ID to be used in finding the associated card"""
    
    split_id = uid.split("_")
    uniqueid = split_id[0][2:] + split_id[1][2:]
    while len(uniqueid) < 16:
        uniqueid = "0" + uniqueid

    return uniqueid.lower()


def makeOutputPath(uID, destination):
    path = os.path.join(destination, uID + "_CAL")
    if os.path.exists(path):
        extension = 2
        while os.path.exists(destination + "/{0}_CAL_v{1}".format(uID, extension)):
            extension += 1
        path = os.path.join(destination, "{0}_CAL_v{1}".format(uID, extension))
    return path


filename = sys.argv[1]    # JSON File
hex_uid = sys.argv[2]   # UniqueID for the specific card in hex form

uid = getUID(hex_uid)   # Raw UniqueID to be stored in the database

try:
    inFile = open(filename, "r")
except IOError:
    sys.exit("File could not be found. Make sure there is a JSON file in the directory.")

try:
    data = json.load(inFile)
except:
    sys.exit("Unable to load the JSON file. Make sure the file is formatted correctly as a JSON file.")



try:
    # Try to get the card
    card = QieCard.objects.get(uid=uid)
except QieCard.DoesNotExist:
    # Except if it doesn't exist then it will throw an error
    sys.exit("Card with this UniqueID is not in the database")

try:
    # Try to get the test
    cal_test = Test.objects.get(name="Calibration")
except Test.DoesNotExist:
    # If it doesn't exist then create it
    cal_test = Test(name="Calibration", abbreviation="cal", required=True)
    print cal_test
    #cal_test.save()

date = data["date"]
run_num = data["run"]
result = data["Result"]
tester = data["Tester"][0]

prev_attempts = list(Attempt.objects.filter(card=card, test_type=cal_test))    # Get list of all old attempts for this card and test
attempt_num = len(prev_attempts) + 1    # Increment the current attempt number by 1

# Create the new attempt 
temp_attempt = Attempt(card=card,
                       date_tested=date,
                       plane_loc="default",
                       attempt_number=attempt_num,
                       test_type=cal_test,
                       result=result,
                       cal_run=run_num,
                       #tester=Tester.objects.get(username__contains=tester)
                       )
#temp_attempt.save()
#for pa in prev_attempts:
#    pa.revoked=True
#    pa.save()

###########################################
# Move the directory to permanent storage #
###########################################

uploads = os.path.join(MEDIA_ROOT, "uploads/")
print "Uploads: " + uploads
card_dir = os.path.join(uploads, "qieCards/")
print "Card_dir: " + card_dir
destination = os.path.join(card_dir, card.barcode)
print "Destination: " + destination
temp_card_dir = os.path.basename(os.path.dirname(filename))
print "Temp Card Dir: " + temp_card_dir






















