#! /usr/bin/env python

import os, multiprocessing
import copy
import math
import numpy as np
from array import array
from ROOT import ROOT, gROOT, gStyle, gRandom, TSystemDirectory
from ROOT import TFile, TChain, TTree, TCut, TH1, TH1F, TH2F, THStack, TGraph, TGraphAsymmErrors, TF1
from ROOT import TStyle, TCanvas, TPad
from ROOT import TLegend, TLatex, TText, TLine, TBox

from variables import *

########## PARSER ##########

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-v", "--variable", action="store", type="string", dest="variable", default="digi_layer")
parser.add_option("-l", "--local", action="store_true", default=False, dest="local")
parser.add_option("-b", "--bash", action="store_true", default=False, dest="bash")
#parser.add_option("-s", "--super_layer", action="store", type="string", default="1", dest="super_layer")
(options, args) = parser.parse_args()
if options.bash: gROOT.SetBatch(True)

########## SETTINGS ##########

gStyle.SetOptStat(0)

LOCAL       = options.local
NTUPLEDIR   = "/home/lisa/GIFcode/GIF_code/ntuples_POA/" if LOCAL else "/eos/cms/store/group/dpg_dt/comm_dt/gif++_2017/POA/"
DATE        = '17_nov'
########## SAMPLES ##########
'''
16 nov
5856    20 mV     100k
5857    30 mV     100k
5858    40 mV     100k
5859    70 mV     116k

17 nov
5862    20          50k
5863    30          52k
5864    40          51k
5865    70          50k
5866   100         100k
5867   150         100k
5868   200         100k

'''

sign_sampl = {}

sign_sampl_31_oct = {
    'Th30' : {
        'files' : ['DTNtuple_GIF_r5742'],#threshold scan
        'run_number' : 5742,#threshold scan
        'threshold' : 30,
    },
    'Th20' : {
        'files' : ['DTNtuple_GIF_r5743'],#threshold scan
        'run_number' : 5743,#threshold scan
#        'files' : ['DTNtuple_GIF_r5753'],
#        'run_number' : 'r5753',
        'threshold' : 20,
    },
    'Th40' : {
        'files' : ['DTNtuple_GIF_r5744'],#threshold scan
        'run_number' : 5744,#threshold scan
        'threshold' : 40,
    },
    'Th100' : {
        'files' : ['DTNtuple_GIF_r5745'],#threshold scan
        'run_number' : 5745,#threshold scan
        'threshold' : 100,
    },
    'Th150' : {
        'files' : ['DTNtuple_GIF_r5746'],#threshold scan
        'run_number' : 5746,#threshold scan
        'threshold' : 150,
    },
}

sign_sampl_8_nov = {
    'Th30' : {
        'files' : ['DTNtuple_GIF_r5773'],#threshold scan
        'run_number' : 5773,#threshold scan
        'threshold' : 30,
    },
    'Th20' : {
        'files' : ['DTNtuple_GIF_r5774'],#threshold scan
        'run_number' : 5774,#threshold scan
        'threshold' : 20,
    },
    'Th40' : {
        'files' : ['DTNtuple_GIF_r5775'],#threshold scan
        'run_number' : 5775,#threshold scan
        'threshold' : 40,
    },
    'Th100' : {
        'files' : ['DTNtuple_GIF_r5776'],#threshold scan
        'run_number' : 5776,#threshold scan
        'threshold' : 100,
    },
    'Th150' : {
        'files' : ['DTNtuple_GIF_r5777'],#threshold scan
        'run_number' : 5777,#threshold scan
        'threshold' : 150,
    },
}


