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
import operator
# Create your views here.

from django.utils import timezone
from django.http import HttpResponse, Http404
from card_db.settings import MEDIA_ROOT, CACHE_DATA 
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction


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

@transaction.atomic
def set_card_status(qiecard):
    tests = Test.objects.all()
    status = {}
    status["total"] = len(tests.filter(required=True))
    status["passed"] = 0
    failedAny = False
    no_result = False

    for test in tests:
        attemptList = Attempt.objects.filter(card=qiecard.pk, test_type = test.pk).order_by("attempt_number")
        if attemptList:
            last = attemptList[len(attemptList) - 1]
            if not last.revoked and test.required:
                if last.overwrite_pass:
                    status["passed"] += 1
                elif last.passed():
                    status["passed"] += 1
                elif last.empty_test():
                    no_result = True
                else:
                    failedAny = True

    if status["total"] == status["passed"]:
        qiecard.status = True
    elif failedAny:
        qiecard.status = False
    elif no_result:
        qiecard.status = None
    else:
        qiecard.status = None

    qiecard.save()
 

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
        if test.name != "Plot Inspection":
            attempts.append(Attempt.objects.filter(run=run, card__barcode=card, test_type=test).last())

    if request.method == 'POST':

        attempt_list = list(Attempt.objects.filter(card__barcode = card, test_type__name ='Plot Inspection'))
        attempt_number = len(attempt_list) + 1 
        #try: 
        #    edit_attempt = Attempt.objects.get(card__barcode=card, test_type__name='Plot Inspection', run=run) 
        #except
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
                post.tester = Tester.objects.get(username=request.POST['testers'])
                #post.tester_id = 39
                post.date_tested = timezone.now()
                post.attempt_number = attempt_number
                post.save()
                return HttpResponseRedirect('../')
  
        for attempt in attempt_list:
            attempt.revoked = True
            attempt.save()

        set_card_status(card)

    else:
        form = AttemptForm()
    

   
    attemptData = []
    for attempt in attempts:
        data = ""
        num_list = []
        num_var_list = {}
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

        

def calibration(request):

    attempt_list = Attempt.objects.filter( test_type__name="Calibration" ).order_by("-date_tested")

    date_list = []
    dict_date = {}
    for attempt in attempt_list:
        if  (attempt.date_tested.date()).strftime("%m-%d-%Y") not in date_list:
            date_list.append((attempt.date_tested.date()).strftime("%m-%d-%Y"))
            
    for date in date_list:
        dict_date[date] = []
        split_date = date.split("-")
        temp_list = list(Attempt.objects.filter(test_type__name="Calibration", date_tested__year=split_date[2], date_tested__month=split_date[0], date_tested__day=split_date[1]).order_by("cal_run"))
        for a in temp_list:
            if a.cal_run not in dict_date[date]:
                dict_date[date].append(a.cal_run)

    return render(request, 'runs/calibration.html', {"dict_date":dict_date, "dates":date_list})


def cal_detail(request, date, run):
    """ This displays the cards and tests  corresponding to a calibration run"""
    split_date = date.split("-")
    card_names   = list(Attempt.objects.filter(cal_run=run, date_tested__year=split_date[2], date_tested__month=split_date[0], date_tested__day=split_date[1]).order_by('card__barcode'))
    # test_types = list(Attempt.objects.filter(run=run))
    

    cards = []
    #tests = []
    for attempt in card_names:
        if attempt.card not in cards:
            cards.append(attempt.card)
    attempts_temp = []
    firefly_id = date + "-" + str(run)
    for card in cards:
    #    attemptList = Attempt.objects.filter(card__barcode=card.barcode, run=run, test_type__name='Plot Inspection').last()
    #    if attemptList:
    #        attempts.append(attemptList)
        
        attempts_temp.append(Attempt.objects.filter(cal_run=run, card=card, date_id=firefly_id).last()) #date_tested__year=split_date[2], date_tested__month=split_date[0], date_tested__day=split_date[1]).last())#, test_type__name ='Plot Inspection' ).last())
    #attempts.order_by('card__barcode')
    
    attempts = []
    for attempt in attempts_temp:
        if attempt.test_type == Test.objects.get(name='Calibration Plot Inspection'):
            
            attempts.append({"attempt":attempt, "valid":True})
        else:
            attempts.append({"attempt":attempt, "valid":False})

   # for attempt in test_types:
   #     if attempt.test_type not in tests:
   #         tests.append(attempt.test_type)
    
    

    return render(request, 'runs/cal_detail.html', {'date': date, 'cal_run': run, 'card_list': cards, 'attempt_list': attempts})



def cal_plots(request, date, run, card):
    
    split_date = date.split("-")
    attempt = Attempt.objects.filter(test_type__name="Calibration", card__barcode = card,  date_tested__year=split_date[2], date_tested__month=split_date[0], date_tested__day=split_date[1], cal_run=int(run)).last()
    testers = Tester.objects.all()
    #barcode_list = []
    #plot_list = []
    #for attempt in attempt_list:
    #    if attempt.card.barcode not in barcode_list:
    #        barcode_list.append(attempt.card.barcode)

    
    #plot_list.append(Attempt.objects.filter(test_type__name="Calibration",  date_tested__year=split_date[2], date_tested__month=split_date[0], date_tested__day=split_date[1], cal_run=int(run), card__barcode = barcode).last())
    if request.method == "POST":
        firefly_id = date + "-" + str(run)
        if 'pass' in request.POST.keys():
            
            prev_attempts = list(Attempt.objects.filter(card__barcode=card, 
                                                        cal_run=run, 
                                                        test_type__name="Calibration Plot Inspection"))
            attempt_num = len(prev_attempts) + 1
            temp_attempt = Attempt(result=True,
                                   tester=Tester.objects.get(username=request.POST.get('testers')),
                                   comments=request.POST.get('comments'),
                                   test_type=Test.objects.get(name="Calibration Plot Inspection"),
                                   date_tested=timezone.now(),
                                   cal_run=int(run),
                                   attempt_number=attempt_num,
                                   card=QieCard.objects.get(barcode=card),
                                   date_id=firefly_id
                                   )
            temp_attempt.save()
            for a in prev_attempts:
                a.revoked = True
                a.save()
            set_card_status(QieCard.objects.get(barcode=card))
        
            return HttpResponseRedirect('../')        

        if 'fail' in request.POST.keys():
            prev_attempts = list(Attempt.objects.filter(card__barcode=card, 
                                                        cal_run=run, 
                                                        test_type__name="Calibration Plot Inspection"))
            attempt_num = len(prev_attempts) + 1
            temp_attempt = Attempt(result=False,
                                   tester=Tester.objects.get(username=request.POST.get('testers')),
                                   comments=request.POST.get('comments'),
                                   test_type=Test.objects.get(name="Calibration Plot Inspection"),
                                   date_tested=timezone.now(),
                                   cal_run=run,
                                   attempt_number = attempt_num,
                                   card=QieCard.objects.get(barcode=card),
                                   date_id=firefly_id
                                   )
            temp_attempt.save()
            for a in prev_attempts:
                a.revoked = True
                a.save()
            set_card_status(QieCard.objects.get(barcode=card))
            return HttpResponseRedirect('../')
        
    return render(request, 'runs/cal_plots.html', {"attempt":attempt, "testers": testers})






