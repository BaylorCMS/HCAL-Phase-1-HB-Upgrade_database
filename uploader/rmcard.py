import sys
import django
sys.path.insert(0, '/home/django/testing_database_hb/card_db')
django.setup()
from qie_cards.models import QieCard 
from django.core.exceptions import ObjectDoesNotExist

barcode = sys.argv[1]
try:
    if barcode == QieCard.objects.get(barcode=barcode).barcode:
        QieCard.objects.filter(barcode=barcode).delete()
        print "Qie Card with barcode '%s' succesfully deleted" % barcode
    else:
        print "Qie Card with barcode '%s' unable to be removed. Check to see if it is attached to a RM." % barcode
except ObjectDoesNotExist:
    print "Qie Card with barcode '%s' is not in the database" % barcode
