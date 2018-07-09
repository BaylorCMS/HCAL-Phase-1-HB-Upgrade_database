"""
cardLookup.py:
    This script looks up a card in the database and returns either the Unique ID or the barcode depending on what was given.
"""


import argparse
import django
import json
import sys


sys.path.insert(0, "/home/django/testing_database_hb/card_db")
django.setup()


from qie_cards.models import QieCard
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned



def formatUID(uID):
    formattedUID = "0x" + uID[:8].upper() + " 0x" + uID[8:].upper()
    return formattedUID


def getBarcode(uID):
    """ This functions gives back the barcode of the card if passed the unique id. Only the last 8 characters of the Unique Id are needed.
    For example, if a Unique ID is 0xb8000000_0xeac36970, then only eac36970 is needed for the lookup of the barcode. """
    
    try:
        card = QieCard.objects.get(uid__contains=uID)
        return card.barcode
    except ObjectDoesNotExist:
        return "-1"
       # sys.exit("No card matching the Unique ID '%s' was able to be found. Either the card is not in the database, or the Unique ID was passed in wrong. Make sure to pass in the last 8 digits of the Unique ID. For example, from 0xb8000000_0xeac36970 only eac36970 is needed." % uID)
    except MultipleObjectsReturned:
        return "-2"
        #  sys.exit("Multiple cards containing this Unique ID were found. Please pass in the last 8 digits of the Unique ID. For example, from 0xb8000000_0xeac36970 only eac36970 is needed.")
    


#def getUID(barcode):
#    """This function gives back the Unique ID given the barcode. The whole barcode must be given. For example, 0700001 is valid but 001 is not."""
#
#    try:
#        card = QieCard.objects.get(barcode__contains=barcode)
#    except ObjectDoesNotExist:
#        sys.exit("No card matching the Barcode '%s' was able to be found. Either the card is not in the database, or the Barcode was passed in wrong. Make sure you pass in the whole barcode, i.e 0700001." % barcode)
#    except MultipleObjectsReturned:
#        sys.exit("Multiple cards containing this barcode were found. Make sure that the whole barcode is passed in so the right card can be found, i.e 0700001.")
#    
#    uid = formatUID(card.uid)
#    return uid
#    
#        
#    
#    return card.uid

def main():
#    parser = argparse.ArgumentParser()
#    parser.add_argument("-b", "--barcode", help="Use the barcode to find the Unique ID", action='store_true')
#    parser.add_argument("identifier", help="Card identifier to be searched. Either barcode or Unique ID depending on -b or -u")
#    parser.add_argument("-u", "--unique", help="Use the Unique ID to find the barcode", action='store_true')
#    
#    options = parser.parse_args()
#    
#    mapping = {}
#    
#    if options.barcode:
#        # Get the unique id for the card using its barcode
#        uid = getUID(options.identifier)
#        mapping[options.identifier] = uid
#    
#    if options.unique:
#        # Get the barcode using the unique id
#        barcode = getBarcode(options.identifier)
#        mapping[options.identifier] = barcode
#
#
#    if mapping:
#        with open("mapping.json", "w") as outfile:
#            json.dump(mapping, outfile)
#

    filename = sys.argv[1]    # Grab the file
    
    try:
        # Try to open the file and remove any empty strings from the list
        with open(filename) as file:
            ids = file.read().splitlines()
        ids[:] = [item for item in ids if item != '']
    except IOError:
        sys.exit("File not able to be opened")
        
    mapping = {}
    for uid in ids:
        mapping[uid] = getBarcode(uid)

    if mapping:
        with open("mapping.json", "w") as output:
            json.dump(mapping, output)
            
        


if __name__ == "__main__": 
    main()


