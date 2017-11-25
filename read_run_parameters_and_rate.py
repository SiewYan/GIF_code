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
parser.add_option("-F", "--first_run", action="store", type="int", default=5890, dest="first_run")
parser.add_option("-L", "--last_run", action="store", type="int", default=5891, dest="last_run")
#parser.add_option("-l", "--last_run", action="store", type="string", default="1", dest="last_run")
(options, args) = parser.parse_args()
if options.bash: gROOT.SetBatch(True)

########## SETTINGS ##########

gStyle.SetOptStat(0)

LOCAL       = options.local
NTUPLEDIR   = "/home/lisa/GIFcode/GIF_code/ntuples_POA/" if LOCAL else "/afs/cern.ch/cms/MUON/dt/sx5/Results/GIF2017/MB2/"
#DATE        = '31_oct'#'17_nov'
outpath = "/home/lisa/GIFcode/GIF_code/plots/" if LOCAL else "plots/"
########## SAMPLES ##########

#print options.first_run

#run_min = 5891#options.run1#5891
#run_max = 5891#options.run2#5891

run_min = min(options.first_run, options.last_run)
run_max = max(options.first_run, options.last_run)
run_interval = "r"+str(run_min)+"-r"+str(run_max)
run_numbers = []

for a in range(run_min,run_max+1,1):
    run_numbers.append(a)

file_name = {} #dictionary, one file per run
line = {} #dictionary
##Usual dictionary of dictionaries definition:
#run_parameters =  { k:{} for k in run_numbers}
##for some reasons, in lxplus the usual definition of a dictionary of dictionaries doesn't work.
##Workaround:
run_parameters = {}
for k in run_numbers:
    run_parameters.update({int(k):{}})
print run_parameters

for a in run_numbers:
    #read run parameters and save them in the parameters dictionary
    file_name[a]  = open(NTUPLEDIR+"Run"+str(a)+"/EfficiencyNew/RunParameters"+str(a)+".txt",'r')
    for line in file_name[a]:
        columns = line.split(" ")
        run_parameters[a].update({columns[0]:columns[1]})
    #grep from occupancy
    #os.system("ls "+ NTUPLEDIR+"Run"+str(a)+"/EfficiencyNew/Occ_NormStat*.C")
    occ_name = "Occ_NormStat_"+str(a)+"_HV"+str(run_parameters[a]['HV'])+"_vth"+str(run_parameters[a]['VTHR'])+"_SLL"+str(run_parameters[a]['LSTEST']+run_parameters[a]['LAYERHV'])+"_Att"+str(run_parameters[a]['FILTER'])+"_"+str(run_parameters[a]['TRIGGER'])+".C"
    print occ_name
    with open(NTUPLEDIR+"Run"+str(a)+"/EfficiencyNew/"+occ_name) as f:
        for line in f:
            if "statistics->SetBinContent(2," in line:
                run_parameters[a].update({'RATE' : line[31:39]})
                
print run_parameters

can_scan_SL1_L1 = TCanvas("can_scan_SL1_L1","can_scan_SL1_L1", 1000, 800)
can_scan_SL1_L1.SetGrid()
can_scan_SL1_L1.cd()
graph = TGraphAsymmErrors()
n=0
for a in sorted(run_parameters):
    print a
    #graph = TGraphAsymmErrors()
    graph.SetPoint(n,int(run_parameters[a]['VTHR']),float(run_parameters[a]['RATE']))
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
etichetta.DrawLatex(0.45, 0.8, "#splitline{SL1_L1 threshold scan}{Runs: "+str(run_interval)+"}")
can_scan_SL1_L1.Update()
can_scan_SL1_L1.Print(outpath + "ThresholdScan_SL1_L1_prova.png")
can_scan_SL1_L1.Print(outpath + "ThresholdScan_SL1_L1_prova.pdf")


if not gROOT.IsBatch(): raw_input("Press Enter to continue...")


exit()

can_scan_SL1_L1 = TCanvas("can_compare_scan_SL1_L1","can_compare_scan_SL1_L1", 1000, 800)
can_scan_SL1_L1.SetGrid()
can_scan_SL1_L1.cd()

