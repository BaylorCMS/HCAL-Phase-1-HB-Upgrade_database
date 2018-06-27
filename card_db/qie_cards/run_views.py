import sqlite3
from django.shortcuts import render
from django.views import generic
import datetime
from os import listdir, path
import json
from sets import Set

from .models import Run, QieCard, Tester, Test, Attempt, Location, QieShuntParams, Channel
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


def detail(request, run):
    """ This displays the cards and tests  corresponding to a run"""
    attempts   = list(Attempt.objects.filter(run=run).order_by('card__barcode'))
    test_types = list(Attempt.objects.filter(run=run).order_by('test_type__name'))
    cards = []
    tests = []
    for attempt in attempts:
        if attempt.card not in cards:
            cards.append(attempt.card)
        
    for attempt in test_types:
        if attempt.test_type not in tests:
            tests.append(attempt.test_type)
    
    
    
    return render(request, 'runs/detail.html', {'card_list': cards,'test_list': tests})


