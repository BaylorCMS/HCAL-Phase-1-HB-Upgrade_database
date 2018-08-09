"""
#   step1.py:
#       This script accepts a properly formatted .json file and uploads it
#       to the database. The json file should contain results from Step 1
#       of Test Stand 1.
"""

__author__  = "Andrew Baas"
__credits__ = ["Shaun Hogan", "Mason Dorseth", "John Lawrence",
                "Jordan Potarf", "Joe Pastika", "Andrew Baas"]

__version__     = "2.01"
__maintainer__  = "Caleb Smith"
__email__       = "caleb_smith2@baylor.edu"
__status__      = "Live"

import sys
import os
import json
import django
from shutil import copyfile
from django.utils import timezone
from card_stats import set_card_status

sys.path.insert(0, '/home/django/testing_database_hb/card_db')
django.setup()

from qie_cards.models import Test, Tester, Attempt, Location, QieCard
from card_db.settings import MEDIA_ROOT

def loadCard(cardData, overwrite):
    """ Loads in QIE card information """
    new_comments =  cardData["TestComment"]
    barcode =   cardData["Barcode"]

    # find or create the qie card for the database
    if overwrite:
        try:
            card = QieCard.objects.get(barcode=barcode)
        except:
            sys.exit('QIE card with barcode "%s" is not in the database' % cardData["Barcode"])
        if card.comments != "":
            card.comments = "Overwritten: " + card.comments + "\n" + new_comments
        else:
            card.comments = new_comments
    else:
        qie = QieCard.objects.filter(barcode=barcode)

        if qie:
            sys.exit('QIE card with barcode "%s" is already in the database' % cardData["Barcode"])
        else:
            card = QieCard(barcode=barcode,
                           comments=new_comments
                           )

    return card

def loadTests(qie, tester, date, testData, path, overwrite):
    """ Loads in all test results """
    attempts = []
    for test in testData.keys():
        try:
            temp_test = Test.objects.get(abbreviation=test)
        except:
            print 'Test "%s" not in database' % test
            print 'Creating "%s" now' % test
            temp_test = Test(name=test, abbreviation=test)
            temp_test.save()

        prev_attempts = list(Attempt.objects.filter(card=qie, test_type=temp_test))
        attempt_num = len(prev_attempts) + 1
        if not testData[test] == "na":
            if testData[test]:
                temp_attempt = Attempt(card=qie,
                                       plane_loc="default",
                                       test_type=temp_test,
                                       attempt_number=attempt_num,
                                       tester=tester,
                                       date_tested=date,
                                       result=1,
                                       temperature=-999,
                                       humidity=-999,
                                       log_file=path,
                                       hidden_log_file=path,
                                       )
            else:
                temp_attempt = Attempt(card=qie,
                                       plane_loc="default",
                                       test_type=temp_test,
                                       attempt_number=attempt_num,
                                       tester=tester,
                                       date_tested=date,
                                       result=0,
                                       temperature=-999,
                                       humidity=-999,
                                       log_file=path,
                                       hidden_log_file=path,
                                       )
            if overwrite:
                for prev_att in prev_attempts:
                    prev_att.revoked = True
                    prev_att.save()
            
            attempts.append(temp_attempt)
    return attempts

def setLocation(qie, date):
    """ Sets a location for the card """
    return Location(card=qie,
                    date_received=date,
                    geo_loc="Wilson Hall 14th floor, Fermilab"
                    )

def moveJsonFile(qie, fileName, overwrite):
    """ Moves the json for this upload to permanent storage """
    url = os.path.join("uploads/qieCards/", qie.barcode)
    path = os.path.join(MEDIA_ROOT, url)
    if overwrite:
        if not os.path.exists(path):
            exit("Database does not contain folder for this card")
        extension = 1
        while os.path.isfile(os.path.join(path,  str(extension) + os.path.basename(fileName))):
            extension += 1
        newPath = os.path.join(path,  str(extension) + os.path.basename(fileName))
            
    else:
        if os.path.exists(path):
            exit("Database already contains folder for this card")    
        os.makedirs(path)
        newPath = os.path.join(path, os.path.basename(fileName))
    
    copyfile(fileName, newPath)
    return os.path.join(url, os.path.basename(newPath))

# Load the .json into a dictionary
fileName = sys.argv[1]

infile = open(fileName, "r")
cardData = json.load(infile)

overwrite = cardData["Overwrite"]

# Upload data to the database
qie = loadCard(cardData, overwrite)

#load time of test
date = cardData["DateRun"] + "-05:00"

#find tester account
try:
    tester = Tester.objects.get(username=cardData["User"])
except:
    sys.exit("Tester %s not valid" % cardData["User"])


newPath = moveJsonFile(qie, fileName, overwrite)
qie.save()

attempts = loadTests(qie, tester, date, cardData["testResults"], newPath, overwrite)

if not overwrite:
    location = setLocation(qie, date)
    location.save()

for attempt in attempts:
    attempt.comments = cardData["TestComment"]
    attempt.save()

set_card_status(qie)