g_L1_17_nov.SetMarkerSize(1.)
g_L1_17_nov.SetMarkerStyle(21)
g_L1_17_nov.SetMarkerColor(2)
g_L1_17_nov.SetFillColor(2)
g_L1_17_nov.SetLineColor(2)
g_L1_17_nov.SetLineWidth(3)
g_L1_17_nov.SetLineStyle(1)
g_L1_17_nov.GetXaxis().SetTitle("threshold [mV]")
g_L1_17_nov.GetYaxis().SetTitleOffset(1.2)
g_L1_17_nov.GetYaxis().SetTitle("rate [kHz]")
g_L1_17_nov.Draw("AL")

g_L1_9_nov.SetMarkerSize(1.)
g_L1_9_nov.SetMarkerStyle(21)
g_L1_9_nov.SetMarkerColor(921)
g_L1_9_nov.SetFillColor(921)
g_L1_9_nov.SetFillStyle(921)
g_L1_9_nov.SetLineColor(921)
g_L1_9_nov.SetLineWidth(3)
g_L1_9_nov.SetLineStyle(1)
g_L1_9_nov.GetXaxis().SetTitle("threshold [mV]")
g_L1_9_nov.GetYaxis().SetTitleOffset(1.2)
g_L1_9_nov.GetYaxis().SetTitle("rate [kHz]")
g_L1_9_nov.Draw("L")

g_L1_3_nov.SetMarkerSize(1.)
g_L1_3_nov.SetMarkerStyle(21)
g_L1_3_nov.SetMarkerColor(8)
g_L1_3_nov.SetFillColor(8)
g_L1_3_nov.SetFillStyle(8)
g_L1_3_nov.SetLineColor(8)
g_L1_3_nov.SetLineWidth(3)
g_L1_3_nov.SetLineStyle(1)
g_L1_3_nov.GetXaxis().SetTitle("threshold [mV]")
g_L1_3_nov.GetYaxis().SetTitleOffset(1.2)
g_L1_3_nov.GetYaxis().SetTitle("rate [kHz]")
g_L1_3_nov.Draw("L")

g_L1_31_oct.SetMarkerSize(1.)
g_L1_31_oct.SetMarkerStyle(21)
g_L1_31_oct.SetMarkerColor(862)
g_L1_31_oct.SetFillColor(868)
g_L1_31_oct.SetFillStyle(3844)
g_L1_31_oct.SetLineColor(868)
g_L1_31_oct.SetLineWidth(3)
g_L1_31_oct.SetLineStyle(1)
g_L1_31_oct.GetXaxis().SetTitle("threshold [mV]")
g_L1_31_oct.GetYaxis().SetTitleOffset(1.2)
g_L1_31_oct.GetYaxis().SetTitle("rate [kHz]")
g_L1_31_oct.Draw("L")


leg_L1 = TLegend(0.7, 0.7, 0.9, 0.9)
leg_L1.SetBorderSize(0)
leg_L1.SetFillStyle(0)
leg_L1.SetFillColor(0)
leg_L1.AddEntry(g_L1_31_oct, "31 oct", 'L')
leg_L1.AddEntry(g_L1_3_nov, "3 nov", 'L')
leg_L1.AddEntry(g_L1_9_nov, "9 nov", 'L')
leg_L1.AddEntry(g_L1_17_nov, "17 nov", 'L')
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
etichetta.DrawLatex(0.45, 0.93, "SL1_L1 threshold scan") 
#etichetta.DrawLatex(0.45, 0.8, "#splitline{SL1_L1 threshold scan}{Runs: "+str(run_interval)+"}") 
can_scan_SL1_L1.Update()
can_scan_SL1_L1.Print(outpath + "Compare_thresholdScan_SL1_L1.png")
can_scan_SL1_L1.Print(outpath + "Compare_thresholdScan_SL1_L1.pdf")

#L4 comparison
file_L4_31_oct = TFile(outpath+"Graph_thresholdScan_SL1_L4_r5742-r5746.root", 'READ')
g_L4_31_oct = TGraphAsymmErrors(file_L4_31_oct.Get("ThresholdScan_SL1_L4_r5742-r5746"))

file_L4_3_nov = TFile(outpath+"Graph_thresholdScan_SL1_L4_r5773-r5777.root", 'READ')
g_L4_3_nov = TGraphAsymmErrors(file_L4_3_nov.Get("ThresholdScan_SL1_L4_r5773-r5777"))

file_L4_9_nov = TFile(outpath+"Graph_thresholdScan_SL1_L4_r5804-r5812.root", 'READ')
g_L4_9_nov = TGraphAsymmErrors(file_L4_9_nov.Get("ThresholdScan_SL1_L4_r5804-r5812"))

