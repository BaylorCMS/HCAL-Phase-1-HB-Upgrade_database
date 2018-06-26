import sqlite3
from django.shortcuts import render
from django.views import generic
import datetime
from os import listdir, path
import json
from sets import Set

from .models import Run #QieCard, Tester, Test, Attempt, Location, QieShuntParams, Channel
import custom.filters as filters

# Create your views here.

from django.utils import timezone
from django.http import HttpResponse, Http404
from card_db.settings import MEDIA_ROOT, CACHE_DATA 


def catalog(request):
    """This displays a list of all runs"""

    runs = Run.objects.all().order_by('number')
    count = len(runs)

    return render(request, 'runs/catalog.html', {'run_list': runs,
                                                 'total_count': count})


