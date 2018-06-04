"""
#   uhtr_upload.py:
#       This script accepts a properly formatted .json file and uploads it
#       to the database. The json file should contain uhtr test results
#       of Test Stand 2.
"""

__author__  = "Andrew Baas"
__credits__ = ["Shaun Hogan", "Mason Dorseth", "John Lawrence",
                "Jordan Potarf", "Joe Pastika", "Andrew Baas"]

__version__     = "2.01"
__maintainer__  = "Caleb Smith"
__email__       = "caleb_smith2@baylor.edu"
__status__      = "Live"

import sys
from shutil import copyfile, copytree, rmtree
import os
import json
import django
import time

sys.path.insert(0, '/home/django/testing_database/card_db')
django.setup()

from django.utils import timezone
from qie_cards.models import Test, Tester, Attempt, Location, QieCard
from card_db.settings import MEDIA_ROOT



def getUID(raw):
    """ Parses the raw UID into a pretty-print format """ 
    return raw[2:18]

def moveImageDir(qie, folder):
    """ Moves the folder of images """
    uniquePre = str(int(time.time()))
    url = os.path.join("uploads/", qie.barcode)
    path = os.path.join(MEDIA_ROOT, url)
    if not os.path.exists(path):
        exit("Database does not contain this card's log folder")
        
    newPath = os.path.join(path, uniquePre + os.path.basename(folder))
    copytree(folder, newPath)
    return os.path.join(url, uniquePre + os.path.basename(folder))

def moveJsonFile(qie, fileName):
    """ Moves the json for this upload to permanent storage """
    uniquePre = str(int(time.time()))
    url = os.path.join("uploads/", qie.barcode)
    path = os.path.join(MEDIA_ROOT, url)
    if not os.path.exists(path):
        exit("Database does not contain this card's log folder")
        
    newPath = os.path.join(path, uniquePre + os.path.basename(fileName))
    copyfile(fileName, newPath)
    return os.path.join(url, uniquePre + os.path.basename(fileName))

# Get filename and upload file to dictionary
fileName = sys.argv[1]
infile = open(fileName, "r")
try:
    cardData = json.load(infile)
except:
    sys.exit("Unable to load json file.")

overwrite = cardData["Overwrite"]

# Check if the tester exists
try:
    tester = Tester.objects.get(username=cardData["User"])
except:
    sys.exit("Tester %s not valid" % cardData["User"]) 

# Get the time of the test
test_time = cardData["DateRun"] + "-06:00"

# Check if the QIE card exists
try:
    qie = QieCard.objects.get(uid=getUID(cardData["Unique_ID"]))
except:
    sys.exit('QIE card with UID %s not in database' % getUID(cardData["Unique_ID"]))

# Move the json file 
url = moveJsonFile(qie, fileName)

attemptArr = []

#load in all test results

###############################################
#            Loading Phase Scan               #
###############################################
test = "overall phase scan"

try:
    temp_test = Test.objects.get(abbreviation=test)
except:
    sys.exit('Test "%s" not in database' % test)

data = cardData[test]

phaseName = os.path.join(os.path.dirname(fileName), "phase_plot" + str(cardData["Jslot"]))
media = moveImageDir(qie, phaseName)

prev_attempts = list(Attempt.objects.filter(card=qie, test_type=temp_test))
attempt_num = len(prev_attempts) + 1
if(data[0] == 0 and data[1] == 0):
    temp_attempt = Attempt(card=qie,
                           plane_loc=cardData["Jslot"],
                           test_type=temp_test,
                           attempt_number=attempt_num,
                           tester=tester,
                           date_tested=test_time,
                           num_passed=0,
                           num_failed=0,
                           revoked=True,
                           comments="This test returned no testing data",
                           log_file=url,
                           image=media,
                           hidden_log_file=url,
                           )
else:
    temp_attempt = Attempt(card=qie,
                           plane_loc="default",
                           test_type=temp_test,
                           attempt_number=attempt_num,
                           tester=tester,
                           date_tested=test_time,
                           num_passed=data[0],
                           num_failed=data[1],
                           log_file=url,
                           image=media,
                           hidden_log_file=url,
                           )
        
if overwrite:
    for prev_att in prev_attempts:
        prev_att.revoked = True
        prev_att.save()

attemptArr.append(temp_attempt)

###############################################
#            Loading Shunt Scan               #
###############################################
test = "overall shunt scan"
try:
    temp_test = Test.objects.get(abbreviation=test)
except:
    sys.exit('Test "%s" not in database' % test)

