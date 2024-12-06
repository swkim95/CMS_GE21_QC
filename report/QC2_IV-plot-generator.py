#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QC2 IV Plot Generator
Automatically generates IV plots for all QC2LONG_PART1 files in the data directory
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from scipy.optimize import curve_fit
import numpy as np
import csv
import math
import statistics
import os
import fnmatch
import argparse

def find_part1_files(data_folder):
    """
    Find all QC2LONG_PART1 files in the data folder
    
    Args:
        data_folder (str): Path to the data folder
    
    Returns:
        list: List of part1 filenames
    """
    part1_files = []
    for file in os.listdir(data_folder):
        if fnmatch.fnmatch(file, 'QC2LONG_PART1_*.txt'):
            # Exclude IVplot files
            if 'IVplot' not in file:
                part1_files.append(file)
    return part1_files

def process_iv_data(data_folder, part1_file, threshold=7):
    """
    Process IV data for a single part1 file
    
    Args:
        data_folder (str): Path to the data folder
        part1_file (str): Name of the part1 file to process
        threshold (float): Threshold for current values
    """
    print(f'\nProcessing {part1_file}...')
    
    # Read the data file
    with open(os.path.join(data_folder, part1_file)) as csv_file:
        csv_content = csv.reader(csv_file, delimiter='\t')
        data_list = list(csv_content)
    del data_list[0:6]  # Delete the headers

    # Initialize lists
    voltage_list = []
    current_list = []
    time_list = []
    voltage_list_to_plot = []
    current_list_to_plot = []
    err_current_list_to_plot = []
    
    # Parse data
    for row in data_list:
        voltage_list.append(float(row[0]))
        current_list.append(float(row[1]))
        time_list.append(float(row[2]))

    # Process data for I-V plot
    start = False
    ramp_up = False
    store = False
    update_list = False
    voltage_list_to_average = []
    current_list_to_average = []

    for j in range(800):
        if(voltage_list[j+2]-voltage_list[j]>2):
            ramp_up = True
            start = False
            store = False
        else:
            ramp_up = False
            
        if(start==False and ramp_up==False and current_list[j]==0 and voltage_list[j]!=0):
            start = True
            voltage_list_to_average = []
            current_list_to_average = []
        elif(start==True and current_list[j]!=0):
            store = True
            voltage_list_to_average.append(voltage_list[j])
            current_list_to_average.append(current_list[j]*1000.0)  # Convert to nA
            update_list = True
        elif(start==True and store==True and current_list[j]==0):
            if(len(voltage_list_to_average)>0 and update_list==True):
                update_list = False
                try:
                    if(statistics.mean(current_list_to_average)<threshold):
                        voltage_list_to_plot.append(statistics.mean(voltage_list_to_average))
                        current_list_to_plot.append(statistics.mean(current_list_to_average))
                        err_current_list_to_plot.append(statistics.stdev(current_list_to_average)/math.sqrt(len(current_list_to_average)))
                except ValueError:
                    if voltage_list_to_plot:  # Only pop if list is not empty
                        voltage_list_to_plot.pop(-1)
                        current_list_to_plot.pop(-1)
                else:
                    print(f'Imon= {statistics.mean(current_list_to_average):.2f} nA. Current higher than threshold, point not added.')
                voltage_list_to_average = []
                current_list_to_average = []

    # Remove points with close voltage values
    list_idx = []
    for i in range(0, len(voltage_list_to_plot)-1):
        if abs(voltage_list_to_plot[i] - voltage_list_to_plot[i+1]) < 5:
            list_idx.append(i+1)

    for idx in sorted(list_idx, reverse=True):
        del voltage_list_to_plot[idx]
        del current_list_to_plot[idx]
        del err_current_list_to_plot[idx]

    # Create plots - exactly as in original script
    plt.plot(time_list, voltage_list, '*')
    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (uA)')
    plt.close()
    
    plt.plot(time_list, current_list, '*')
    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (uA)')
    plt.close()
    
    plt.errorbar(x=voltage_list_to_plot, y=current_list_to_plot, yerr=err_current_list_to_plot, fmt='*')
    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (nA)')
    plt.savefig(os.path.join(data_folder, part1_file.replace('.txt', '_IVplot.png')))
    plt.close()

    # Save data to file
    list_to_save = [['Voltage (V)', 'Current (nA)', 'Error_current (nA)']]
    for v, c, e in zip(voltage_list_to_plot, current_list_to_plot, err_current_list_to_plot):
        list_to_save.append([str(v), str(c), str(e)])
    
    if not voltage_list_to_plot:  # If no data points
        list_to_save = [['Voltage (V)', 'Current (nA)', 'Error_current (nA)']]
    
    data_filename = part1_file.replace('.txt', '_IVplot.txt')
    np.savetxt(os.path.join(data_folder, data_filename), list_to_save, delimiter='\t', fmt='%s')
    print(f'Created {data_filename}')

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate IV plots for QC2 testing')
    parser.add_argument('data_folder', help='Path to the data folder')
    parser.add_argument('--threshold', type=float, default=7,
                      help='Threshold (nA) for current values (default: 7)')
    
    args = parser.parse_args()
    
    # Find all part1 files
    part1_files = find_part1_files(args.data_folder)
    
    if not part1_files:
        print(f'No QC2LONG_PART1 files found in {args.data_folder}')
        return
    
    print(f'Found {len(part1_files)} QC2LONG_PART1 files')
    
    # Process each file
    for part1_file in part1_files:
        process_iv_data(args.data_folder, part1_file, args.threshold)

if __name__ == '__main__':
    main()


