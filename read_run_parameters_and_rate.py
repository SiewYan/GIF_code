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
#parser.add_option("-r1", "--run1", action="store", type="string", dest="run1", default="0")
#parser.add_option("-l2", "--lun2", action="store", type="int", dest="un2", default=0)
parser.add_option("-v", "--variable", action="store", type="string", dest="variable", default="digi_layer")
parser.add_option("-l", "--local", action="store_true", default=False, dest="local")
parser.add_option("-b", "--bash", action="store_true", default=False, dest="bash")
parser.add_option("-F", "--first_run", action="store", type="int", default=0, dest="first_run")
parser.add_option("-L", "--last_run", action="store", type="int", default=0, dest="last_run")
parser.add_option("-e", "--raw_list", action="store", type="string", dest="raw_list", default="")
#parser.add_option("-l", "--last_run", action="store", type="string", default="1", dest="last_run")
(options, args) = parser.parse_args()
if options.bash: gROOT.SetBatch(True)

########## SETTINGS ##########

gStyle.SetOptStat(0)
##For running in local: python read_run_parameters_and_rate.py -l
LOCAL       = options.local
NTUPLEDIR   = "/home/lisa/GIFcode/GIF_code/ntuples_POA/" if LOCAL else "/afs/cern.ch/cms/MUON/dt/sx5/Results/GIF2017/MB2/"
outpath = "/home/lisa/GIFcode/GIF_code/plots/" if LOCAL else "plots/"
########## SAMPLES ##########

##First check if a manual list of runs has been inserted:
run_numbers = []
if options.raw_list!="":
    ordered_list = [str(item) for item in options.raw_list.split(',')]
    print "ordered list: ", ordered_list
    run_min = min(int(item) for item in ordered_list)
    run_max = max(int(item) for item in ordered_list)
    run_interval = "r"+str(run_min)+"-r"+str(run_max)
    for a in sorted(ordered_list):
        print a
	run_numbers.append(int(a))

elif (options.raw_list=="" and (options.first_run and options.last_run) ):
    ##Sort the minimum-maximum range of the considered runs
    run_min = min(options.first_run, options.last_run)
    run_max = max(options.first_run, options.last_run)
    run_interval = "r"+str(run_min)+"-r"+str(run_max)
    ##Create the run list
    for a in range(run_min,run_max+1,1):
        run_numbers.append(a)

else:
    print "Invalid run range!! Aborting..."
    exit()

##Initialize dictionaries
file_name = {}
line = {}
##Usual dictionary of dictionaries definition:
#run_parameters =  { k:{} for k in run_numbers}
##for some reasons, in lxplus the usual definition of a dictionary of dictionaries doesn't work.
##Workaround:
run_parameters = {}
for k in run_numbers:
    run_parameters.update({int(k):{}})