data = cardData[test]

shuntName = os.path.join(os.path.dirname(fileName), "shunt_plot" + str(cardData["Jslot"]))

media = moveImageDir(qie, shuntName)

prev_attempts = list(Attempt.objects.filter(card=qie, test_type=temp_test))
attempt_num = len(prev_attempts) + 1
if(data[0] == 0 and data[1] == 0):
    temp_attempt = Attempt(card=qie,
                           plane_loc=cardData["Jslot"],
                           test_type=temp_test,
                           attempt_number=attempt_num,
                           tester=tester,
                           date_tested=test_time,
                           num_passed=0,
                           num_failed=0,
                           revoked=True,
                           comments="This test returned no testing data",
                           image=media,
                           log_file=url,
                           hidden_log_file=url,
                           )
else:
    temp_attempt = Attempt(card=qie,
                           plane_loc="default",
                           test_type=temp_test,
                           attempt_number=attempt_num,
                           tester=tester,
                           date_tested=test_time,
                           num_passed=data[0],
                           num_failed=data[1],
                           image=media,
                           log_file=url,
                           hidden_log_file=url,
                           )

if overwrite:
    for prev_att in prev_attempts:
        prev_att.revoked = True
        prev_att.save()

attemptArr.append(temp_attempt)

###############################################
#          Loading Charge Injection           #
###############################################
test = "overall charge injection"
try:
    temp_test = Test.objects.get(abbreviation=test)
except:
    sys.exit('Test "%s" not in database' % test)

data = cardData[test]

ciName = os.path.join(os.path.dirname(fileName), "ci_plot" + str(cardData["Jslot"]))
media = moveImageDir(qie, ciName)

prev_attempts = list(Attempt.objects.filter(card=qie, test_type=temp_test))
attempt_num = len(prev_attempts) + 1
if(data[0] == 0 and data[1] == 0):
    temp_attempt = Attempt(card=qie,
                           plane_loc=cardData["Jslot"],
                           test_type=temp_test,
                           attempt_number=attempt_num,
                           tester=tester,
                           date_tested=test_time,
                           num_passed=0,
                           num_failed=0,
                           revoked=True,
                           comments="This test returned no testing data",
                           log_file=url,
                           image=media,
                           hidden_log_file=url,
                           )
else:
    temp_attempt = Attempt(card=qie,
                           plane_loc="default",
                           test_type=temp_test,
                           attempt_number=attempt_num,
                           tester=tester,
                           date_tested=test_time,
                           num_passed=data[0],
                           num_failed=data[1],
                           log_file=url,
                           image=media,
                           hidden_log_file=url,
                           )
        
if overwrite:
    for prev_att in prev_attempts:
        prev_att.revoked = True
        prev_att.save()

attemptArr.append(temp_attempt)

###############################################
#         Loading Pedestal Values             #
###############################################
test = "overall pedestal"
try:
    temp_test = Test.objects.get(abbreviation=test)
except:
    sys.exit('Test "%s" not in database' % test)

data = cardData[test]

pedName = os.path.join(os.path.dirname(fileName), "ped_plot" + str(cardData["Jslot"]))

media = moveImageDir(qie, pedName)

prev_attempts = list(Attempt.objects.filter(card=qie, test_type=temp_test))
attempt_num = len(prev_attempts) + 1
if(data[0] == 0 and data[1] == 0):
    temp_attempt = Attempt(card=qie,
                           plane_loc=cardData["Jslot"],
                           test_type=temp_test,
                           attempt_number=attempt_num,
                           tester=tester,
                           date_tested=test_time,
                           num_passed=0,
                           num_failed=0,
                           revoked=True,
                           comments="This test returned no testing data",
                           log_file=url,
                           image=media,
                           hidden_log_file=url,
                           )
else:
    temp_attempt = Attempt(card=qie,
                           plane_loc="default",
                           test_type=temp_test,
                           attempt_number=attempt_num,
                           tester=tester,
                           date_tested=test_time,
                           num_passed=data[0],
                           num_failed=data[1],
                           log_file=url,
                           image=media,
                           hidden_log_file=url,
                           )
        
if overwrite:
    for prev_att in prev_attempts:
        prev_att.revoked = True
        prev_att.save()

attemptArr.append(temp_attempt)


###############################################
#           Submitting Attempts               #
###############################################
for attempt in attemptArr:
    attempt.save()

###############################################
#        Deleting Plot Folders                #
###############################################
rmtree(phaseName)
rmtree(ciName)
rmtree(pedName)
rmtree(shuntName)
