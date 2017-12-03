#! /usr/bin/env python

import os, multiprocessing
import copy
import math
import numpy as np
from array import array
from ROOT import ROOT, gROOT, gStyle, gRandom, TSystemDirectory
from ROOT import TFile, TChain, TTree, TCut, TH1, TH1F, TH2F, THStack, TGraph, TGraphAsymmErrors, TF1, TMath
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
##For running outside lxplus: python read_run_parameters_and_rate.py -l
LOCAL       = options.local
TXTDIR   = "/home/lisa/GIFcode/GIF_code/summaryGif/" if LOCAL else "/afs/cern.ch/user/m/meneguz/public/summaryGif/"
##Modify your local outpath!
if not os.path.exists("plots_from_txt"):
    os.system("mkdir plots_from_txt")
outpath = "plots_from_txt/"
################ LIST OF SCANS TO BE COMPARED ############
#HV_scan_29_nov_L4 = {"29_nov" : "5907,5908,5909,5910,5911,5912,5913,5914"}
#HV_scan_29_nov_L1 = {"29_nov" : "5915,5916,5917,5918,5919,5920,5921"}
#HV_scan_22_nov_L1 = {"22_nov" : "5873,5878,5879,5880,5881,5882,5883,5884"}
#HV_scan_22_nov_L4 = {"22_nov" : "5885,5886,5887,5888,5889,5890,5891"}

##execut the macro to obtain graphs
#os.system("python plot_from_txt.py -b -e "+HV_scan_29_nov_L4["29_nov"]+ " -o " + "_29_nov")
#os.system("python plot_from_txt.py -b -e "+HV_scan_29_nov_L1["29_nov"]+ " -o " + "_29_nov")
#os.system("python plot_from_txt.py -b -e "+HV_scan_22_nov_L4["22_nov"]+ " -o " + "_22_nov")
#os.system("python plot_from_txt.py -b -e "+HV_scan_22_nov_L1["22_nov"]+ " -o " + "_22_nov")

HV_scans = {"29_nov_L4" : "5907,5908,5909,5910,5911,5912,5913,5914", "29_nov_L1" : "5915,5916,5917,5918,5919,5920,5921", "22_nov_L1" : "5873,5878,5879,5880,5881,5882,5883,5884", "22_nov_L4" : "5885,5886,5887,5888,5889,5890,5891", "15_nov_L4" : "5825,5826,5827,5828,5829", "15_nov_L1" : "5815,5816,5817,5818,5819,5820,5821,5822,5824", "1_nov_L4" : "5750,5751,5752,5753,5754,5755,5763", "1_nov_L1" : "5756,5757,5758,5759,5760,5761,5762"}
#all missing: "8_nov_L4" : "5782,5786,5794,5795,5706,5797,5798,5799", "8_nov_L1" : "5782,5783,5784,5785,5789,5792,5793",
colors = [634, 4, 856, 410, 2, 1, 881, 798, 602, 921]

files_L1 = {}
graphs_L1 = {}
files_L4 = {}
graphs_L4 = {}

files_rate_L1 = {}
graphs_rate_L1 = {}
files_rate_L4 = {}
graphs_rate_L4 = {}
#for k in sorted(HV_scans):
#    files.update({k:{}})
#    graphs.update({k:{}})

for a in sorted(HV_scans):
    if options.local:
        os.system("python plot_from_txt.py -l -b -e "+HV_scans[a]+ " -o " + "_" + a)
    else:
        os.system("python plot_from_txt.py -b -e "+HV_scans[a]+ " -o " + "_" + a)        
    run_interval = "r"+ HV_scans[a][:4] + "-r" + HV_scans[a][-4:]
    files_L1[a] = TFile(outpath+"Graph_HV_scan_SL1_L1_"+run_interval+"_"+a+".root", 'READ')
    graphs_L1[a] = TGraphAsymmErrors(files_L1[a].Get("HV_scan_SL1_L1_"+run_interval))
    files_L4[a] = TFile(outpath+"Graph_HV_scan_SL1_L4_"+run_interval+"_"+a+".root", 'READ')
    graphs_L4[a] = TGraphAsymmErrors(files_L4[a].Get("HV_scan_SL1_L4_"+run_interval))

    files_rate_L1[a] = TFile(outpath+"Graph_HV_scan_rate_SL1_L1_"+run_interval+"_"+a+".root", 'READ')
    graphs_rate_L1[a] = TGraphAsymmErrors(files_rate_L1[a].Get("HV_scan_rate_SL1_L1_"+run_interval))
    files_rate_L4[a] = TFile(outpath+"Graph_HV_scan_rate_SL1_L4_"+run_interval+"_"+a+".root", 'READ')
    graphs_rate_L4[a] = TGraphAsymmErrors(files_rate_L4[a].Get("HV_scan_rate_SL1_L4_"+run_interval))


##Efficiency SL1_L1    
can_HV_scan_SL1_L1 = TCanvas("can_compare_HV_scan_SL1_L1","can_compare_HV_scan_SL1_L1", 1000, 800)
can_HV_scan_SL1_L1.SetGrid()
can_HV_scan_SL1_L1.cd()

