import os
import sys
import shutil
from card_stats import set_card_status
import django

sys.path.insert(0, '/home/django/testing_database_hb/card_db')
django.setup()

from qie_cards.models import QieCard, Attempt, Test, Tester
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from card_db.settings import MEDIA_ROOT
from django.db import transaction

path_to_pics = os.path.join("/home/django/testing_database_hb/uploader", "qiecard_pics")
file_name = os.path.join(path_to_pics, os.listdir(path_to_pics)[0])

code = os.path.splitext(os.path.basename(file_name))[0]

try:
    qiecard = QieCard.objects.get(barcode=str(code))
except ObjectDoesNotExist:
    sys.exit("Card with barcode does not exist in the database.")

try:
    test = Test.objects.get(name="Card Picture")
except ObjectDoesNotExist:
    test = Test(name="Card Picture", abbreviation="moneyshot")
    test.save()

tester = Tester.objects.get(username="hcaldaq")

try:
    temp_attempt = Attempt.objects.get(card=qiecard, test_type__name="Card Picture")
except ObjectDoesNotExist:
    temp_attempt = Attempt(card=qiecard, 
                           result=1,
                           date_tested=timezone.now(),
                           plane_loc="default",
                           attempt_number=1,
                           tester=tester,
                           test_type=Test.objects.get(name="Card Picture"),
                           )

shutil.move(file_name, os.path.join(MEDIA_ROOT, "uploads", "qieCards", qiecard.barcode, os.path.basename(file_name)))

temp_attempt.image = os.path.join("uploads", "qieCards", qiecard.barcode, os.path.basename(file_name))
temp_attempt.save()
set_card_status(qiecard)
print "Card Uploaded Succesfully"

