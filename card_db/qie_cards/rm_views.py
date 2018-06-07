from django.shortcuts import render
from django.views import generic
from os import path
import json

from .models import ReadoutModule, RmLocation, RMBiasVoltage, QieCard, Test

# Create your views here.

from django.utils import timezone
from django.http import HttpResponse, Http404
from card_db.settings import MEDIA_ROOT 


class CatalogView(generic.ListView):
    """ This displays a list of all readout modules """
    
    template_name = 'readout_modules/catalog.html'
    context_object_name = 'rm_list'
    def get_queryset(self):
        return ReadoutModule.objects.all().order_by('rm_number')

def catalog(request):
    """ This displays a list of all readout modules """
    rms = ReadoutModule.objects.all().order_by('rm_number')
    count = len(rms)

    return render(request, 'readout_modules/catalog.html', {'rm_list': rms,
                                                            'total_count': count})

def detail(request, rm):
    """ This displays details about a readout module """
    if len(rm) > 4: # rm must be the unique id
        try:
            readoutMod = ReadoutModule.objects.get(rm_uid__endswith=rm[-3:])
        except ReadoutModule.DoesNotExist:
            #raise Http404("Readout Module uid " + str(rm) + " does not exist")
            return render(request, 'readout_modules/error.html')
    else:           # rm must be the barcode
        try:
            readoutMod = ReadoutModule.objects.get(rm_number=rm)
        except ReadoutModule.DoesNotExist:
            #raise Http404("Readout Module number " + str(rm) + " does not exist")
            return render(request, 'readout_modules/error.html')

    if(request.POST.get('comment_add')):
        comment = ""
        if not readoutMod.comments == "":
            comment += "\n"
        comment += str(timezone.now().date()) + " " + str(timezone.now().hour) + "." + str(timezone.now().minute) + ": " + request.POST.get('comment')
        readoutMod.comments += comment
        readoutMod.save()

    if(request.POST.get('location_add')):
        if len(RmLocation.objects.filter(rm=readoutMod)) < 10:
            RmLocation.objects.create(geo_loc=request.POST.get("location"), rm=readoutMod)

    """ Now a script updates Readout Module locations every hour. """
    #readoutMod.update()
    locations = RmLocation.objects.filter(rm=readoutMod)
    
    try:
        biasVolts = RMBiasVoltage.objects.get(readout_module=readoutMod)
    except RMBiasVoltage.DoesNotExist:
        biasVolts = ""

    return render(request, 'readout_modules/detail.html', {'rm': readoutMod,
                                                           'locations': locations,
                                                           'bv' : biasVolts,
                                                          })


def error(request): 
    """ This displays an error for incorrect barcode or unique id """
    return render(request, 'readout_modules/error.html')

def fieldView(request):
    """ This displays RM field data. """
    options = ["rm_number",
               "rm_uid",
               "card_1",
               "card_2",
               "card_3",
               "card_4",
               "card_1.status",
               "card_2.status",
               "card_3.status",
               "card_4.status",
               "card_1.uid",
               "card_2.uid",
               "card_3.uid",
               "card_4.uid",
               "card_1.b_fw",
               "card_2.b_fw",
               "card_3.b_fw",
               "card_4.b_fw",
               "card_1.i_top_fw",
               "card_1.i_bot_fw",
               "card_2.i_top_fw",
               "card_2.i_bot_fw",
               "card_3.i_top_fw",
               "card_3.i_bot_fw",
               "card_4.i_top_fw",
               "card_4.i_bot_fw",
               "comments",
               "last location"]
    
    fields = []
    for i in range(6):
        if(request.POST.get('field' + str(i+1))):
            field = request.POST.get('field' + str(i+1))
            if field in options:
                fields.append(field)


    rms = list(ReadoutModule.objects.all().order_by("rm_number"))
    cards = list(QieCard.objects.all().order_by("barcode"))
    locs = RmLocation.objects.all().order_by("rm")
    items = []
    # Info for "Card Status"
    cache = path.join(MEDIA_ROOT, "cached_data/summary.json")
    infile = open(cache, "r")
    cardStat = json.load(infile)
    infile.close()
    num_required = len(Test.objects.filter(required=True))
    
    for i in xrange(len(rms)):
        rm = rms[i]
        item = {}
        item["id"] = rm.pk
        item["fields"] = []
        for field in fields:
            f_list = field.split(".")
            if field == "last location":    # Get RM last location
                loc_list = locs.filter(rm=rm).order_by("date_received")
                if len(loc_list) == 0:
                    item["fields"].append("No Locations Recorded")
                else:
                    #item["fields"].append(len(card.location_set.all()))
                    item["fields"].append(loc_list.reverse()[0].geo_loc)
            elif f_list[-1] == "status":    # Get QIE Card status
                card = getattr(rm, f_list[0])
                j = cards.index(card)
                if cardStat[j]["num_failed"] != 0:
                    item["fields"].append("FAILED")
                elif cardStat[j]["num_passed"] == num_required:
                    if cardStat[j]["forced"]:
                        item["fields"].append("GOOD (FORCED)")
                    else:
                        item["fields"].append("GOOD")
                else:
                    item["fields"].append("INCOMPLETE")
            elif field[-2:] == "fw":        # Get QIE Card firmware (bridge or igloo)
                card = getattr(rm, f_list[0])
                firmware = f_list[1]
                if firmware == "b_fw":      # Bridge firmware
                    item["fields"].append(card.get_bridge_ver_hex())
                elif firmware == "i_top_fw":    # Igloo firmware
                    item["fields"].append(card.get_top_igloo_ver_hex())
                elif firmware == "i_bot_fw":    # Igloo firmware
                    item["fields"].append(card.get_bot_igloo_ver_hex())
            elif f_list[-1] == "uid":       # Get QIE Card unique id
                card = getattr(rm, f_list[0])
                item["fields"].append(card.uid)
            else:                           # Get RM attribute: RM number, unique id, QIE Cards (1-4), comments, last location
                item["fields"].append(getattr(rm, field))

        items.append(item)

    return render(request, 'readout_modules/fieldView.html', {'fields': fields, "items": items, "options": options})


