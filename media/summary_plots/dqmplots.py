#!/usr/bin/env python
# Create DQM plots for the HB testing
# For ROOT, source /home/daqowner/dist/etc/env.sh

import os,sys
from string import *
from ROOT import *
import django
import json

import random
sys.path.insert(0,'/home/django/testing_database_hb/card_db')
django.setup()

print '*** Script to produce summary plots for the HB QIE tests at WH, July 2018.'
print 'Can run in batch mode (python dqmplots.py -b) to suppress runtime graphics.' 

# Draw histograms
def draw1(h, hp, hf, hn, vn, vt):

    h.SetLineWidth(2)
    hp.SetLineColor(kGreen+1)
    hp.SetFillColor(kGreen+1)
    #hp.SetLineStyle(2)
    hf.SetLineColor(kRed)
    hf.SetFillColor(kRed)
    #hf.SetLineStyle(2)

    hs = THStack(hn+'_s', '')
    hs.Add(hf)
    hs.Add(hp)
    SetOwnership(hs, 0 )

    np = hp.Integral()
    nf = hf.Integral()

    hs.SetMaximum(1.5*hs.GetMaximum())
    #h.SetMinimum(0)
    h.SetTitle("")
    h.GetXaxis().SetTitle(vn)
    #h.GetXa`xis().CenterTitle()
    h.GetXaxis().SetTitleOffset(1.25)
    h.GetXaxis().SetTitleSize(0.055)
    h.GetXaxis().SetTitleFont(42)
    h.GetXaxis().SetLabelOffset(0.012)
    h.GetXaxis().SetLabelSize(0.050)
    h.GetXaxis().SetLabelFont(42)
    h.GetXaxis().SetNdivisions(8, 5, 0)
    h.GetYaxis().SetTitle("Number of tests")
    #h.GetYaxis().CenterTitle()
    #h.GetYaxis().SetTitleOffset(1.05)
    h.GetYaxis().SetTitleSize(0.055)
    h.GetYaxis().SetTitleFont(42)
    #h.GetYaxis().SetNdivisions(0, 0, 0)
    h.Draw()
    hs.Draw('same')
    h.Draw('same')
    #h.Draw('same')

    nbins = h.GetNbinsX()
    # Make the title
    t = TLatex(0.65, 0.84, vt)
    if (h.GetMaximumBin() > nbins/2):
        t = TLatex(0.13, 0.84, vt)
    t.SetTextSize(0.042)
    t.SetTextFont(42)
    t.SetNDC()
    t.Draw("same")
    SetOwnership(t, 0)

    # Make the histogram legend
    l = TLegend(0.61, 0.66, 0.88, 0.82)
    if (h.GetMaximumBin() > nbins/2):
        l = TLegend(0.13, 0.66, 0.40, 0.82)        
    l.SetBorderSize(0)
    l.SetFillStyle(0000)
    l.AddEntry(h,'all', 'l')
    l.AddEntry(hp,'pass: '+str(np), 'f')
    l.AddEntry(hf,'fail: '+str(nf), 'f')
    l.Draw("same")
    SetOwnership(l, 0 )

def draw2(hvsqie, hn, vn, vt):
    hvsqie.SetTitle("")
    hvsqie.GetXaxis().SetTitle("Channel #")
   #hvsqie.GetXaxis().CenterTitle()
    hvsqie.GetXaxis().SetTitleOffset(1.25)
    hvsqie.GetXaxis().SetTitleSize(0.055)
    hvsqie.GetXaxis().SetTitleFont(42)
    hvsqie.GetXaxis().SetLabelOffset(0.012)
    hvsqie.GetXaxis().SetLabelSize(0.050)
    hvsqie.GetXaxis().SetLabelFont(42)
    hvsqie.GetXaxis().SetNdivisions(8, 5, 0)
    hvsqie.GetYaxis().SetTitle(vn)
   #hvsqie.GetYaxis().CenterTitle()
   #hvsqie.GetYaxis().SetTitleOffset(1.05)
    hvsqie.GetYaxis().SetTitleSize(0.055)
    hvsqie.GetYaxis().SetTitleFont(42)
   #hvsqie.GetYaxis().SetNdivisions(0, 0, 0)
    hvsqie.Draw()

    nbins = h.GetNbinsX()
    # Make the title
    t = TLatex(0.65, 0.84, vt)
    if (h.GetMaximumBin() > nbins/2):
        t = TLatex(0.13, 0.84, vt)
    t.SetTextSize(0.042)
    t.SetTextFont(42)
    t.SetNDC()
    t.Draw("same")
    SetOwnership(t, 0)

    # Make the histogram legend
    l = TLegend(0.61, 0.66, 0.88, 0.82)
    if (h.GetMaximumBin() > nbins/2):
        l = TLegend(0.13, 0.66, 0.40, 0.82)
    l.SetBorderSize(0)
    l.SetFillStyle(0000)
    l.AddEntry(hvsqie, 'all', 'l')
    l.Draw("same")
    SetOwnership(l, 0 )