sign_sampl_9_nov = {
    'Th20' : {
        'files' : ['DTNtuple_GIF_r5807'],#threshold scan
        'run_number' : 5807,#threshold scan
        'threshold' : 20,
    },
    'Th30' : {
        'files' : ['DTNtuple_GIF_r5804'],#threshold scan
        'run_number' : 5804,#threshold scan
        'threshold' : 30,
    },
    'Th40' : {
        'files' : ['DTNtuple_GIF_r5808'],#threshold scan
        'run_number' : 5808,#threshold scan
        'threshold' : 40,
    },
    'Th70' : {
        'files' : ['DTNtuple_GIF_r5809'],#threshold scan
        'run_number' : 5809,#threshold scan
        'threshold' : 70,
    },
    'Th100' : {
        'files' : ['DTNtuple_GIF_r5810'],#threshold scan
        'run_number' : 5810,#threshold scan
        'threshold' : 100,
    },
    'Th150' : {
        'files' : ['DTNtuple_GIF_r5811'],#threshold scan
        'run_number' : 5811,#threshold scan
        'threshold' : 150,
    },
    'Th200' : {
        'files' : ['DTNtuple_GIF_r5812'],#threshold scan
        'run_number' : 5812,#threshold scan
        'threshold' : 200,
    },
}


sign_sampl_17_nov = {
    'Th20' : {
        'files' : ['DTNtuple_GIF_r5862'],#threshold scan
        'run_number' : 5862,#threshold scan
        'threshold' : 20,
    },
    'Th30' : {
        'files' : ['DTNtuple_GIF_r5863'],#threshold scan
        'run_number' : 5863,#threshold scan
        'threshold' : 30,
    },
    'Th40' : {
        'files' : ['DTNtuple_GIF_r5864'],#threshold scan
        'run_number' : 5864,#threshold scan
        'threshold' : 40,
    },
    'Th70' : {
        'files' : ['DTNtuple_GIF_r5865'],#threshold scan
        'run_number' : 5865,#threshold scan
        'threshold' : 70,
    },
    'Th100' : {
        'files' : ['DTNtuple_GIF_r5866'],#threshold scan
        'run_number' : 5866,#threshold scan
        'threshold' : 100,
    },
    'Th150' : {
        'files' : ['DTNtuple_GIF_r5867'],#threshold scan
        'run_number' : 5867,#threshold scan
        'threshold' : 150,
    },
    'Th200' : {
        'files' : ['DTNtuple_GIF_r5868'],#threshold scan
        'run_number' : 5868,#threshold scan
        'threshold' : 200,
    },
}

if DATE == "17_nov":
    sign_sampl = sign_sampl_17_nov
elif DATE == "9_nov":
    sign_sampl = sign_sampl_9_nov
elif DATE == "8_nov":
    sign_sampl = sign_sampl_8_nov
elif DATE == "31_oct":
    sign_sampl = sign_sampl_31_oct

run_on_files = []
for a in sorted(sign_sampl):
    run_on_files.append(a)

#run_on_files = ['Th20', 'Th30', 'Th40', 'Th100', 'Th150']


#################################
min_run = 10000000000000000000000
max_run = 0 
for l in run_on_files:
    min_run = min(min_run,int(sign_sampl[l]['run_number']))
    max_run = max(max_run,int(sign_sampl[l]['run_number']))
run_interval = 'r'+str(min_run)+'-r'+str(max_run)
print "Threshold scan performed in GIF++ runs ", run_interval
outpath = "/home/lisa/GIFcode/GIF_code/plots/" if LOCAL else "plots/"
NORM = False
if options.variable == "digi_layer":
    NORM = True

########## INITIALIZATION #############

scan_SL1_L1 = {}
scan_SL1_L2 = {}
scan_SL1_L3 = {}
scan_SL1_L4 = {}
chain = {}
hist = {}
hist_counter = {}
can = {}
can_SL1 = {}
can_SL2 = {}
can_SL3 = {}
hist_SL1_L1 = {}
hist_SL1_L2 = {}
hist_SL1_L3 = {}
hist_SL1_L4 = {}

hist_SL2_L1 = {}
hist_SL2_L2 = {}
hist_SL2_L3 = {}
hist_SL2_L4 = {}

hist_SL3_L1 = {}
hist_SL3_L2 = {}
hist_SL3_L3 = {}
hist_SL3_L4 = {}
#cut = ""
#cut_SL1 = "digi_sl==1"
#cut_SL2 = "digi_sl==2"
#cut_SL3 = "digi_sl==3"

