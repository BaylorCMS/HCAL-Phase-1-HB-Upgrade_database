"""
#   update_json.py:
#       This script collects the necessary database into a json. This json
#       is then used in the website to generate the interactive plots.
"""

__author__  = "Andrew Baas"
__credits__ = ["Joe Pastika", "Adryanna Smith", "Andrew Baas"]

__version__     = "2.0"
__maintainer__  = "Caleb Smith"
__email__       = "caleb_smith2@baylor.edu"
__status__      = "Live"

import sys
import os
import json
import calendar
from django import setup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "card_db.settings")
sys.path.insert(0, '/home/django/testing_database/card_db')
setup()

from qie_cards.models import Test, Attempt, QieCard

# These constants define the possible states of a card
FAILED = 2      # Card failed test in at least one non-revoked attempt
PASSED = 1      # Card passed test in all non-revoked attempts
REMAIN = 0      # Card had attempts, yet all were revoked
DEFAULT = -1    # Card had no attempts

# Uploads all required data from the database
tests = list(Test.objects.all())
attempts = list(Attempt.objects.order_by("date_tested"))
cards = list(QieCard.objects.all())

testStates = {} # Stores the states of each test for each card

# Make each test's id be an index in the dictionary
for test in tests:
    testStates[str(test.pk)] = {}
    # Add data about each card into the dictionary per test
    for card in cards:
        temp = {"barcode":card.barcode, "date":-1,"state":DEFAULT}
        testStates[str(test.pk)][card.pk] = temp

# Change the state of each card depending upon the attempts
for attempt in attempts:

    curState = testStates[str(attempt.test_type_id)][attempt.card_id]["state"]
    
    # Determine how to change the state of the card
    if not curState == FAILED:
        if (attempt.passed_all() or attempt.overwrite_pass) and not attempt.revoked:
            testStates[str(attempt.test_type_id)][attempt.card_id]["date"] = calendar.timegm(attempt.date_tested.timetuple())
            testStates[str(attempt.test_type_id)][attempt.card_id]["state"] = PASSED
       
        elif not attempt.num_failed == 0 and not attempt.revoked:   
            testStates[str(attempt.test_type_id)][attempt.card_id]["date"] = calendar.timegm(attempt.date_tested.timetuple())
            testStates[str(attempt.test_type_id)][attempt.card_id]["state"] = FAILED
       
        elif attempt.revoked and curState == DEFAULT:
            testStates[str(attempt.test_type_id)][attempt.card_id]["date"] = calendar.timegm(attempt.date_tested.timetuple())
            testStates[str(attempt.test_type_id)][attempt.card_id]["state"] = REMAIN

# Dump the json into the proper location
with open("/home/django/testing_database/media/plots/plots.json", 'w') as f:
    json.dump(testStates, f)
f.close()
