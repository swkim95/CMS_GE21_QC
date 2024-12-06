# -*- coding: utf-8 -*-
"""
QC2 Report Generator
Automatically generates QC2 reports for all foils in the data directory
"""
import os
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import mplhep as hep
from fpdf import FPDF
from datetime import datetime
from fpdf.enums import XPos, YPos
import argparse
import fnmatch

def find_qc2_files(data_folder, foil_name):
    """
    Find QC2 related files for a given foil name in the specified folder
    
    Args:
        data_folder (str): Path to the data folder
        foil_name (str): Name of the foil
    
    Returns:
        tuple: (part1_file, megger_file, all_channels_file)
    """
    part1_file = ''
    megger_file = ''
    all_channels_file = ''
    
    # List all files in the data folder
    files = os.listdir(data_folder)
    
    # Find part1 file
    for file in files:
        if file.startswith(f'QC2LONG_PART1_{foil_name}_') and file.endswith('.txt'):
            if 'IVplot' not in file:
                part1_file = file[:-4]  # Remove .txt extension
                break
    
    # Find megger file
    for file in files:
        if file.startswith(f'QC2FAST_{foil_name}_') and file.endswith('.txt'):
            megger_file = file[:-4]  # Remove .txt extension
            break
    
    # Find all channels file
    for file in files:
        if file.startswith('QC2_all_channels_monitor_') and file.endswith('.txt'):
            all_channels_file = file[:-4]  # Remove .txt extension
            break
    
    return part1_file, megger_file, all_channels_file

def find_all_foils(data_folder):
    """
    Find all unique foil names in the data folder from QC2LONG_PART1 files
    
    Args:
        data_folder (str): Path to the data folder
    
    Returns:
        list: List of unique foil names
    """
    foil_names = []
    for file in os.listdir(data_folder):
        if file.startswith('QC2LONG_PART1_') and file.endswith('.txt'):
            if 'IVplot' not in file:
                # Extract foil name from filename
                parts = file.split('_')
                foil_name = '_'.join(parts[2:-2])  # Exclude prefix and date/time
                if foil_name not in foil_names:
                    foil_names.append(foil_name)
    return foil_names