cut = "digi_time<=2800"
cut_L1 = "digi_layer == 1"
cut_L2 = "digi_layer == 2"
cut_L3 = "digi_layer == 3"
cut_L4 = "digi_layer == 4"
SL1 = "digi_sl==1 && digi_time<=2800"
SL2 = "digi_sl==2 && digi_time<=2800"
SL3 = "digi_sl==3 && digi_time<=2800"
cut_SL1_L1 = SL1 + " && " + cut_L1
cut_SL1_L2 = SL1 + " && " + cut_L2
cut_SL1_L3 = SL1 + " && " + cut_L3
cut_SL1_L4 = SL1 + " && " + cut_L4
cut_SL2_L1 = SL2 + " && " + cut_L1
cut_SL2_L2 = SL2 + " && " + cut_L2
cut_SL2_L3 = SL2 + " && " + cut_L3
cut_SL2_L4 = SL2 + " && " + cut_L4
cut_SL3_L1 = SL3 + " && " + cut_L1
cut_SL3_L2 = SL3 + " && " + cut_L2
cut_SL3_L3 = SL3 + " && " + cut_L3
cut_SL3_L4 = SL3 + " && " + cut_L4

######### ROUTINE ############
if variable[options.variable]['nbins']<=0:
    print "Not a valid bin range for variable"
    exit()
