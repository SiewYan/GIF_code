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
parser.add_option("-o", "--optionalstring", action="store", type="string", dest="optionalstring", default="")
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
##For running outside lxplus: python read_run_parameters_and_rate.py -l
LOCAL       = options.local
TXTDIR   = "/home/lisa/GIFcode/GIF_code/summaryGif/" if LOCAL else "/afs/cern.ch/user/m/meneguz/public/summaryGif/"
##Modify your local outpath!
if not os.path.exists("plots_from_txt"):
    os.system("mkdir plots_from_txt")
outpath = "plots_from_txt/"
########## SAMPLES ##########

##First check if a manual list of runs has been inserted:
run_numbers = []
if options.raw_list!="":
    if "," in options.raw_list:
        ordered_list = [str(item) for item in options.raw_list.split(',')]
        run_min = min(int(item) for item in ordered_list)
        run_max = max(int(item) for item in ordered_list)
        run_interval = "r"+str(run_min)+"-r"+str(run_max)
        for a in sorted(ordered_list):
            run_numbers.append(int(a))
    elif "-" in options.raw_list:
        ordered_list = [str(item) for item in options.raw_list.split('-')]
        #print ordered_list
        run_min = min(int(item) for item in ordered_list)
        run_max = max(int(item) for item in ordered_list)
        run_interval = "r"+str(run_min)+"-r"+str(run_max)
        for a in range(run_min,run_max+1,1):
            run_numbers.append(a)
    else:
        print "Not a valid run interval!! Aborting.."
        exit()

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
    if os.path.exists(TXTDIR+"RunParametersOut"+str(a)+".txt"):
        #print "EfficiencyNew exists!"
    	##Read RunParameters.txt and save the variables in run_parameters dictionary
    	file_name[a]  = open(TXTDIR+"RunParametersOut"+str(a)+".txt",'r')
    	##Read lines
    	for line in file_name[a]:
            #print "printing line: "
            #print line
            ##Split columns (thanks to Sergio)
            columns = line.split(" ")
            ##Clean columns from empty spaces, it happens for Eff outputs
            for it in columns:
                if it=="":
                    columns.remove(it)
            #print "splitted line: "
            #print columns
            ##Save column[0] of RunParameters.txt as the dictionary index, and column[1] as the corresponding value
            if columns[0] != "Eff" and columns[0] != "statlayer" and columns[0] != "BKglayer":
                run_parameters[a].update({columns[0]:columns[1]})
            ##Save Eff properly
            if columns[0] == "Eff":
                eff_string = columns[0] + columns[1]
                run_parameters[a].update({eff_string : columns[3]})##efficiency is included in column 3 now
            elif columns[0] == "statlayer":
                for p in range(0,12):
                    run_parameters[a].update({"RATE_SL1_L"+str(p+1) : columns[2+p]})
                #eff_string = columns[0] + columns[1]
                #run_parameters[a].update({eff_string : columns[3]})##efficiency is included in column 3 now
    else:
        print "Cannot read RunParametersOut.txt because it doesn't exist!! Aborting..."
        exit()


##Print a summary of the parameters read                
#print run_parameters
#exit()

##Dictionaries are unordered objects; let's create a new dictionary with HV
#!!! add here a switch to L1 or L4 scans
HV_scan_L1 = {}
HV_scan_L4 = {}
for a in sorted(run_parameters):
    HV_scan_L1.update( {int(run_parameters[a]['HV']) : run_parameters[a]['Eff1'] } )
    HV_scan_L4.update( {int(run_parameters[a]['HV']) : run_parameters[a]['Eff4'] } )    

#for a in sorted(HV_scan_L1):#in this way we should plot
#    print a    

##Prepare the canvas to plot the HV scan for SL1_L1
can_HV_scan_SL1_L1 = TCanvas("can_HV_scan_SL1_L1","can_HV_scan_SL1_L1", 1000, 800)
can_HV_scan_SL1_L1.SetGrid()
can_HV_scan_SL1_L1.cd()
##Prepare summary TGraph
graph_HV_L1 = TGraphAsymmErrors()
n=0
for a in sorted(HV_scan_L1):
#for a in sorted(run_parameters):
    ##Fill the TGraph with threshold (x-axis) and rate (y-axis)
    #######graph.SetPoint(n,int(run_parameters[a]['VTHR']),float(run_parameters[a]['RATE_SL1_L1']))
    graph_HV_L1.SetPoint(n,int(a),float(HV_scan_L1[a]))
    n = n+1
