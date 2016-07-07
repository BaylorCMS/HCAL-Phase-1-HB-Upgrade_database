import sys
import os
import json
import django

sys.path.insert(0, '/home/django/testing_database/card_db')
django.setup()

from django.utils import timezone
from qie_cards.models import Test, Tester, Attempt, Location, QieCard
from card_db.settings import MEDIA_ROOT



def getUID(raw):
    """ Parses the raw UID into a pretty-print format """
    raw = raw[4:]
    refined = ""
    for i in range(6):
        refined += raw[2*i : 2*(i + 1)]
        refined += ':'
    return refined[:17]

def moveJsonFile(qie, fileName):
    """ Moves the json for this upload to permanent storage """
    url = os.path.join("uploads/", qie.barcode)
    path = os.path.join(MEDIA_ROOT, url)
    if not os.path.exists(path):
        exit("Database does not contain this card's log folder")
        
    newPath = os.path.join(path, str(timezone.now()) + os.path.basename(fileName))
    os.rename(fileName, newPath)
    return os.path.join(url, str(timezone.now()) + os.path.basename(fileName))

# Get filename and upload file to dictionary
fileName = sys.argv[1]
infile = open(fileName, "r")
cardData = json.load(infile)

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
for test in ["overall pedestal", "overall charge injection", "overall shunt scan", "overall phase scan"]:

test = "overall phase scan"
try:
    temp_test = Test.objects.get(abbreviation=test)
except:
    sys.exit('Test "%s" not in database' % test)

data = cardData[test]

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
                           log_file=url
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
                           log_file=url
                           )
        
if overwrite:
    for prev_att in prev_attempts:
        prev_att.revoked = True
        prev_att.save()

attemptArr.append(temp_attempt)

test = "overall shunt scan"
try:
    temp_test = Test.objects.get(abbreviation=test)
except:
    sys.exit('Test "%s" not in database' % test)

data = cardData[test]

histoName = os.path.join(os.path.directory(fileName), "histostats.tar.gz")

url = moveJsonFile(qie, pedName)

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
                           log_file=url
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
                           log_file=url
                           )
        
if overwrite:
    for prev_att in prev_attempts:
        prev_att.revoked = True
        prev_att.save()

attemptArr.append(temp_attempt)

test = "overall charge injection"
try:
    temp_test = Test.objects.get(abbreviation=test)
except:
    sys.exit('Test "%s" not in database' % test)

data = cardData[test]

pedName = os.path.join(os.path.directory(fileName), "ci_plot" + str(cardData["Jslot"]) + ".tar.gz")

url = moveJsonFile(qie, pedName)

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
                           log_file=url
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
                           log_file=url
                           )
        
if overwrite:
    for prev_att in prev_attempts:
        prev_att.revoked = True
        prev_att.save()

attemptArr.append(temp_attempt)

test = "overall pedestal"
try:
    temp_test = Test.objects.get(abbreviation=test)
except:
    sys.exit('Test "%s" not in database' % test)

data = cardData[test]

pedName = os.path.join(os.path.directory(fileName), "ped_plot" + str(cardData["Jslot"]) + ".tar.gz")

url = moveJsonFile(qie, pedName)

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
                           log_file=url
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
                           log_file=url
                           )
        
if overwrite:
    for prev_att in prev_attempts:
        prev_att.revoked = True
        prev_att.save()

attemptArr.append(temp_attempt)
        
for attempt in attemptArr:
    attempt.save()