# Sezen's clean ROOT style:
gROOT.SetStyle('Plain')
gStyle.SetOptStat(kFALSE)
gStyle.SetPalette(1)
gStyle.SetTextFont(42)
gStyle.SetTitleStyle(0000)
gStyle.SetTitleBorderSize(0)

# Check later whether this is useful or not
from django.utils import timezone
from django.http import HttpResponse, Http404
from card_db.settings import MEDIA_ROOT 

# Import all model classes
from qie_cards.models import Test, Tester, Variable, QieCard, Channel, Attempt

print 'Processing variables... Selecting variables resulting from the latest attempts.'
variables = list(Variable.objects.filter(attempt__revoked=False))
nvariables = len(variables)
print 'Number of variables accessed:', len(variables)

# Find the test names and variables names
print 'Listing test names and variable names.'
varnames = []
vtests = []
nv = 0
#for v in variables:
#    nv = nv + 1
#    if v.name not in varnames:
#        varnames.append(v.name)
#    va = v.attempt
#    va = va.test_type
#    if va not in vtests:
#        vtests.append(va)
#    #if nv == 20000: break

varnames = [u'slope', u'chi2Fit1', u'y-intercept', u'timeConst2', u'timeConst1', u'switch3', u'switch2', u'switch1', u'switch4', u'sigma', u'mean', u'isIncreasing']
vtests = ['capID1pedestal', 'phaseScan', 'capID2pedestal', 'pedestalScan', 'iQiScan', 'capID3pedestal', 'capID0pedestal', 'gselScan', 'pedestal']

print '   Number of tests:', len(vtests)
print '   Number of variables:', len(varnames)

print 'Preparing histograms...'

# Find the histogram x-axis minima and maxima
vmin = []
for nt in range(len(vtests)):
    vmin0 = []
    for nv in range(len(varnames)):
        vmin0.append(9999.)
    vmin.append(vmin0)

vmax = []
for nt in range(len(vtests)):
    vmax0 = []
    for nv in range(len(varnames)):
        vmax0.append(-9999.)
    vmax.append(vmax0)


n = 0
for v in variables:
    va = v.attempt
    va = str(va.test_type)
    val = atof(v.value)
    n = n + 1
    #if n == 20000: break
    for nt in range(len(vtests)):
        for nv in range(len(varnames)):
            if v.name == varnames[nv] and va == vtests[nt]:
                #print v[0], nv, varnames[nv], nt, v[1], vtests[nt], v[2], vmin[nt][nv], vmax[nt][nv]
                if val <= vmin[nt][nv]: 
                    vmin[nt][nv] = val
                if val >= vmax[nt][nv]: 
                    vmax[nt][nv] = val

#print 'vmin:\n'
#for v in vmin:
#    print v
#print 'vmax:\n'
#for v in vmax:
#    print v


