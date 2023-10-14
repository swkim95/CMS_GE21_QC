import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.font_manager as font_manager
import mplhep as hep
from fpdf import FPDF
import argparse
import os

def func(x, a, b):
    return a*np.exp(b*np.array(x))

def gain(rate, current):
    primary_electron = 346
    e = -1.6e-19
    return current / (primary_electron * e * rate)     

def qc5_eff_rate(mt, mn, d51):
    # Rate
    dr = pd.read_csv('/afs/cern.ch/user/s/seulgi/private/Work/GEM/CMS_GE21_QC/report/data/QC5_GE21-MODULE-{}-{}_{}.txt'.format(mt, mn, d51), sep="\t", skiprows=[1, 2])
    imon = dr.iloc[:, 1].tolist()
    count_off = dr.iloc[:, 5].tolist()
    count_on = dr.iloc[:, 7].tolist()
    rates = []
    for i in range(len(count_on)):
        rate = (count_on[i] - count_off[i]) / 10
        rates.append(rate)
    return imon, rates

def qc5_eff_gain(mt, mn, d51, rate_measurement):
    imon, rates = rate_measurement
    # Current
    dc = pd.read_csv('/afs/cern.ch/user/s/seulgi/private/Work/GEM/CMS_GE21_QC/report/data/QC5_GE21-MODULE-{}-{}_{}_currents_OFF_ON.txt'.format(mt, mn, d51), sep="\t", header=None)
    im = np.where(np.array(imon) == 720)[0][0]
    r = rates[im]
    currents = []
    for im_ in range(len(imon)):
        current = np.mean(np.array(dc.iloc[:, im_])) - np.mean(np.array(dc.iloc[:, im_+len(imon)]))
        currents.append(current) 
    gains = [gain(r, currents[i]) for i in range(len(imon))]
    return gains

def qc5_eff_plot(mt, mn, d51, rate_measurement, gain_measurement):
    fig, ax1 = plt.subplots()
    fig.set_figheight(9)
    fig.set_figwidth(10)
    hep.cms.label(llabel="Preliminary", rlabel="CERN 904 Lab")
   
    imon, rates = rate_measurement
    gains = gain_measurement
    print(imon, gains)
    popt, pcov = curve_fit(func, imon, gains)
    ax1.set_yscale("log")
    ax1.set_xlabel('Imon')
    ax1.set_ylabel('Effective Gain')
    ax1.plot(imon, gains, 'ok', color='red')
    ax1.plot(imon, func(imon, *popt), 'b-', linewidth=1.5, label=r'$P(t) = [p0]e^{-t/\tau}$')
    ax2 = ax1.twinx()
    ax2.set_ylabel('Rate [Hz]')
    ax2.plot(imon, rates, 'ok', color='blue')
    plt.show()
    #voltage = (np.array(dr['Vmon'])).tolist() 

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-mt", "--module_type", dest="module_type", help="module type")
    parser.add_argument("-mn", "--module_number", dest="module_number", help="module number")
    parser.add_argument("-d5", "--qc5_date", dest="qc5_date", help="qc5 test date (YYYYMMDD)")
    args = parser.parse_args()
    a = qc5_eff_rate(args.module_type, args.module_number, args.qc5_date)
    b = qc5_eff_gain(args.module_type, args.module_number, args.qc5_date, a)
    qc5_eff_plot(args.module_type, args.module_number, args.qc5_date, a, b)
