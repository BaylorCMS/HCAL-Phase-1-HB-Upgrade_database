from django.shortcuts import render
from django.views import generic
from os import path
import json

from .models import CalibrationUnit, CuLocation, QieCard, Test

# Create your views here.

from django.utils import timezone
from django.http import HttpResponse, Http404
from card_db.settings import MEDIA_ROOT 


class CatalogView(generic.ListView):
    """ This displays a list of all calibration units """
    
    template_name = 'calibration_units/catalog.html'
    context_object_name = 'cu_list'
    def get_queryset(self):
        return CalibrationUnit.objects.all().order_by('cu_number')

def catalog(request):
    """ This displays a list of all calibration units """

    cus = CalibrationUnit.objects.all().order_by('cu_number')
    count = len(cus)

    return render(request, 'calibration_units/catalog.html', {'cu_list': cus,
                                                              'total_count': count})

def detail(request, cu):
    """ This displays details about a calibration unit """
    if len(cu) > 3: # cu must be the unique id
        try:
            calUnit = CalibrationUnit.objects.get(cu_uid__endswith=cu)
        except CalibrationUnit.DoesNotExist:
            #raise Http404("Calibration Unit number " + str(cu_number) + " does not exist")
            return render(request, 'calibration_unit/error.html')
    else:           # cu must be the barcode
        try:
            calUnit = CalibrationUnit.objects.get(cu_number=cu)
        except CalibrationUnit.DoesNotExist:
            #raise Http404("Calibration Unit number " + str(cu_number) + " does not exist")
            return render(request, 'calibration_unit/error.html')

    if(request.POST.get('comment_add')):
        comment = ""
        if not calUnit.comments == "":
            comment += "\n"
        comment += str(timezone.now().date()) + " " + str(timezone.now().hour) + "." + str(timezone.now().minute) + ": " + request.POST.get('comment')
        calUnit.comments += comment
        calUnit.save()
    
    if(request.POST.get('location_add')):
        if len(CuLocation.objects.filter(cu=calUnit)) < 10:
            CuLocation.objects.create(geo_loc=request.POST.get("location"), cu=calUnit)

    locations = CuLocation.objects.filter(cu=calUnit)
    
    return render(request, 'calibration_units/detail.html', {'cu' : calUnit,
                                                             'locations' : locations})
def error(request): 
    """ This displays an error for incorrect barcode or unique id """
    return render(request, 'calibration_units/error.html')

def fieldView(request):
    """ This displays CU field data. """
    options = ["cu_number","cu_uid","qie_card","qie_card.uid","qie_card.b_fw","qie_card.i_top_fw", "qie_card.i_bot_fw","qie_card.status",
               "pulser_board","comments","last location"]
    fields = []
    for i in range(6):
        if(request.POST.get('field' + str(i+1))):
            field = request.POST.get('field' + str(i+1))
            if field in options:
                fields.append(field)

    cus = list(CalibrationUnit.objects.all().order_by("cu_number"))
    cards = list(QieCard.objects.all().order_by("barcode"))
    locs = CuLocation.objects.all().order_by("cu")
    items = []
    # Info for "Card Status"
    cache = path.join(MEDIA_ROOT, "cached_data/summary.json")
    infile = open(cache, "r")
    cardStat = json.load(infile)
    infile.close()
    num_required = len(Test.objects.filter(required=True))
    for i in xrange(len(cus)):
        cu = cus[i]
        item = {}
        item["id"] = cu.pk
        item["fields"] = []
        for field in fields:
            f_list = field.split(".")
            if field == "last location":    # Get CU last location
                loc_list = locs.filter(cu=cu).order_by("date_received")
                if len(loc_list) == 0:
                    item["fields"].append("No Locations Recorded")
                else:
                    item["fields"].append(loc_list.reverse()[0].geo_loc)
            elif f_list[-1] == "status":    # Get QIE Card status
                card = getattr(cu, f_list[0])
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
                card = getattr(cu, f_list[0])
                firmware = f_list[1]
                if firmware == "b_fw":      # Bridge firmware
                    item["fields"].append(card.get_bridge_ver_hex())
                elif firmware == "i_top_fw":    # Igloo top firmware
                    item["fields"].append(card.get_top_igloo_ver_hex())
                elif firmware == "i_bot_fw":    # Igloo bot firmware
                    item["fields"].append(card.get_bot_igloo_ver_hex())
            elif f_list[-1] == "uid":       # Get QIE Card unique id
                card = getattr(cu, f_list[0])
                item["fields"].append(card.uid)
            else:                           # Get CU attribute: CU number, unique id, QIE Card, Pulser Board, comments, last location
                item["fields"].append(getattr(cu, field))

        items.append(item)

    return render(request, 'calibration_units/fieldView.html', {'fields': fields, "items": items, "options": options})


