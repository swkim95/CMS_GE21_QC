#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QC2 Megger File Generator
Creates megger files for each QC2LONG_PART1 file in the data directory
"""

import os
import csv
import fnmatch
import argparse
from datetime import datetime

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

def extract_foil_name(filename):
    """
    Extract foil name from QC2LONG_PART1 filename
    
    Args:
        filename (str): QC2LONG_PART1 filename
        
    Returns:
        str: Foil name
    """
    # Remove QC2LONG_PART1_ prefix and _date_time.txt suffix
    parts = filename.split('_')
    # Join the parts that make up the foil name (excluding prefix and date/time)
    foil_name = '_'.join(parts[2:-2])
    return foil_name

def get_valid_float_input(prompt):
    """
    Get a valid float input from the user
    
    Args:
        prompt (str): Prompt to show to the user
    
    Returns:
        float: Valid float value
    """
    while True:
        try:
            value = float(input(prompt))
            return value
        except ValueError:
            print("Please enter a valid number")

def collect_megger_data():
    """
    Collect megger data from user input
    
    Returns:
        list: List of [time, impedance, sparks] rows
    """
    times = [0.5, 1, 2, 3, 4, 5]
    data = []
    
    for time in times:
        print(f"\nFor time {time} minutes:")
        impedance = get_valid_float_input(f"Impedance (GOhm) for time {time}: ")
        sparks = get_valid_float_input(f"Sparks for time {time}: ")
        data.append([time, impedance, sparks])
    
    # Show summary and ask for confirmation
    print("\nSummary of entered values:")
    print("Time (minutes)\tImpedance (GOhm)\tSparks")
    for row in data:
        print(f"{row[0]}\t\t{row[1]}\t\t{row[2]}")
    
    while True:
        correction = input("\nDo you need to correct any values? (y/n): ").lower()
        if correction == 'n':
            break
        elif correction == 'y':
            try:
                time_idx = int(input("Enter the index (1-6) of the time point to correct: ")) - 1
                if 0 <= time_idx < len(times):
                    print(f"\nRe-enter values for time {times[time_idx]} minutes:")
                    data[time_idx][1] = get_valid_float_input(f"Impedance (GOhm) for time {times[time_idx]}: ")
                    data[time_idx][2] = get_valid_float_input(f"Sparks for time {times[time_idx]}: ")
                    
                    # Show updated summary
                    print("\nUpdated values:")
                    print("Time (minutes)\tImpedance (GOhm)\tSparks")
                    for row in data:
                        print(f"{row[0]}\t\t{row[1]}\t\t{row[2]}")
                else:
                    print("Invalid index. Please enter a number between 1 and 6.")
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 6.")
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
    
    return data

def create_megger_file(data_folder, foil_name, megger_date, data):
    """
    Create a megger file for a given foil
    
    Args:
        data_folder (str): Path to the data folder
        foil_name (str): Name of the foil
        megger_date (str): Date for the megger file in YYYYMMDD format
        data (list): List of [time, impedance, sparks] rows
    """
    megger_filename = f'QC2FAST_{foil_name}_{megger_date}.txt'
    megger_filepath = os.path.join(data_folder, megger_filename)
    
    # Prepare data rows
    rows = [['Time (minutes)', 'Impedance (GOhm)', 'Sparks']]
    for row in data:
        rows.append([str(row[0]), str(row[1]), str(int(row[2]))])  # Convert sparks to integer
    
    # Write using csv writer to ensure consistent formatting
    with open(megger_filepath, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(rows)
    
    print(f'\nCreated megger file: {megger_filename}')

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate megger files for QC2 testing')
    parser.add_argument('data_folder', help='Path to the data folder')
    parser.add_argument('megger_date', help='Date for megger files (YYYYMMDD format)')
    
    args = parser.parse_args()
    
    # Validate megger date format
    try:
        datetime.strptime(args.megger_date, '%Y%m%d')
    except ValueError:
        print('Error: Megger date must be in YYYYMMDD format')
        return
    
    # Find all part1 files
    part1_files = find_part1_files(args.data_folder)
    
    if not part1_files:
        print(f'No QC2LONG_PART1 files found in {args.data_folder}')
        return
    
    print(f'Found {len(part1_files)} QC2LONG_PART1 files')
    
    # Process each file
    for part1_file in part1_files:
        foil_name = extract_foil_name(part1_file)
        print(f'\nCreating megger file for {foil_name}')
        
        # Collect data from user
        data = collect_megger_data()
        
        # Create the megger file
        create_megger_file(args.data_folder, foil_name, args.megger_date, data)

if __name__ == '__main__':
    main() 