# Map histogram names to histograms and properties
vars = {}
# Book the histograms:
nbin = 60
r = 0.5
for nv in range(len(varnames)):
    for nt in range(len(vtests)):
        hn = 'h_'+str(varnames[nv])+'_'+str(vtests[nt]) 
        vdiff = abs(vmax[nt][nv] - vmin[nt][nv])
        if vdiff == 0: vdiff = vmax[nt][nv]
        h = TH1D(hn, hn, nbin, vmin[nt][nv]-r*vdiff, vmax[nt][nv]+r*vdiff)
        hp = TH1D(hn+'_p', hn+'_p', nbin, vmin[nt][nv]-r*vdiff, vmax[nt][nv]+r*vdiff)
        hf = TH1D(hn+'_f', hn+'_f', nbin, vmin[nt][nv]-r*vdiff, vmax[nt][nv]+r*vdiff)
        hvsqie = TH2D(hn+'_tp', hn+'_tp', 18, 0, 17, nbin, vmin[nt][nv]-r*vdiff, vmax[nt][nv]+r*vdiff)
        vars[hn] = h, hp, hf, hvsqie, str(varnames[nv]), str(vtests[nt]), vmin[nt][nv], vmax[nt][nv]
        
hnames = []
for hn in sorted(vars.iterkeys()):
    hnames.append(hn)

print 'Number of histograms prepared:', len(hnames)

print "Filling histograms..."
n = 0
m = 0
log = ""

empty = 0
bad = 0
total = 0
for v in variables:
    va = v.attempt
    n = n + 1
    hn = 'h_'+str(v.name)+'_'+str(va)
    h, hp, hf, hvsqie, vn, vt, vmin, vmax = vars[hn]
    if hn not in hnames or v.value < vmin-10*abs(vmin) or v.value > vmax+10*abs(vmax):
        print hn, v.value
        m = m + 1
    h.Fill(v.value)
    if v.test_pass == 1:
        hp.Fill(v.value)
    else:
        hf.Fill(v.value)
    #hvsqie.Fill(1.0, v.value)
    if (log != v.attempt.hidden_log_file):
        log = v.attempt.log_file
        with open("/home/django/testing_database_hb/media/"+str(log)) as f:
            logdata = json.load(f)
    repeat = False
    if (v.name == "slope"):
        i = 1
        total = total + 1
        hvsqie.Fill(random.randint(1,16),v.value)
        
        for elem in logdata:
            break
            if (i == 2):
                qie = 16
                for side in logdata[elem]:
                    for chan in logdata[elem][side]:
                        for test in logdata[elem][side][chan]:
                            try: 
                                if (logdata[elem][side][chan][slope] == v.value):
                                    if (repeat == False):
                                        hvsqie.Fill(qie, v.value)
                                        print (elem+"/"+side+"/"+side+"/"+chan+"/"+"slope: "+v.value+" at qie "+qie)
                                        repeat = True
                                    else: 
                                        bad = bad + 1
                                        print ("\n!!!!!ERROR!!!!!")
                                        print (elem+"/"+side+"/"+side+"/"+chan+"/"+"slope: "+v.value+" at qie "+qie)
                                        print ("Is a repeat of a previous element\n")
                            except NameError:
                                pass
                                    
                        qie = qie - 1
            i = i + 1
        if (repeat == False):
            empty = empty + 1
    print("iteration # "+str(n))
print ("Slopes finished: "+str(total)+" total, "+str(empty)+" with no match, "+str(bad)+" duplicate matches.")

print 'Drawing histograms...'
# Make a canvas and set its margins
c = TCanvas('c', 'c', 450, 400)
c.SetBottomMargin(0.15)
c.SetLeftMargin(0.13)
c.SetLogy(1)


for hn in sorted(vars.iterkeys()):
    #if ((hn / vars.iterkeys().length())%1 == 0):
    #    print (hn/vars.iterkeys().length() + '%')
    h, hp, hf, hvsqie, vn, vt, vmin, vmax = vars[hn]
    if h.Integral() == 0: continue
    #print h.GetName(), h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax()
    #print hp.GetName(), hp.GetXaxis().GetXmin(), hp.GetXaxis().GetXmax()
    #print hf.GetName(), hf.GetXaxis().GetXmin(), hf.GetXaxis().GetXmax()
    draw1(h, hp, hf, hn, vn, vt)
    # Save the file
    c.Print('plots/'+hn+'.png')
    draw2(hvsqie, hn, vn, vt)
    c.Print('plots/'+hn+'_q.png')

print 'Histograms saved to the plots directory.'