leg_L1 = TLegend(0.2, 0.7, 0.4, 0.9)
leg_L1.SetBorderSize(0)
leg_L1.SetFillStyle(0)
leg_L1.SetFillColor(0)
x_min = 3190
x_max = 3610
imin = 100
for i, j in enumerate(graphs_L1):
    if "L1" in j:
        imin = min(imin,i)
        graphs_L1[j].SetMarkerSize(1.)
        graphs_L1[j].SetMarkerStyle(21)
        graphs_L1[j].SetMarkerColor(colors[i])
        graphs_L1[j].SetFillColor(colors[i])
        graphs_L1[j].SetLineColor(colors[i])
        graphs_L1[j].SetLineWidth(3)
        leg_L1.AddEntry(graphs_L1[j],j,'PL')
        graphs_L1[j].GetXaxis().SetLimits(x_min,x_max)
        graphs_L1[j].GetXaxis().SetTitle("HV [V]")
        graphs_L1[j].GetYaxis().SetTitleOffset(1.2)
        graphs_L1[j].GetYaxis().SetTitle("efficiency")
        graphs_L1[j].GetYaxis().SetLimits(0,1.01)
        graphs_L1[j].SetLineStyle(2)
        if i==imin:
            graphs_L1[j].Draw("APL")
        else:
            graphs_L1[j].Draw("PL")

leg_L1.Draw()
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
etichetta.DrawLatex(0.45, 0.93, "SL1_L1 HV scan")
#etichetta.DrawLatex(0.45, 0.8, "#splitline{SL1_L1 threshold scan}{Runs: "+str(run_interval)+"}")
can_HV_scan_SL1_L1.Update()
can_HV_scan_SL1_L1.Print(outpath + "Compare_HV_scan_SL1_L1.png")
can_HV_scan_SL1_L1.Print(outpath + "Compare_HV_scan_SL1_L1.pdf")

##Efficiency SL1_L4    
can_HV_scan_SL1_L4 = TCanvas("can_compare_HV_scan_SL1_L4","can_compare_HV_scan_SL1_L4", 1000, 800)
can_HV_scan_SL1_L4.SetGrid()
can_HV_scan_SL1_L4.cd()

leg_L4 = TLegend(0.2, 0.7, 0.4, 0.9)
leg_L4.SetBorderSize(0)
leg_L4.SetFillStyle(0)
leg_L4.SetFillColor(0)
x_min = 3190
x_max = 3610
imin = 100
for i, j in enumerate(graphs_L4):
    if "L4" in j:
        imin = min(imin,i)
        graphs_L4[j].SetMarkerSize(1.)
        graphs_L4[j].SetMarkerStyle(21)
        graphs_L4[j].SetMarkerColor(colors[i])
        graphs_L4[j].SetFillColor(colors[i])
        graphs_L4[j].SetLineColor(colors[i])
        graphs_L4[j].SetLineWidth(3)
        leg_L4.AddEntry(graphs_L4[j],j,'PL')
        graphs_L4[j].GetXaxis().SetLimits(x_min,x_max)
        graphs_L4[j].GetXaxis().SetTitle("HV [V]")
        graphs_L4[j].GetYaxis().SetTitleOffset(1.2)
        graphs_L4[j].GetYaxis().SetTitle("efficiency")
        graphs_L4[j].GetYaxis().SetLimits(0,1.01)
        graphs_L4[j].SetMaximum(1.01)
        graphs_L4[j].SetLineStyle(2)
        if i==imin:
            graphs_L4[j].Draw("APL")
        else:
            graphs_L4[j].Draw("PL")

leg_L4.Draw()
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
etichetta.DrawLatex(0.45, 0.93, "SL1_L4 HV scan")
#etichetta.DrawLatex(0.45, 0.8, "#splitline{SL1_L4 threshold scan}{Runs: "+str(run_interval)+"}")
can_HV_scan_SL1_L4.Update()
can_HV_scan_SL1_L4.Print(outpath + "Compare_HV_scan_SL1_L4.png")
can_HV_scan_SL1_L4.Print(outpath + "Compare_HV_scan_SL1_L4.pdf")


##Rate SL1_L1    
can_HV_scan_rate_SL1_L1 = TCanvas("can_compare_HV_scan_rate_SL1_L1","can_compare_HV_scan_rate_SL1_L1", 1000, 800)
can_HV_scan_rate_SL1_L1.SetGrid()
can_HV_scan_rate_SL1_L1.cd()