graph_HV_L1.SetMarkerSize(1.)
graph_HV_L1.SetMarkerStyle(21)
graph_HV_L1.SetMarkerColor(418)
graph_HV_L1.SetFillColor(868)
graph_HV_L1.SetFillStyle(3844)
graph_HV_L1.SetLineColor(418-1)
graph_HV_L1.SetLineWidth(2)
graph_HV_L1.SetLineStyle(2)
graph_HV_L1.GetXaxis().SetTitle("HV [V]")
graph_HV_L1.GetYaxis().SetTitleOffset(1.2)
graph_HV_L1.GetYaxis().SetTitle("efficiency")
graph_HV_L1.GetYaxis().SetRangeUser(0,1.01)
graph_HV_L1.Draw("APL")
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
etichetta.SetTextColor(418)
etichetta.SetTextFont(102)
etichetta.DrawLatex(0.2, 0.8, "#splitline{SL1_L1 HV scan}{Runs: "+str(run_interval)+"}")
can_HV_scan_SL1_L1.Update()
can_HV_scan_SL1_L1.Print(outpath + "HVScan_SL1_L1_"+str(run_interval)+options.optionalstring+".png")
can_HV_scan_SL1_L1.Print(outpath + "HVScan_SL1_L1_"+str(run_interval)+options.optionalstring+".pdf")
graph_HV_L1.SetName("HV_scan_SL1_L1_"+run_interval)
new_file_HV_scan_SL1_L1 = TFile(outpath + "Graph_HV_scan_SL1_L1_"+run_interval+ options.optionalstring+".root",'RECREATE')
graph_HV_L1.Write()
graph_HV_L1.Set(0)
print "Graph_HV_scan_SL1_L1_"+run_interval+ options.optionalstring+".root written in "+outpath

##Prepare the canvas to plot the HV scan for SL1_L4
can_HV_scan_SL1_L4 = TCanvas("can_HV_scan_SL1_L4","can_HV_scan_SL1_L4", 1000, 800)
can_HV_scan_SL1_L4.SetGrid()
can_HV_scan_SL1_L4.cd()
##Prepare summary TGraph
graph_HV_L4 = TGraphAsymmErrors()
n=0
for a in sorted(HV_scan_L4):
#for a in sorted(run_parameters):
    ##Fill the TGraph with threshold (x-axis) and rate (y-axis)
    #######graph.SetPoint(n,int(run_parameters[a]['VTHR']),float(run_parameters[a]['RATE_SL4_L4']))
    graph_HV_L4.SetPoint(n,int(a),float(HV_scan_L4[a]))
    n = n+1
graph_HV_L4.SetMarkerSize(1.)
graph_HV_L4.SetMarkerStyle(21)
graph_HV_L4.SetMarkerColor(801)
graph_HV_L4.SetFillColor(868)
graph_HV_L4.SetFillStyle(3844)
graph_HV_L4.SetLineColor(801-1)
graph_HV_L4.SetLineWidth(2)
graph_HV_L4.SetLineStyle(2)
graph_HV_L4.GetXaxis().SetTitle("HV [V]")
graph_HV_L4.GetYaxis().SetTitleOffset(1.2)
graph_HV_L4.GetYaxis().SetTitle("efficiency")
graph_HV_L4.GetYaxis().SetRangeUser(0,1.01)
graph_HV_L4.Draw("APL")
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
etichetta.SetTextColor(801)
etichetta.SetTextFont(102)
etichetta.DrawLatex(0.2, 0.8, "#splitline{SL1_L4 HV scan}{Runs: "+str(run_interval)+"}")
can_HV_scan_SL1_L4.Update()
can_HV_scan_SL1_L4.Print(outpath + "HVScan_SL1_L4_"+str(run_interval)+options.optionalstring+".png")
can_HV_scan_SL1_L4.Print(outpath + "HVScan_SL1_L4_"+str(run_interval)+options.optionalstring+".pdf")
graph_HV_L4.SetName("HV_scan_SL1_L4_"+run_interval)
new_file_HV_scan_SL1_L4 = TFile(outpath + "Graph_HV_scan_SL1_L4_"+run_interval+ options.optionalstring+".root",'RECREATE')
graph_HV_L4.Write()
graph_HV_L4.Set(0)
print "Graph_HV_scan_SL1_L4_"+run_interval+ options.optionalstring+".root written in "+outpath



