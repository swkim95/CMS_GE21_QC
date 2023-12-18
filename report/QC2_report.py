# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 17:21:24 2021

@author: luife
"""
import os
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from fpdf.enums import XPos, YPos

"Edit this part of the acode according to the location of your QC2 files"
"---------------------------------------------------------------------------"
data_folder='QC2_results/data_GE21_foils_20231001'
subfolder='/'
part1_file='QC2LONG_PART1_GE21-FOIL-M8-G3-CERN-B10-0013_20231001_11-30'
megger_file='QC2FAST_GE21-FOIL-M8-G3-CERN-B10-0013_20231001'
all_channels_file='QC2_all_channels_monitor_20231002_06-29'
include_IV_plot=True   #Set to False if you do not want to include the I-V plot in the pdf report and the /plots folder.
"----------------------------------------------------------------------------"


#Create folder for plots and pdf reports if it doesn't exit:
if not os.path.exists(data_folder+'/plots'):
    os.makedirs(data_folder+'/plots')
#Create folder for reports if it doesn't exit
if not os.path.exists(data_folder+'/pdf_reports'):
    os.makedirs(data_folder+'/pdf_reports')

############################Open all the associated files
with open(data_folder+'/megger'+'/'+megger_file+'.txt') as csv_file:
    csv_content = csv.reader(csv_file, delimiter='\t')
    megger_list = list(csv_content)


with open(data_folder+subfolder+part1_file+'.txt') as csv_file:
    csv_content = csv.reader(csv_file, delimiter='\t')
    data_list_part1 = list(csv_content)
description_list=data_list_part1[0:5]
CH_number=int(description_list[0][1][2]) #The channel number is only one digit in position [0][1] after the substring "CH"
del data_list_part1[0:6] #Delete the headers
voltage_list_part1=[]
current_list_part1=[]
time_list_part1=[]

with open(data_folder+subfolder+part1_file+'_IVplot.txt') as csv_file:
    csv_content = csv.reader(csv_file, delimiter='\t')
    data_list_IV = list(csv_content)
del data_list_IV[0]
IV_voltage=[]
IV_current=[]
IV_current_error=[]

with open(data_folder+subfolder+all_channels_file+'.txt') as csv_file:
    csv_content = csv.reader(csv_file, delimiter='\t')
    data_list_allCH = list(csv_content)
del data_list_allCH[0:2]
voltage_list_part2=[]
current_list_part2=[]
time_list_part2=[]

lenpart1=len(part1_file)
with open(data_folder+subfolder+'QC2NOTES_'+part1_file[14:lenpart1-15]+'.txt') as csv_file:
    csv_content = csv.reader(csv_file, delimiter='\t')
    notes_list = list(csv_content)
del notes_list[0]

###################################Generate the plots
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

plt.plot(time_list_part1,voltage_list_part1,'*')
plt.xlabel('Time (s)', fontsize=18)
plt.ylabel('Voltage (V)', fontsize=18)
plt.xticks(fontsize=16); plt.yticks(fontsize=16);
plt.savefig(data_folder+'/plots/'+part1_file+'-V-t.png',bbox_inches='tight')
plt.close()
plt.plot(time_list_part1,current_list_part1,'*')
plt.xlabel('Time (s)', fontsize=18)
plt.ylabel('Current (uA)', fontsize=18)
plt.xticks(fontsize=16); plt.yticks(fontsize=16);
plt.savefig(data_folder+'/plots/'+part1_file+'-I-t.png',bbox_inches='tight')
plt.close()
plt.errorbar(x=IV_voltage,y=IV_current,yerr=IV_current_error,fmt='*')
plt.xlabel('Voltage (V)', fontsize=18)
plt.ylabel('Current (nA)', fontsize=18)
plt.xticks(fontsize=16); plt.yticks(fontsize=16);
if(include_IV_plot):plt.savefig(data_folder+'/plots/'+part1_file+'-I-V.png',bbox_inches='tight')
plt.close()
plt.plot(time_list_part2,voltage_list_part2,'*')
plt.xlabel('Time (hour)', fontsize=18)
plt.ylabel('Voltage (V)', fontsize=18)
plt.xticks(fontsize=16); plt.yticks(fontsize=16);
plt.savefig(data_folder+'/plots/'+part1_file+'-V-t-long.png',bbox_inches='tight')
plt.close()
plt.plot(time_list_part2,current_list_part2,'*')
plt.xlabel('Time (hour)', fontsize=18)
plt.ylabel('Current (uA)', fontsize=18)
plt.xticks(fontsize=16); plt.yticks(fontsize=16);
plt.savefig(data_folder+'/plots/'+part1_file+'-I-t-long.png',bbox_inches='tight')

###################################Generate PDF report
pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(True, margin = 1.0)
#### Generate header
pdf.set_font('helvetica', 'B', 22)
pdf.cell(40, 10, 'GE21 QC2 Report',new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font('helvetica', 'B', 12)
for k in range (len(description_list)):
    pdf.cell(40,5, description_list[k][0]+' '+description_list[k][1],new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font('helvetica', 'B', 16)
pdf.cell(300, 20, 'Acceptance test I (Megger test)')

#### Generate Megger table
pdf.set_font('helvetica', '', 10)
pdf.cell(300, 15, '',new_x=XPos.LMARGIN, new_y=YPos.NEXT)
line_height = pdf.font_size * 1.5
col_width = pdf.epw / 3  # distribute content evenly

for row in megger_list:
    for entry in row:
        pdf.multi_cell(col_width, line_height, entry, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, max_line_height=pdf.font_size)
    pdf.ln(line_height)
    
#### Place V-time, I-time and I-V plots of first part
pdf.set_font('helvetica', 'B', 16)
pdf.cell(300, 20, 'Acceptance test II -Part 1-')
pdf.set_font('helvetica', '', 10)
pdf.cell(300, 15, '',new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.image(data_folder+'/plots/'+part1_file+'-V-t.png',pdf.get_x(),pdf.get_y(),pdf.epw/3)
pdf.image(data_folder+'/plots/'+part1_file+'-I-t.png',pdf.get_x()+pdf.epw/3,pdf.get_y(),pdf.epw/3)
plt.xticks(fontsize=16); plt.yticks(fontsize=16);
if(include_IV_plot):pdf.image(data_folder+'/plots/'+part1_file+'-I-V.png',pdf.get_x()+2*pdf.epw/3,pdf.get_y(),pdf.epw/3)
pdf.set_font('helvetica', 'B', 16)
pdf.cell(300, 100, 'Acceptance test II -Part 2-')
pdf.set_font('helvetica', '', 10)
pdf.cell(300, 55, '', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.image(data_folder+'/plots/'+part1_file+'-V-t-long.png',pdf.get_x(),pdf.get_y(),pdf.epw/3)
pdf.image(data_folder+'/plots/'+part1_file+'-I-t-long.png',pdf.get_x()+pdf.epw/3,pdf.get_y(),pdf.epw/3)
pdf.set_font('helvetica', 'B', 16)
pdf.cell(300, 100, 'Notes')
pdf.set_font('helvetica', '', 10)
pdf.cell(300, 55, '', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
for row in notes_list:
     pdf.cell(300,pdf.font_size,row[0],new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.output(data_folder+'/pdf_reports/'+'QC2REPORT_'+part1_file[14:44]+'_'+datetime.now().strftime("%Y%m%d_%H-%M")+'.pdf')

################################### Generate individual .txt files for the QC2 long Part 2
QC2_part2_list_to_save=[]
for i in range (len(description_list)-1):
    temp_header=[]
    temp_header.append(description_list[i][0])
    temp_header.append(description_list[i][1])
    temp_header.append('\t')
    QC2_part2_list_to_save.append(temp_header)
time_stamp_part2=all_channels_file[25:39]
QC2_part2_list_to_save.append(['Time_stamp:',time_stamp_part2,'\t'])
QC2_part2_list_to_save.append(['Voltage (V)','Current (uA)','Time (s)'])
for i in range(len(data_list_allCH)):
    temp_list=[]
    temp_list.append(data_list_allCH[i][CH_number+1])
    temp_list.append(data_list_allCH[i][CH_number+9])
    temp_list.append(data_list_allCH[i][0])
    QC2_part2_list_to_save.append(temp_list)
np.savetxt(data_folder+'/QC2LONG_PART2'+part1_file[13:44]+all_channels_file[24:39]+'.txt',QC2_part2_list_to_save, delimiter='\t', fmt='%s')
