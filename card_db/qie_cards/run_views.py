import sqlite3
from django.shortcuts import render
from django.views import generic
from django.http import HttpResponseRedirect
import datetime
from os import listdir, path
import json
from sets import Set

from .models import Run, QieCard, Tester, Test, Attempt, Location, QieShuntParams, Channel
from .run_form import AttemptForm

import custom.filters as filters

# Create your views here.

from django.utils import timezone
from django.http import HttpResponse, Http404
from card_db.settings import MEDIA_ROOT, CACHE_DATA 
from django.core.exceptions import MultipleObjectsReturned


def catalog(request):
    """This displays a list of all runs"""

    runs = Run.objects.all().order_by('number')
    count = len(runs)

    return render(request, 'runs/catalog.html', {'run_list': runs,
                                                 'total_count': count})


def detail(request, run):
    """ This displays the cards and tests  corresponding to a run"""
    card_names   = list(Attempt.objects.filter(run=run).order_by('card__barcode'))
    test_types = list(Attempt.objects.filter(run=run).order_by('test_type__name'))
    

    cards = []
    tests = []
    for attempt in card_names:
        if attempt.card not in cards:
            cards.append(attempt.card)
    attempts_temp = []
    for card in cards:
    #    attemptList = Attempt.objects.filter(card__barcode=card.barcode, run=run, test_type__name='Plot Inspection').last()
    #    if attemptList:
    #        attempts.append(attemptList)

        attempts_temp.append(Attempt.objects.filter(run=run, card=card).last())#, test_type__name ='Plot Inspection' ).last())
    #attempts.order_by('card__barcode')
    
    attempts = []
    for attempt in attempts_temp:
        if attempt.test_type == Test.objects.get(name='Plot Inspection'):
            attempts.append({"attempt":attempt, "valid":True})
        else:
            attempts.append({"attempt":attempt, "valid":False})

    for attempt in test_types:
        if attempt.test_type not in tests:
            tests.append(attempt.test_type)
    
    
    return render(request, 'runs/detail.html', {'card_list': cards,'test_list': tests, 'run': run, 'attempt_list': attempts})

CHANNEL_MAPPING= {"Top": {"0": 1, "1": 2, "2": 3, "3": 4, "4": 5, "5": 6, "6": 7, "7": 8},
                  "Bot": {"0": 9, "1": 10, "2": 11, "3": 12, "4": 13, "5": 14, "6": 15, "7": 16}}

def getChannel(num, channels):
    """This function grabs the right channel out of a list of channels and returns that channel"""
    for channel in channels:
        if num == channel.number:
            return channel

def card_plots(request, run, card):
    """This displays the test plots relating to a card"""
    test_types = list(Attempt.objects.filter(run=run).order_by('test_type__name'))
    tests = []
    for attempt in test_types:
        if attempt.test_type not in tests:
            tests.append(attempt.test_type)
    testers = Tester.objects.all()
    attempts = []
    for test in tests:
        attempts.append(Attempt.objects.filter(run=run, card__barcode=card, test_type=test).last())

    if request.method == 'POST':

        attempt_list = list(Attempt.objects.filter(card__barcode = card, test_type__name ='Plot Inspection'))
        attempt_number = len(attempt_list) + 1 

        if 'pass' in request.POST.keys():
            form = AttemptForm(request.POST)
            
            if form.is_valid():
                post = form.save(commit=False)
                post.run = run
                post.card = QieCard.objects.get(barcode=str(card))
                post.result = True
                post.test_type = Test.objects.get(name='Plot Inspection')
                #post.tester = Tester.objects.get(username='Bryan Caraway')
                post.tester = Tester.objects.get(username=request.POST['testers'])
                #post.tester_id = 39
                post.date_tested = timezone.now()
                post.attempt_number = attempt_number
                post.save()
                return HttpResponseRedirect('../')
        
        if 'fail' in request.POST.keys():
            form = AttemptForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.run = run
                post.card = QieCard.objects.get(barcode=str(card))
                post.result = False
                post.test_type = Test.objects.get(name='Plot Inspection')
                #post.tester = Tester.objects.get(username='Bryan Caraway')
                post.tester_id = 39
                post.date_tested = timezone.now()
                post.attempt_number = attempt_number
                post.save()
                return HttpResponseRedirect('../')
  
        for attempt in attempt_list:
            attempt.revoked = True
            attempt.save()

    else:
        form = AttemptForm()
    

   
    attemptData = []
    for attempt in attempts:
        data = ""
        num_list = []
        num_var_list = {}
        if attempt:
            if attempt.num_channels_passed != 0 or attempt.num_channels_failed != 0:
                if not str(attempt.hidden_log_file) == "default.png":
                    inFile = open(path.join(MEDIA_ROOT, str(attempt.hidden_log_file)), "r")
                    tempDict = json.load(inFile)
                    rawUID = tempDict["Unique_ID"]
                    channel_list = []
                    for position in tempDict[rawUID]:
                        for channel in tempDict[rawUID][position]:
                            channel_num = CHANNEL_MAPPING[position][channel[-1]]
                            num_var_list[channel_num] =  tempDict[rawUID][position][channel][attempt.test_type.name]
                            num_list.append(CHANNEL_MAPPING[position][channel[-1]])
                            new_chan = Channel(number=CHANNEL_MAPPING[position][channel[-1]])
                            channel_list.append(new_chan)      
                            
                    num_list.sort()
                            
                    o_channel_list = {}
                    for i in num_list:
                        channel = getChannel(i, channel_list)
                        o_channel_list[channel.number] = num_var_list[i]    # Ordered dictionary of channel objects with their variables and values
                        data += channel.get_number_display() + ": \n"
                        for variable in o_channel_list[channel.number]:
                            value = o_channel_list[channel.number][variable][0]
                            result = o_channel_list[channel.number][variable][1]
                            data += "\t" + variable + ": " + str(value) + ", "
                            if result == 0:
                                data += "FAIL"
                            else:
                                data += "PASS"
                            data += "\n"    
                        data += "\n"
                                
            attemptData.append((attempt, data))

    return render(request, 'runs/card_plots.html', {'test_list': tests, 'attempt_list': attempts, 'testers': testers, 'form': form, 'attempts': attemptData, 'card':card}) 

def test_plots(request, run, test):
    """This displays the plots relating tied to a specific test"""
    card_names = list(Attempt.objects.filter(run=run).order_by('card__barcode'))
    cards = []
    for attempt in card_names:
        if attempt.card not in cards:
            cards.append(attempt.card)

    attempts = []
    for card in cards:
        attempts.append(Attempt.objects.filter(run=run, test_type__name=test, card__barcode=card).last())

    return render(request, 'runs/test_plots.html', {'card_list': cards, 'attempt_list': attempts})

        