##Loop on considered runs
for a in run_numbers:
    ##Check if EfficiencyNew directory exists. Formats are different in EfficiencyNew wrt Efficiency old.
    if os.path.exists(NTUPLEDIR+"Run"+str(a)+"/EfficiencyNew"):
        print "EfficiencyNew exists!"
    	##Read RunParameters.txt and save the variables in run_parameters dictionary
    	file_name[a]  = open(NTUPLEDIR+"Run"+str(a)+"/EfficiencyNew/RunParameters"+str(a)+".txt",'r')
    	##Read lines
    	for line in file_name[a]:
            ##Split columns (thanks to Sergio)
            columns = line.split(" ")
            ##Save column[0] of RunParameters.txt as the dictionary index, and column[1] as the corresponding value
            run_parameters[a].update({columns[0]:columns[1]})
        ##Search for Occ_NormStat macro: first create the string name
        occ_name = "Occ_NormStat_"+str(a)+"_HV"+str(run_parameters[a]['HV'])+"_vth"+str(run_parameters[a]['VTHR'])+"_SLL"+str(run_parameters[a]['LSTEST']+run_parameters[a]['LAYERHV'])+"_Att"+str(run_parameters[a]['FILTER'])+"_"+str(run_parameters[a]['TRIGGER'])+".C"
        ##Now open the macro
        with open(NTUPLEDIR+"Run"+str(a)+"/EfficiencyNew/"+occ_name) as f:
            ##Loop in the macro lines
            for line in f:
                ##Look for the second bin of statistics histogram
                if "statistics->SetBinContent(2," in line:
                    ##Save normalized occupancy value under the key 'RATE_SL1_L1'
                    run_parameters[a].update({'RATE_SL1_L1' : line[31:39]})

    elif os.path.exists(NTUPLEDIR+"Run"+str(a)+"/Efficiency"):
        print "EfficiencyNew does not exist!"
    	##Read RunParameters.txt and save the variables in run_parameters dictionary
    	file_name[a]  = open(NTUPLEDIR+"Run"+str(a)+"/Efficiency/RunParameters"+str(a)+".txt",'r')
    	##Read lines
    	for line in file_name[a]:
            ##Split columns (thanks to Sergio)
            columns = line.split(" ")
            ##Save column[0] of RunParameters.txt as the dictionary index, and column[1] as the corresponding value
            run_parameters[a].update({columns[0]:columns[1]})
        ##Search for Occ_NormStat macro: first create the string name
        occ_name = "Occ_NormStat_"+str(a)+"_HV"+str(run_parameters[a]['HV'])+"_vth"+str(run_parameters[a]['VTHR'])+"_SLL"+str(run_parameters[a]['LSTEST']+run_parameters[a]['LAYERHV'])+"_Att"+str(run_parameters[a]['FILTER'])+".C"
        ##Now open the macro
        with open(NTUPLEDIR+"Run"+str(a)+"/Efficiency/"+occ_name) as f:
            ##Loop in the macro lines
            for line in f:
                ##Look for the second bin of statistics histogram
                if "statistics27->SetBinContent(2," in line:
                    ##Save normalized occupancy value under the key 'RATE_SL1_L1'
                    print line[33:41]
                    run_parameters[a].update({'RATE_SL1_L1' : line[33:41]})
                elif "statistics43->SetBinContent(2," in line:
                    ##Save normalized occupancy value under the key 'RATE_SL1_L1'
                    run_parameters[a].update({'RATE_SL1_L1' : line[33:41]})
                #elif "statistics" in line:
                #    print line
                #else:
                #    print "Occupancy plot not found!! Aborting..."
                #    exit()
    else:
        print "Cannot read RunParameters.txt!! Aborting..."
        exit()


##Print a summary of the parameters read                
print run_parameters

##Dictionaries are unordered objects; let's create a new dictionary with thresholds
threshold_scan = {}
for a in sorted(run_parameters):
    threshold_scan.update( {int(run_parameters[a]['VTHR']) : run_parameters[a]['RATE_SL1_L1'] } )

print threshold_scan

##Prepare the canvas to plot the scan for SL1_L1
can_scan_SL1_L1 = TCanvas("can_scan_SL1_L1","can_scan_SL1_L1", 1000, 800)
can_scan_SL1_L1.SetGrid()
can_scan_SL1_L1.cd()
##Prepare summary TGraph
graph = TGraphAsymmErrors()
n=0
for a in sorted(threshold_scan):
#for a in sorted(run_parameters):
    print a
    ##Fill the TGraph with threshold (x-axis) and rate (y-axis)
    #######graph.SetPoint(n,int(run_parameters[a]['VTHR']),float(run_parameters[a]['RATE_SL1_L1']))
    graph.SetPoint(n,int(a),float(threshold_scan[a]))
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
graph.GetYaxis().SetTitle("rate [kHz]")
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
can_scan_SL1_L1.Print(outpath + "ThresholdScan_SL1_L1_"+str(run_interval)+".png")
can_scan_SL1_L1.Print(outpath + "ThresholdScan_SL1_L1_"+str(run_interval)+".pdf")

'''
##Prepare the canvas to plot SL1_L4
can_scan_SL1_L4 = TCanvas("can_scan_SL1_L4","can_scan_SL1_L4", 1000, 800)
can_scan_SL1_L4.SetGrid()
can_scan_SL1_L4.cd()
##Prepare summary TGraph
graph = TGraphAsymmErrors()
n=0
for a in sorted(run_parameters):
    print a
    ##Fill the TGraph with threshold (x-axis) and rate (y-axis)
    graph.SetPoint(n,int(run_parameters[a]['VTHR']),float(run_parameters[a]['RATE_SL1_L1']))
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
graph.GetYaxis().SetTitle("rate [Hz]")
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
can_scan_SL1_L4.Print(outpath + "ThresholdScan_SL1_L4_"+str(run_interval)+".png")
can_scan_SL1_L4.Print(outpath + "ThresholdScan_SL1_L4_"+str(run_interval)+".pdf")
'''

if not gROOT.IsBatch(): raw_input("Press Enter to continue...")