for s in run_on_files:
    chain[s] = TChain("DTTree")
    for j,ss in enumerate(sign_sampl[s]['files']):
        print "ss: ", ss
        chain[s].Add(NTUPLEDIR + ss + ".root")
        hist_SL1_L1[s] = TH1F(s+"_SL1_L1", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL1_L2[s] = TH1F(s+"_SL1_L2", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL1_L3[s] = TH1F(s+"_SL1_L3", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL1_L4[s] = TH1F(s+"_SL1_L4", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])

        hist_SL2_L1[s] = TH1F(s+"_SL2_L1", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL2_L2[s] = TH1F(s+"_SL2_L2", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL2_L3[s] = TH1F(s+"_SL2_L3", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL2_L4[s] = TH1F(s+"_SL2_L4", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])

        hist_SL3_L1[s] = TH1F(s+"_SL3_L1", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL3_L2[s] = TH1F(s+"_SL3_L2", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL3_L3[s] = TH1F(s+"_SL3_L3", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL3_L4[s] = TH1F(s+"_SL3_L4", ";"+variable[options.variable]['title'], variable[options.variable]['nbins'], variable[options.variable]['min'], variable[options.variable]['max'])


        hist_SL1_L1[s].Sumw2()
        hist_SL1_L2[s].Sumw2()
        hist_SL1_L3[s].Sumw2()
        hist_SL1_L4[s].Sumw2()

        hist_SL2_L1[s].Sumw2()
        hist_SL2_L2[s].Sumw2()
        hist_SL2_L3[s].Sumw2()
        hist_SL2_L4[s].Sumw2()

        hist_SL3_L1[s].Sumw2()
        hist_SL3_L2[s].Sumw2()
        hist_SL3_L3[s].Sumw2()
        hist_SL3_L4[s].Sumw2()

        #n of entries for normalization
        #nentries = chain[s].GetEntriesFast()
	#nentries = 2800#250000
	#print "nentries: ", nentries
	#print "\n"
	#print "!!!!NENTRIES HARDCODED!!!!!"
        #print "\n"

        chain[s].Project(s+"_counter", options.variable, cut)
        nentries = chain[s].GetEntriesFast()
	print "nentries: ", nentries
	print "\n"
        
	fconst = TF1("fconst","[0]",variable[options.variable]['min'], variable[options.variable]['max'])
        time_box = 2800
        normalization = (time_box*1.e-09*1.e03)
        #print normalization
        #normalization = 357
        average_wire = 59
	fconst.SetParameter(0,nentries*average_wire*(normalization))

        chain[s].Project(s+"_SL1_L1", options.variable, cut_SL1_L1)
        hist_SL1_L1[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())
        chain[s].Project(s+"_SL1_L2", options.variable, cut_SL1_L2)
        hist_SL1_L2[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())
        chain[s].Project(s+"_SL1_L3", options.variable, cut_SL1_L3)
        hist_SL1_L3[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())
        chain[s].Project(s+"_SL1_L4", options.variable, cut_SL1_L4)
        hist_SL1_L4[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())

        chain[s].Project(s+"_SL2_L1", options.variable, cut_SL2_L1)
        hist_SL2_L1[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())
        chain[s].Project(s+"_SL2_L2", options.variable, cut_SL2_L2)
        hist_SL2_L2[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())
        chain[s].Project(s+"_SL2_L3", options.variable, cut_SL2_L3)
        hist_SL2_L3[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())
        chain[s].Project(s+"_SL2_L4", options.variable, cut_SL2_L4)
        hist_SL2_L4[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())

        chain[s].Project(s+"_SL3_L1", options.variable, cut_SL3_L1)
        hist_SL3_L1[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())
        chain[s].Project(s+"_SL3_L2", options.variable, cut_SL3_L2)
        hist_SL3_L2[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())
        chain[s].Project(s+"_SL3_L3", options.variable, cut_SL3_L3)
        hist_SL3_L3[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())
        chain[s].Project(s+"_SL3_L4", options.variable, cut_SL3_L4)
        hist_SL3_L4[s].SetOption("%s" % chain[s].GetTree().GetEntriesFast())

        #normalization
	if NORM:
	    hist_SL1_L1[s].Divide(fconst)
	    hist_SL1_L2[s].Divide(fconst)
	    hist_SL1_L3[s].Divide(fconst)
	    hist_SL1_L4[s].Divide(fconst)

	    hist_SL2_L1[s].Divide(fconst)
	    hist_SL2_L2[s].Divide(fconst)
	    hist_SL2_L3[s].Divide(fconst)
	    hist_SL2_L4[s].Divide(fconst)

	    hist_SL3_L1[s].Divide(fconst)
	    hist_SL3_L2[s].Divide(fconst)
	    hist_SL3_L3[s].Divide(fconst)
	    hist_SL3_L4[s].Divide(fconst)

        scan_SL1_L1[sign_sampl[s]['threshold']] = hist_SL1_L1[s].GetBinContent(1)
        print s, sign_sampl[s]['threshold'], scan_SL1_L1[sign_sampl[s]['threshold']]
        scan_SL1_L2[sign_sampl[s]['threshold']] = hist_SL1_L2[s].GetBinContent(2)
        print s, sign_sampl[s]['threshold'], scan_SL1_L2[sign_sampl[s]['threshold']]
        scan_SL1_L3[sign_sampl[s]['threshold']] = hist_SL1_L3[s].GetBinContent(3)
        print s, sign_sampl[s]['threshold'], scan_SL1_L3[sign_sampl[s]['threshold']]
        scan_SL1_L4[sign_sampl[s]['threshold']] = hist_SL1_L4[s].GetBinContent(4)
        print s, sign_sampl[s]['threshold'], scan_SL1_L4[sign_sampl[s]['threshold']]
        
	#properly set the maximum y-axis of the histograms
        yax_SL1 = max(hist_SL1_L1[s].GetMaximum(),hist_SL1_L2[s].GetMaximum())
        yax_SL1 = max(yax_SL1, hist_SL1_L3[s].GetMaximum())
        yax_SL1 = max(yax_SL1, hist_SL1_L4[s].GetMaximum())

        yax_SL2 = max(hist_SL2_L1[s].GetMaximum(),hist_SL2_L2[s].GetMaximum())
        yax_SL2 = max(yax_SL2, hist_SL2_L3[s].GetMaximum())
        yax_SL2 = max(yax_SL2, hist_SL2_L4[s].GetMaximum())

        yax_SL3 = max(hist_SL3_L1[s].GetMaximum(),hist_SL3_L2[s].GetMaximum())
        yax_SL3 = max(yax_SL3, hist_SL3_L3[s].GetMaximum())
        yax_SL3 = max(yax_SL3, hist_SL3_L4[s].GetMaximum())

	#Plot SL1
	can_SL1[s] = TCanvas("can_SL1","can_SL1", 1000, 800)
	can_SL1[s].SetGrid()
	can_SL1[s].cd()
        hist_SL1_L1[s].SetMarkerSize(1.)
        hist_SL1_L1[s].SetMarkerStyle(21)
        hist_SL1_L1[s].SetMarkerColor(15)
        hist_SL1_L1[s].SetFillColor(15)
        hist_SL1_L1[s].SetFillStyle(0)
        hist_SL1_L1[s].SetLineColor(15)
        hist_SL1_L1[s].SetLineWidth(3)
        hist_SL1_L1[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL1_L1[s].GetYaxis().SetTitle("counts")
        hist_SL1_L1[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL1_L1[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL1_L1[s].SetMaximum(yax_SL1*(1.05))
        hist_SL1_L1[s].Draw("HISTO")

        hist_SL1_L2[s].SetMarkerSize(1.)
        hist_SL1_L2[s].SetMarkerStyle(21)
        hist_SL1_L2[s].SetMarkerColor(418)
        hist_SL1_L2[s].SetFillColor(418)
        hist_SL1_L2[s].SetFillStyle(0)
        hist_SL1_L2[s].SetLineColor(418)
        hist_SL1_L2[s].SetLineWidth(3)
        hist_SL1_L2[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL1_L2[s].GetYaxis().SetTitle("counts")
        hist_SL1_L2[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL1_L2[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL1_L2[s].Draw("HISTO,sames")

        hist_SL1_L3[s].SetMarkerSize(1.)
        hist_SL1_L3[s].SetMarkerStyle(21)
        hist_SL1_L3[s].SetMarkerColor(866)
        hist_SL1_L3[s].SetFillColor(866)
        hist_SL1_L3[s].SetFillStyle(0)
        hist_SL1_L3[s].SetLineColor(866)
        hist_SL1_L3[s].SetLineWidth(3)
        hist_SL1_L3[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL1_L3[s].GetYaxis().SetTitle("counts")
        hist_SL1_L3[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL1_L3[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL1_L3[s].Draw("HISTO,sames")

        hist_SL1_L4[s].SetMarkerSize(1.)
        hist_SL1_L4[s].SetMarkerStyle(21)
        hist_SL1_L4[s].SetMarkerColor(801)
        hist_SL1_L4[s].SetFillColor(801)
        hist_SL1_L4[s].SetFillStyle(0)
        hist_SL1_L4[s].SetLineColor(801)
        hist_SL1_L4[s].SetLineWidth(3)
        hist_SL1_L4[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL1_L4[s].GetYaxis().SetTitle("counts")
        hist_SL1_L4[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL1_L4[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL1_L4[s].Draw("HISTO,sames")

        leg_SL1 = TLegend(0.7, 0.7, 0.9, 0.9)
        leg_SL1.SetBorderSize(0)
        leg_SL1.SetFillStyle(0)
        leg_SL1.SetFillColor(0)
        leg_SL1.AddEntry(hist_SL1_L1[s], "SL1_L1", 'L')
        leg_SL1.AddEntry(hist_SL1_L2[s], "SL1_L2", 'L')
        leg_SL1.AddEntry(hist_SL1_L3[s], "SL1_L3", 'L')
        leg_SL1.AddEntry(hist_SL1_L4[s], "SL1_L4", 'L')
        #leg.AddEntry(hist[s], "", 'L')
        leg_SL1.Draw()

        latex = TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.04)
        latex.SetTextColor(1)
        latex.SetTextFont(42)
        latex.SetTextAlign(33)
        latex.DrawLatex(0.9, 0.96, "run n. %.0f (2017)" % (float(ss[14:])))
        latex.SetTextSize(0.04)
        latex.SetTextFont(62)
        latex.DrawLatex(0.30, 0.96, "GIF++")

    	can_SL1[s].Update()
    	can_SL1[s].Print(outpath + "Test_r" + str(sign_sampl[s]['run_number']) + "_" + str(options.variable)  + "_SL1.png")
    	can_SL1[s].Print(outpath + "Test_r" + str(sign_sampl[s]['run_number']) + "_" + str(options.variable)  + "_SL1.pdf")
    	can_SL1[s].Close()

	#Plot SL2
	can_SL2[s] = TCanvas("can_SL2","can_SL2", 1000, 800)
	can_SL2[s].SetGrid()
	can_SL2[s].cd()
        hist_SL2_L1[s].SetMarkerSize(1.)
        hist_SL2_L1[s].SetMarkerStyle(21)
        hist_SL2_L1[s].SetMarkerColor(15)
        hist_SL2_L1[s].SetFillColor(15)
        hist_SL2_L1[s].SetFillStyle(0)
        hist_SL2_L1[s].SetLineColor(15)
        hist_SL2_L1[s].SetLineWidth(3)
        hist_SL2_L1[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL2_L1[s].GetYaxis().SetTitle("counts")
        hist_SL2_L1[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL2_L1[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL2_L1[s].SetMaximum(yax_SL2*(1.05))
        hist_SL2_L1[s].Draw("HISTO")

        hist_SL2_L2[s].SetMarkerSize(1.)
        hist_SL2_L2[s].SetMarkerStyle(21)
        hist_SL2_L2[s].SetMarkerColor(418)
        hist_SL2_L2[s].SetFillColor(418)
        hist_SL2_L2[s].SetFillStyle(0)
        hist_SL2_L2[s].SetLineColor(418)
        hist_SL2_L2[s].SetLineWidth(3)
        hist_SL2_L2[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL2_L2[s].GetYaxis().SetTitle("counts")
        hist_SL2_L2[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL2_L2[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL2_L2[s].Draw("HISTO,sames")

        hist_SL2_L3[s].SetMarkerSize(1.)
        hist_SL2_L3[s].SetMarkerStyle(21)
        hist_SL2_L3[s].SetMarkerColor(866)
        hist_SL2_L3[s].SetFillColor(866)
        hist_SL2_L3[s].SetFillStyle(0)
        hist_SL2_L3[s].SetLineColor(866)
        hist_SL2_L3[s].SetLineWidth(3)
        hist_SL2_L3[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL2_L3[s].GetYaxis().SetTitle("counts")
        hist_SL2_L3[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL2_L3[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL2_L3[s].Draw("HISTO,sames")

        hist_SL2_L4[s].SetMarkerSize(1.)
        hist_SL2_L4[s].SetMarkerStyle(21)
        hist_SL2_L4[s].SetMarkerColor(801)
        hist_SL2_L4[s].SetFillColor(801)
        hist_SL2_L4[s].SetFillStyle(0)
        hist_SL2_L4[s].SetLineColor(801)
        hist_SL2_L4[s].SetLineWidth(3)
        hist_SL2_L4[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL2_L4[s].GetYaxis().SetTitle("counts")
        hist_SL2_L4[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL2_L4[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL2_L4[s].Draw("HISTO,sames")

        leg_SL2 = TLegend(0.7, 0.7, 0.9, 0.9)
        leg_SL2.SetBorderSize(0)
        leg_SL2.SetFillStyle(0)
        leg_SL2.SetFillColor(0)
        leg_SL2.AddEntry(hist_SL2_L1[s], "SL2_L1", 'L')
        leg_SL2.AddEntry(hist_SL2_L2[s], "SL2_L2", 'L')
        leg_SL2.AddEntry(hist_SL2_L3[s], "SL2_L3", 'L')
        leg_SL2.AddEntry(hist_SL2_L4[s], "SL2_L4", 'L')
        #leg.AddEntry(hist[s], "", 'L')
        leg_SL2.Draw()

        latex = TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.04)
        latex.SetTextColor(1)
        latex.SetTextFont(42)
        latex.SetTextAlign(33)
        latex.DrawLatex(0.9, 0.96, "run n. %.0f (2017)" % (float(ss[14:])))
        latex.SetTextSize(0.04)
        latex.SetTextFont(62)
        latex.DrawLatex(0.30, 0.96, "GIF++")

    	can_SL2[s].Update()
    	can_SL2[s].Print(outpath + "Test_r" + str(sign_sampl[s]['run_number']) + "_" + str(options.variable)  + "_SL2.png")
    	can_SL2[s].Print(outpath + "Test_r" + str(sign_sampl[s]['run_number']) + "_" + str(options.variable)  + "_SL2.pdf")
    	can_SL2[s].Close()

	#Plot SL3
	can_SL3[s] = TCanvas("can_SL3","can_SL3", 1000, 800)
	can_SL3[s].SetGrid()
	can_SL3[s].cd()
        hist_SL3_L1[s].SetMarkerSize(1.)
        hist_SL3_L1[s].SetMarkerStyle(21)
        hist_SL3_L1[s].SetMarkerColor(15)
        hist_SL3_L1[s].SetFillColor(15)
        hist_SL3_L1[s].SetFillStyle(0)
        hist_SL3_L1[s].SetLineColor(15)
        hist_SL3_L1[s].SetLineWidth(3)
        hist_SL3_L1[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL3_L1[s].GetYaxis().SetTitle("counts")
        hist_SL3_L1[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL3_L1[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL3_L1[s].SetMaximum(yax_SL3*(1.05))
        hist_SL3_L1[s].Draw("HISTO")

        hist_SL3_L2[s].SetMarkerSize(1.)
        hist_SL3_L2[s].SetMarkerStyle(21)
        hist_SL3_L2[s].SetMarkerColor(418)
        hist_SL3_L2[s].SetFillColor(418)
        hist_SL3_L2[s].SetFillStyle(0)
        hist_SL3_L2[s].SetLineColor(418)
        hist_SL3_L2[s].SetLineWidth(3)
        hist_SL3_L2[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL3_L2[s].GetYaxis().SetTitle("counts")
        hist_SL3_L2[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL3_L2[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL3_L2[s].Draw("HISTO,sames")

        hist_SL3_L3[s].SetMarkerSize(1.)
        hist_SL3_L3[s].SetMarkerStyle(21)
        hist_SL3_L3[s].SetMarkerColor(866)
        hist_SL3_L3[s].SetFillColor(866)
        hist_SL3_L3[s].SetFillStyle(0)
        hist_SL3_L3[s].SetLineColor(866)
        hist_SL3_L3[s].SetLineWidth(3)
        hist_SL3_L3[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL3_L3[s].GetYaxis().SetTitle("counts")
        hist_SL3_L3[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL3_L3[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL3_L3[s].Draw("HISTO,sames")

        hist_SL3_L4[s].SetMarkerSize(1.)
        hist_SL3_L4[s].SetMarkerStyle(21)
        hist_SL3_L4[s].SetMarkerColor(801)
        hist_SL3_L4[s].SetFillColor(801)
        hist_SL3_L4[s].SetFillStyle(0)
        hist_SL3_L4[s].SetLineColor(801)
        hist_SL3_L4[s].SetLineWidth(3)
        hist_SL3_L4[s].GetYaxis().SetTitleOffset(1.2)
        hist_SL3_L4[s].GetYaxis().SetTitle("counts")
        hist_SL3_L4[s].GetXaxis().SetTitle(variable[options.variable]['title'])
        hist_SL3_L4[s].GetXaxis().SetRangeUser(variable[options.variable]['min'], variable[options.variable]['max'])
        hist_SL3_L4[s].Draw("HISTO,sames")

        leg_SL3 = TLegend(0.7, 0.7, 0.9, 0.9)
        leg_SL3.SetBorderSize(0)
        leg_SL3.SetFillStyle(0)
        leg_SL3.SetFillColor(0)
        leg_SL3.AddEntry(hist_SL3_L1[s], "SL3_L1", 'L')
        leg_SL3.AddEntry(hist_SL3_L2[s], "SL3_L2", 'L')
        leg_SL3.AddEntry(hist_SL3_L3[s], "SL3_L3", 'L')
        leg_SL3.AddEntry(hist_SL3_L4[s], "SL3_L4", 'L')
        #leg.AddEntry(hist[s], "", 'L')
        leg_SL3.Draw()

        latex = TLatex()
        latex.SetNDC()
        latex.SetTextSize(0.04)
        latex.SetTextColor(1)
        latex.SetTextFont(42)
        latex.SetTextAlign(33)
        latex.DrawLatex(0.9, 0.96, "run n. %.0f (2017)" % (float(ss[14:])))
        latex.SetTextSize(0.04)
        latex.SetTextFont(62)
        latex.DrawLatex(0.30, 0.96, "GIF++")

    	can_SL3[s].Update()
    	can_SL3[s].Print(outpath + "Test_r" + str(sign_sampl[s]['run_number']) + "_" + str(options.variable)  + "_SL3.png")
    	can_SL3[s].Print(outpath + "Test_r" + str(sign_sampl[s]['run_number']) + "_" + str(options.variable)  + "_SL3.pdf")
    	can_SL3[s].Close()

#Plot threshold scan
#SL1_L1
can_scan_SL1_L1 = TCanvas("can_scan_SL1_L1","can_scan_SL1_L1", 1000, 800)
can_scan_SL1_L1.SetGrid()
can_scan_SL1_L1.cd()
graph = TGraphAsymmErrors()
n=0
for a in sorted(scan_SL1_L1):
    #print scan_SL1_L1[a]
    graph.SetPoint(n,a,scan_SL1_L1[a])
    n = n+1
graph.SetMarkerSize(1.)
graph.SetMarkerStyle(21)
graph.SetMarkerColor(862)
graph.SetFillColor(868)
graph.SetFillStyle(3844)
graph.SetLineColor(868)
graph.SetLineWidth(2)
graph.SetLineStyle(2)
graph.GetXaxis().SetTitle("threshold [mV]")
graph.GetYaxis().SetTitleOffset(1.2)
graph.GetYaxis().SetTitle("rate")
graph.Draw("APL")
latex = TLatex()
latex.SetNDC()
latex.SetTextSize(0.04)
latex.SetTextColor(1)
latex.SetTextFont(42)
latex.SetTextAlign(33)
latex.SetTextSize(0.04)
latex.SetTextFont(62)
latex.DrawLatex(0.30, 0.96, "GIF++")
etichetta = TLatex()
etichetta.SetNDC()
etichetta.SetTextSize(0.04)
etichetta.SetTextColor(4)
etichetta.SetTextFont(102)
etichetta.DrawLatex(0.45, 0.8, "#splitline{SL1_L1 threshold scan}{Runs: "+str(run_interval)+"}") 
can_scan_SL1_L1.Update()
can_scan_SL1_L1.Print(outpath + "ThresholdScan_SL1_L1_"+run_interval+".png")
can_scan_SL1_L1.Print(outpath + "ThresholdScan_SL1_L1_"+run_interval+".pdf")
graph.Set(0)

#SL1_L4
can_scan_SL1_L4 = TCanvas("can_scan_SL1_L4","can_scan_SL1_L4", 1000, 800)
can_scan_SL1_L4.SetGrid()
can_scan_SL1_L4.cd()
graph = TGraphAsymmErrors()
n=0
for a in sorted(scan_SL1_L4):
    #print scan_SL1_L4[a]
    graph.SetPoint(n,a,scan_SL1_L4[a])
    n = n+1
graph.SetMarkerSize(1.)
graph.SetMarkerStyle(21)
graph.SetMarkerColor(862)
graph.SetFillColor(868)
graph.SetFillStyle(3844)
graph.SetLineColor(868)
graph.SetLineWidth(2)
graph.SetLineStyle(2)
graph.GetXaxis().SetTitle("threshold [mV]")
graph.GetYaxis().SetTitleOffset(1.2)
graph.GetYaxis().SetTitle("rate")
graph.Draw("APL")
latex = TLatex()
latex.SetNDC()
latex.SetTextSize(0.04)
latex.SetTextColor(1)
latex.SetTextFont(42)
latex.SetTextAlign(33)
latex.SetTextSize(0.04)
latex.SetTextFont(62)
latex.DrawLatex(0.30, 0.96, "GIF++")
etichetta = TLatex()
etichetta.SetNDC()
etichetta.SetTextSize(0.04)
etichetta.SetTextColor(4)
etichetta.SetTextFont(102)
etichetta.DrawLatex(0.45, 0.8, "#splitline{SL1_L4 threshold scan}{Runs: "+str(run_interval)+"}") 
can_scan_SL1_L4.Update()
can_scan_SL1_L4.Print(outpath + "ThresholdScan_SL1_L4_"+run_interval+".png")
can_scan_SL1_L4.Print(outpath + "ThresholdScan_SL1_L4_"+run_interval+".pdf")
graph.Set(0)


if not gROOT.IsBatch(): raw_input("Press Enter to continue...")