##Dictionaries are unordered objects; let's create a new dictionary with thresholds
rate_HV_scan_L1 = {}
rate_HV_scan_L2 = {}
rate_HV_scan_L3 = {}
rate_HV_scan_L4 = {}
rate_HV_scan_L5 = {}
rate_HV_scan_L6 = {}
rate_HV_scan_L7 = {}
rate_HV_scan_L8 = {}
rate_HV_scan_L9 = {}
rate_HV_scan_L10 = {}
rate_HV_scan_L11 = {}
rate_HV_scan_L12 = {}
for a in sorted(run_parameters):
    rate_HV_scan_L1.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L1'] } )
    rate_HV_scan_L2.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L2'] } )
    rate_HV_scan_L3.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L3'] } )
    rate_HV_scan_L4.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L4'] } )
    rate_HV_scan_L5.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L5'] } )
    rate_HV_scan_L6.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L6'] } )
    rate_HV_scan_L7.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L7'] } )
    rate_HV_scan_L8.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L8'] } )
    rate_HV_scan_L9.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L9'] } )
    rate_HV_scan_L10.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L10'] } )
    rate_HV_scan_L11.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L11'] } )
    rate_HV_scan_L12.update( {int(run_parameters[a]['HV']) : run_parameters[a]['RATE_SL1_L12'] } )


##Prepare the canvas to plot the scan for SL1_L1
can_scan_SL1_L1 = TCanvas("can_scan_SL1_L1","can_scan_SL1_L1", 1000, 800)
can_scan_SL1_L1.SetGrid()
can_scan_SL1_L1.cd()
##Prepare summary TGraph
graph = TGraphAsymmErrors()
n=0
for a in sorted(rate_HV_scan_L1):
#for a in sorted(run_parameters):
    ##Fill the TGraph with threshold (x-axis) and rate (y-axis)
    #######graph.SetPoint(n,int(run_parameters[a]['VTHR']),float(run_parameters[a]['RATE_SL1_L1']))
    graph.SetPoint(n,int(a),float(rate_HV_scan_L1[a]))
    n = n+1
graph.SetMarkerSize(1.)
graph.SetMarkerStyle(21)
graph.SetMarkerColor(862)
graph.SetFillColor(868)
graph.SetFillStyle(3844)
graph.SetLineColor(868)
graph.SetLineWidth(2)
graph.SetLineStyle(2)
graph.GetXaxis().SetTitle("HV [V]")
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
etichetta.DrawLatex(0.2, 0.8, "#splitline{SL1_L1 HV scan rate}{Runs: "+str(run_interval)+"}")
can_scan_SL1_L1.Update()
can_scan_SL1_L1.Print(outpath + "HV_scan_rate_SL1_L1_"+str(run_interval)+options.optionalstring+".png")
can_scan_SL1_L1.Print(outpath + "HV_scan_rate_SL1_L1_"+str(run_interval)+options.optionalstring+".pdf")
graph.SetName("HV_scan_rate_SL1_L1_"+run_interval)
new_file_HV_scan_rate_SL1_L1 = TFile(outpath + "Graph_HV_scan_rate_SL1_L1_"+run_interval+ options.optionalstring+".root",'RECREATE')
graph.Write()
graph.Set(0)
print "Graph_HV_scan_rate_SL1_L1_"+run_interval+ options.optionalstring+".root written in "+outpath