leg_L1 = TLegend(0.2, 0.7, 0.4, 0.9)
leg_L1.SetBorderSize(0)
leg_L1.SetFillStyle(0)
leg_L1.SetFillColor(0)
x_min = 3190
x_max = 3610
y_max = 0
imin = 100
for i, j in enumerate(graphs_rate_L1):
    if "L1" in j:
        imin = min(imin,i)
        graphs_rate_L1[j].SetMarkerSize(1.)
        graphs_rate_L1[j].SetMarkerStyle(21)
        graphs_rate_L1[j].SetMarkerColor(colors[i])
        graphs_rate_L1[j].SetFillColor(colors[i])
        graphs_rate_L1[j].SetLineColor(colors[i])
        graphs_rate_L1[j].SetLineWidth(3)
        leg_L1.AddEntry(graphs_rate_L1[j],j,'PL')
        graphs_rate_L1[j].GetXaxis().SetLimits(x_min,x_max)
        graphs_rate_L1[j].GetXaxis().SetTitle("HV [V]")
        graphs_rate_L1[j].GetYaxis().SetTitleOffset(1.2)
        graphs_rate_L1[j].GetYaxis().SetTitle("rate [kHz]")
        y_max = max(y_max, graphs_rate_L1[j].GetHistogram().GetMaximum())
        graphs_rate_L1[j].SetMaximum(y_max*(1.01))
        graphs_rate_L1[j].SetLineStyle(2)
        if i==imin:
            graphs_rate_L1[j].Draw("APL")
        else:
            graphs_rate_L1[j].Draw("PL")

leg_L1.Draw()
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
etichetta.DrawLatex(0.45, 0.93, "SL1_L1 HV scan rate")
#etichetta.DrawLatex(0.45, 0.8, "#splitline{SL1_L1 threshold scan_rate}{Runs: "+str(run_interval)+"}")
can_HV_scan_rate_SL1_L1.Update()
can_HV_scan_rate_SL1_L1.Print(outpath + "Compare_HV_scan_rate_SL1_L1.png")
can_HV_scan_rate_SL1_L1.Print(outpath + "Compare_HV_scan_rate_SL1_L1.pdf")

##Rate SL1_L4    
can_HV_scan_rate_SL1_L4 = TCanvas("can_compare_HV_scan_rate_SL1_L4","can_compare_HV_scan_rate_SL1_L4", 1000, 800)
can_HV_scan_rate_SL1_L4.SetGrid()
can_HV_scan_rate_SL1_L4.cd()

leg_L4 = TLegend(0.2, 0.7, 0.4, 0.9)
leg_L4.SetBorderSize(0)
leg_L4.SetFillStyle(0)
leg_L4.SetFillColor(0)
x_min = 3190
x_max = 3610
imin = 100
y_max_L4 = 8
for i, j in enumerate(graphs_rate_L4):
    if "L4" in j:
        imin = min(imin,i)
        graphs_rate_L4[j].SetMarkerSize(1.)
        graphs_rate_L4[j].SetMarkerStyle(21)
        graphs_rate_L4[j].SetMarkerColor(colors[i])
        graphs_rate_L4[j].SetFillColor(colors[i])
        graphs_rate_L4[j].SetLineColor(colors[i])
        graphs_rate_L4[j].SetLineWidth(3)
        leg_L4.AddEntry(graphs_rate_L4[j],j,'PL')
        graphs_rate_L4[j].GetXaxis().SetLimits(x_min,x_max)
        graphs_rate_L4[j].GetXaxis().SetTitle("HV [V]")
        graphs_rate_L4[j].GetYaxis().SetTitleOffset(1.2)
        graphs_rate_L4[j].GetYaxis().SetTitle("rate [kHz]")
        graphs_rate_L4[j].SetLineStyle(2)
        y_max_L4 = max(y_max_L4, graphs_rate_L4[j].GetHistogram().GetMaximum())
        print y_max_L4
        graphs_rate_L4[j].GetYaxis().SetLimits(0,y_max_L4)
        #y_max_L4 += 5
        #graphs_rate_L4[j].SetMaximum(10)
        if i==imin:
            graphs_rate_L4[j].SetMaximum(max(y_max_L4, graphs_rate_L4[j].GetHistogram().GetMaximum())*(1.01))
            graphs_rate_L4[j].Draw("APL")
            graphs_rate_L4[j].SetMaximum(max(y_max_L4, graphs_rate_L4[j].GetHistogram().GetMaximum())*(1.01))
            graphs_rate_L4[j].GetYaxis().SetLimits(0,y_max_L4)
        else:
            graphs_rate_L4[j].SetMaximum(max(y_max_L4, graphs_rate_L4[j].GetHistogram().GetMaximum())*(1.01))
            graphs_rate_L4[j].Draw("PL")
            graphs_rate_L4[j].SetMaximum(max(y_max_L4, graphs_rate_L4[j].GetHistogram().GetMaximum())*(1.01))
            graphs_rate_L4[j].GetYaxis().SetLimits(0,y_max_L4)

leg_L4.Draw()
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
etichetta.DrawLatex(0.45, 0.93, "SL1_L4 HV scan rate")
#etichetta.DrawLatex(0.45, 0.8, "#splitline{SL1_L4 threshold scan_rate}{Runs: "+str(run_interval)+"}")
can_HV_scan_rate_SL1_L4.Update()
can_HV_scan_rate_SL1_L4.Print(outpath + "Compare_HV_scan_rate_SL1_L4.png")
can_HV_scan_rate_SL1_L4.Print(outpath + "Compare_HV_scan_rate_SL1_L4.pdf")

if not gROOT.IsBatch(): raw_input("Press Enter to continue...")
exit()