file_L4_17_nov = TFile(outpath+"Graph_thresholdScan_SL1_L4_r5862-r5868.root", 'READ')
g_L4_17_nov = TGraphAsymmErrors(file_L4_17_nov.Get("ThresholdScan_SL1_L4_r5862-r5868"))

can_scan_SL1_L4 = TCanvas("can_compare_scan_SL1_L4","can_compare_scan_SL1_L4", 1000, 800)
can_scan_SL1_L4.SetGrid()
can_scan_SL1_L4.cd()

g_L4_17_nov.SetMarkerSize(1.)
g_L4_17_nov.SetMarkerStyle(21)
g_L4_17_nov.SetMarkerColor(2)
g_L4_17_nov.SetFillColor(2)
g_L4_17_nov.SetLineColor(2)
g_L4_17_nov.SetLineWidth(3)
g_L4_17_nov.SetLineStyle(1)
g_L4_17_nov.GetXaxis().SetTitle("threshold [mV]")
g_L4_17_nov.GetYaxis().SetTitleOffset(1.2)
g_L4_17_nov.GetYaxis().SetTitle("rate [kHz]")
g_L4_17_nov.Draw("AL")

g_L4_9_nov.SetMarkerSize(1.)
g_L4_9_nov.SetMarkerStyle(21)
g_L4_9_nov.SetMarkerColor(921)
g_L4_9_nov.SetFillColor(921)
g_L4_9_nov.SetFillStyle(921)
g_L4_9_nov.SetLineColor(921)
g_L4_9_nov.SetLineWidth(3)
g_L4_9_nov.SetLineStyle(1)
g_L4_9_nov.GetXaxis().SetTitle("threshold [mV]")
g_L4_9_nov.GetYaxis().SetTitleOffset(1.2)
g_L4_9_nov.GetYaxis().SetTitle("rate [kHz]")
g_L4_9_nov.Draw("L")

g_L4_3_nov.SetMarkerSize(1.)
g_L4_3_nov.SetMarkerStyle(21)
g_L4_3_nov.SetMarkerColor(8)
g_L4_3_nov.SetFillColor(8)
g_L4_3_nov.SetFillStyle(8)
g_L4_3_nov.SetLineColor(8)
g_L4_3_nov.SetLineWidth(3)
g_L4_3_nov.SetLineStyle(1)
g_L4_3_nov.GetXaxis().SetTitle("threshold [mV]")
g_L4_3_nov.GetYaxis().SetTitleOffset(1.2)
g_L4_3_nov.GetYaxis().SetTitle("rate [kHz]")
g_L4_3_nov.Draw("L")

g_L4_31_oct.SetMarkerSize(1.)
g_L4_31_oct.SetMarkerStyle(21)
g_L4_31_oct.SetMarkerColor(862)
g_L4_31_oct.SetFillColor(868)
g_L4_31_oct.SetFillStyle(3844)
g_L4_31_oct.SetLineColor(868)
g_L4_31_oct.SetLineWidth(3)
g_L4_31_oct.SetLineStyle(1)
g_L4_31_oct.GetXaxis().SetTitle("threshold [mV]")
g_L4_31_oct.GetYaxis().SetTitleOffset(1.2)
g_L4_31_oct.GetYaxis().SetTitle("rate [kHz]")
g_L4_31_oct.Draw("L")


leg_L4 = TLegend(0.7, 0.7, 0.9, 0.9)
leg_L4.SetBorderSize(0)
leg_L4.SetFillStyle(0)
leg_L4.SetFillColor(0)
leg_L4.AddEntry(g_L4_31_oct, "31 oct", 'L')
leg_L4.AddEntry(g_L4_3_nov, "3 nov", 'L')
leg_L4.AddEntry(g_L4_9_nov, "9 nov", 'L')
leg_L4.AddEntry(g_L4_17_nov, "17 nov", 'L')
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
etichetta.DrawLatex(0.45, 0.93, "SL1_L4 threshold scan") 
#etichetta.DrawLatex(0.45, 0.8, "#splitline{SL1_L4 threshold scan}{Runs: "+str(run_interval)+"}") 
can_scan_SL1_L4.Update()
can_scan_SL1_L4.Print(outpath + "Compare_thresholdScan_SL1_L4.png")
can_scan_SL1_L4.Print(outpath + "Compare_thresholdScan_SL1_L4.pdf")

if not gROOT.IsBatch(): raw_input("Press Enter to continue...")