'''#L2
##Prepare the canvas to plot the scan for SL1_L2
can_scan_SL1_L2 = TCanvas("can_scan_SL1_L2","can_scan_SL1_L2", 1000, 800)
can_scan_SL1_L2.SetGrid()
can_scan_SL1_L2.cd()
##Prepare summary TGraph
graph = TGraphAsymmErrors()
n=0
for a in sorted(rate_HV_scan_L2):
#for a in sorted(run_parameters):
    ##Fill the TGraph with threshold (x-axis) and rate (y-axis)
    #######graph.SetPoint(n,int(run_parameters[a]['VTHR']),float(run_parameters[a]['RATE_SL1_L2']))
    graph.SetPoint(n,int(a),float(rate_HV_scan_L2[a]))
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
etichetta.DrawLatex(0.2, 0.8, "#splitline{SL1_L2 HV scan rate}{Runs: "+str(run_interval)+"}")
can_scan_SL1_L2.Update()
can_scan_SL1_L2.Print(outpath + "HV_scan_rate_SL1_L2_"+str(run_interval)+options.optionalstring+".png")
can_scan_SL1_L2.Print(outpath + "HV_scan_rate_SL1_L2_"+str(run_interval)+options.optionalstring+".pdf")
graph.SetName("HV_scan_rate_SL1_L2_"+run_interval)
new_file_HV_scan_rate_SL1_L2 = TFile(outpath + "Graph_HV_scan_rate_SL1_L2_"+run_interval+ options.optionalstring+".root",'RECREATE')
graph.Write()
graph.Set(0)
print "Graph_HV_scan_rate_SL1_L2_"+run_interval+ options.optionalstring+".root written in "+outpath

#L3
##Prepare the canvas to plot the scan for SL1_L3
can_scan_SL1_L3 = TCanvas("can_scan_SL1_L3","can_scan_SL1_L3", 1000, 800)
can_scan_SL1_L3.SetGrid()
can_scan_SL1_L3.cd()
##Prepare summary TGraph
graph = TGraphAsymmErrors()
n=0
for a in sorted(rate_HV_scan_L3):
#for a in sorted(run_parameters):
    ##Fill the TGraph with threshold (x-axis) and rate (y-axis)
    #######graph.SetPoint(n,int(run_parameters[a]['VTHR']),float(run_parameters[a]['RATE_SL1_L3']))
    graph.SetPoint(n,int(a),float(rate_HV_scan_L3[a]))
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
etichetta.DrawLatex(0.2, 0.8, "#splitline{SL1_L3 HV scan rate}{Runs: "+str(run_interval)+"}")
can_scan_SL1_L3.Update()
can_scan_SL1_L3.Print(outpath + "HV_scan_rate_SL1_L3_"+str(run_interval)+options.optionalstring+".png")
can_scan_SL1_L3.Print(outpath + "HV_scan_rate_SL1_L3_"+str(run_interval)+options.optionalstring+".pdf")
graph.SetName("HV_scan_rate_SL1_L3_"+run_interval)
new_file_HV_scan_rate_SL1_L3 = TFile(outpath + "Graph_HV_scan_rate_SL1_L3_"+run_interval+ options.optionalstring+".root",'RECREATE')
graph.Write()
graph.Set(0)
print "Graph_HV_scan_rate_SL1_L3_"+run_interval+ options.optionalstring+".root written in "+outpath
'''

#L4
##Prepare the canvas to plot the scan for SL1_L4
can_scan_SL1_L4 = TCanvas("can_scan_SL1_L4","can_scan_SL1_L4", 1000, 800)
can_scan_SL1_L4.SetGrid()
can_scan_SL1_L4.cd()
##Prepare summary TGraph
graph = TGraphAsymmErrors()
n=0
for a in sorted(rate_HV_scan_L4):
#for a in sorted(run_parameters):
    ##Fill the TGraph with threshold (x-axis) and rate (y-axis)
    #######graph.SetPoint(n,int(run_parameters[a]['VTHR']),float(run_parameters[a]['RATE_SL1_L4']))
    graph.SetPoint(n,int(a),float(rate_HV_scan_L4[a]))
    n = n+1
graph.SetMarkerSize(1.)
graph.SetMarkerStyle(21)
graph.SetMarkerColor(881)
graph.SetFillColor(868)
graph.SetFillStyle(3844)
graph.SetLineColor(880)
graph.SetLineWidth(2)
graph.SetLineStyle(2)
graph.GetXaxis().SetTitle("HV [V]")
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
etichetta.SetTextColor(881)
etichetta.SetTextFont(102)
etichetta.DrawLatex(0.2, 0.8, "#splitline{SL1_L4 HV scan rate}{Runs: "+str(run_interval)+"}")
can_scan_SL1_L4.Update()
can_scan_SL1_L4.Print(outpath + "HV_scan_rate_SL1_L4_"+str(run_interval)+options.optionalstring+".png")
can_scan_SL1_L4.Print(outpath + "HV_scan_rate_SL1_L4_"+str(run_interval)+options.optionalstring+".pdf")
graph.SetName("HV_scan_rate_SL1_L4_"+run_interval)
new_file_HV_scan_rate_SL1_L4 = TFile(outpath + "Graph_HV_scan_rate_SL1_L4_"+run_interval+ options.optionalstring+".root",'RECREATE')
graph.Write()
graph.Set(0)
print "Graph_HV_scan_rate_SL1_L4_"+run_interval+ options.optionalstring+".root written in "+outpath


if not gROOT.IsBatch(): raw_input("Press Enter to continue...")
exit()