def process_foil(data_folder, foil_name):
    """
    Process a single foil and generate its QC2 report
    
    Args:
        data_folder (str): Path to the data folder
        foil_name (str): Name of the foil
    """
    # Find all required files
    part1_file, megger_file, all_channels_file = find_qc2_files(data_folder, foil_name)
    
    if not part1_file or not megger_file or not all_channels_file:
        print(f"Could not find all required files for foil {foil_name}")
        return
    
    print(f"Processing foil {foil_name}...")
    
    # Create folders if they don't exist
    if not os.path.exists(os.path.join(data_folder, 'plots')):
        os.makedirs(os.path.join(data_folder, 'plots'))
    if not os.path.exists(os.path.join(data_folder, 'pdf_reports')):
        os.makedirs(os.path.join(data_folder, 'pdf_reports'))

    # Read megger file
    with open(os.path.join(data_folder, megger_file + '.txt')) as csv_file:
        csv_content = csv.reader(csv_file, delimiter='\t')
        megger_list = list(csv_content)

    # Read part1 file
    with open(os.path.join(data_folder, part1_file + '.txt')) as csv_file:
        csv_content = csv.reader(csv_file, delimiter='\t')
        data_list_part1 = list(csv_content)
    description_list = data_list_part1[0:5]
    CH_number = int(description_list[0][1][2])  # The channel number is only one digit
    del data_list_part1[0:6]  # Delete the headers
    
    # Initialize lists
    voltage_list_part1 = []
    current_list_part1 = []
    time_list_part1 = []

    # Read IV plot data
    with open(os.path.join(data_folder, part1_file + '_IVplot.txt')) as csv_file:
        csv_content = csv.reader(csv_file, delimiter='\t')
        data_list_IV = list(csv_content)
    del data_list_IV[0]
    IV_voltage = []
    IV_current = []
    IV_current_error = []

    # Read all channels file
    with open(os.path.join(data_folder, all_channels_file + '.txt')) as csv_file:
        csv_content = csv.reader(csv_file, delimiter='\t')
        data_list_allCH = list(csv_content)
    del data_list_allCH[0:2]
    voltage_list_part2 = []
    current_list_part2 = []
    time_list_part2 = []

    # Read notes file
    lenpart1 = len(part1_file)
    with open(os.path.join(data_folder, 'QC2NOTES_' + part1_file[14:lenpart1-15] + '.txt')) as csv_file:
        csv_content = csv.reader(csv_file, delimiter='\t')
        notes_list = list(csv_content)
    del notes_list[0]

    # Process data
    for i in range(len(data_list_part1)):
        voltage_list_part1.append(float(data_list_part1[i][0]))
        current_list_part1.append(float(data_list_part1[i][1]))
        time_list_part1.append(float(data_list_part1[i][2]))
    
    for i in range(len(data_list_IV)):
        IV_voltage.append(float(data_list_IV[i][0]))
        IV_current.append(float(data_list_IV[i][1]))
        IV_current_error.append(float(data_list_IV[i][2]))
    
    for i in range(len(data_list_allCH)):
        voltage_list_part2.append(float(data_list_allCH[i][CH_number+1]))
        current_list_part2.append(float(data_list_allCH[i][CH_number+9]))
        time_list_part2.append(float(data_list_allCH[i][0])/3600.0)

    # Generate plots
    fig, axc1 = plt.subplots()
    fig.set_figheight(9)
    fig.set_figwidth(10)
    hep.cms.label(llabel="Preliminary", rlabel="CERN 904 Lab", fontsize=24)
    axc1.set_ylabel('Current [nA]', fontsize=24, color='blue', loc='top')
    axc1.set_xlabel('Time [s]', fontsize=24, loc='right')
    axc1.tick_params(axis="x", direction='in', labelsize=20, length=8)
    axc1.tick_params(axis="y", direction='in', labelsize=20, colors='blue', length=8)
    axc1.plot(time_list_part1,current_list_part1,'s-', color='blue')

    axv1 = axc1.twinx()
    axv1.set_ylabel('Voltage [V]', fontsize=24, color='red', loc='top')
    axv1.tick_params(axis="y", direction='in', labelsize=20, length=8, colors='red')
    axv1.plot(time_list_part1,voltage_list_part1,'s-', color='r')
    plt.savefig(os.path.join(data_folder, 'plots', part1_file + '-VI-t.png'), bbox_inches='tight')
    plt.close()

    fig2, ax = plt.subplots()
    fig2.set_figheight(9)
    fig2.set_figwidth(10)
    hep.cms.label(llabel="Preliminary", rlabel="CERN 904 Lab", fontsize=24)
    ax.errorbar(x=IV_voltage,y=IV_current,yerr=IV_current_error,fmt='s', color='k')
    ax.set_yscale("log")
    ax.set_yticks([1, 7, 10])
    ax.tick_params(axis="x", direction='in', labelsize=20, length=8)
    ax.tick_params(axis="y", direction='in', labelsize=20, length=8)
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel('Voltage [V]', fontsize=24, loc='right')
    ax.set_ylabel('Current [nA]', fontsize=24, loc='top')
    ax.axhline(y=7, color='r', linestyle='-')
    plt.savefig(os.path.join(data_folder, 'plots', part1_file + '-I-V.png'), bbox_inches='tight')
    plt.close()

    fig3, axc2 = plt.subplots()
    fig3.set_figheight(9)
    fig3.set_figwidth(10)
    hep.cms.label(llabel="Preliminary", rlabel="CERN 904 Lab", fontsize=24)
    axc2.set_ylabel('Current [nA]', fontsize=24, color='blue', loc='top')
    axc2.set_xlabel('Time [hr]', fontsize=24, loc='right')
    axc2.tick_params(axis="x", direction='in', labelsize=20, length=8)
    axc2.tick_params(axis="y", direction='in', labelsize=20, colors='blue', length=8)
    axc2.plot(time_list_part2,current_list_part2,'s-', color='blue')

    axv2 = axc2.twinx()
    axv2.set_ylabel('Voltage [V]', fontsize=24, color='r', loc='top')
    axv2.tick_params(axis="y", direction='in', labelsize=20, length=8, colors='red')
    axv2.plot(time_list_part2,voltage_list_part2,'s-', color='r')
    plt.savefig(os.path.join(data_folder, 'plots', part1_file + '-VI-t-long.png'), bbox_inches='tight')
    plt.close()

    # Generate PDF report
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=1.0)
    
    # Generate header
    pdf.set_font('helvetica', 'B', 22)
    pdf.cell(40, 10, 'GE21 QC2 Report', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('helvetica', 'B', 12)
    for k in range(len(description_list)):
        pdf.cell(40, 5, description_list[k][0] + ' ' + description_list[k][1], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(300, 20, 'Acceptance test I (Megger test)')

    # Generate Megger table
    pdf.set_font('helvetica', '', 10)
    pdf.cell(300, 15, '', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    line_height = pdf.font_size * 1.5
    col_width = pdf.epw / 3

    for row in megger_list:
        for entry in row:
            pdf.multi_cell(col_width, line_height, entry, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, max_line_height=pdf.font_size)
        pdf.ln(line_height)

    # Place plots
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(300, 20, 'Acceptance test II -Part 1-')
    pdf.set_font('helvetica', '', 10)
    pdf.cell(300, 15, '', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.image(os.path.join(data_folder, 'plots', part1_file + '-VI-t.png'), pdf.get_x(), pdf.get_y(), pdf.epw*0.4)
    pdf.image(os.path.join(data_folder, 'plots', part1_file + '-I-V.png'), pdf.get_x()+pdf.epw*0.45, pdf.get_y(), pdf.epw*0.365)
    pdf.ln(62)
    
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(300, 20, 'Acceptance test II -Part 2-')
    pdf.set_font('helvetica', '', 10)
    pdf.cell(300, 15, '', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.image(os.path.join(data_folder, 'plots', part1_file + '-VI-t-long.png'), pdf.get_x(), pdf.get_y(), pdf.epw*0.4)
    pdf.ln(62)
    
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(300, 20, 'Notes')
    pdf.set_font('helvetica', '', 10)
    pdf.cell(300, 15, '', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    for row in notes_list:
        pdf.cell(300, pdf.font_size, row[0], new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Save PDF
    pdf_filename = f'QC2REPORT_{part1_file[14:44]}_{datetime.now().strftime("%Y%m%d_%H-%M")}.pdf'
    pdf.output(os.path.join(data_folder, 'pdf_reports', pdf_filename))
    print(f'Created report: {pdf_filename}')

    # Generate individual txt files for QC2 long Part 2
    QC2_part2_list_to_save = []
    for i in range(len(description_list)-1):
        temp_header = []
        temp_header.append(description_list[i][0])
        temp_header.append(description_list[i][1])
        temp_header.append('\t')
        QC2_part2_list_to_save.append(temp_header)
    
    time_stamp_part2 = all_channels_file[25:39]
    QC2_part2_list_to_save.append(['Time_stamp:', time_stamp_part2, '\t'])
    QC2_part2_list_to_save.append(['Voltage (V)', 'Current (uA)', 'Time (s)'])
    
    for i in range(len(data_list_allCH)):
        temp_list = []
        temp_list.append(data_list_allCH[i][CH_number+1])
        temp_list.append(data_list_allCH[i][CH_number+9])
        temp_list.append(data_list_allCH[i][0])
        QC2_part2_list_to_save.append(temp_list)
    
    part2_filename = f'QC2LONG_PART2{part1_file[13:44]}{all_channels_file[24:39]}.txt'
    np.savetxt(os.path.join(data_folder, part2_filename), QC2_part2_list_to_save, delimiter='\t', fmt='%s')

def main():
    parser = argparse.ArgumentParser(description='Generate QC2 reports for all foils in the data folder')
    parser.add_argument('data_folder', help='Path to the data folder')
    
    args = parser.parse_args()
    
    # Find all foils
    foil_names = find_all_foils(args.data_folder)
    
    if not foil_names:
        print(f'No QC2LONG_PART1 files found in {args.data_folder}')
        return
    
    print(f'Found {len(foil_names)} foils to process')
    
    # Process each foil
    for foil_name in foil_names:
        process_foil(args.data_folder, foil_name)

if __name__ == '__main__':
    main()