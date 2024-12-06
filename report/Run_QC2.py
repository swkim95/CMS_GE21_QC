#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run_QC2.py
Integrated script to run all QC2 processing steps:
1. Generate megger files (QC2_megger_generator.py)
2. Generate IV plots (QC2_IV-plot-generator.py)
3. Generate QC2 reports (QC2_report.py)
"""

import os
import sys
import subprocess
from datetime import datetime
import readline
import glob

class TabCompleter:
    """
    Tab completion class for directory paths
    """
    def __init__(self):
        self.matches = []
    
    def complete(self, text, state):
        if state == 0:
            # If text is empty, show all files/dirs in current directory
            if not text:
                self.matches = glob.glob('*')
            else:
                # If text ends with path separator, look inside that directory
                dirname = os.path.dirname(text)
                if dirname:
                    dirname = os.path.expanduser(dirname)
                    if not dirname.endswith(os.sep):
                        dirname += os.sep
                else:
                    dirname = ''
                
                # Get the basename (part we're completing)
                basename = os.path.basename(text)
                
                # If text ends with path separator, show everything in that directory
                if text.endswith(os.sep):
                    self.matches = glob.glob(text + '*')
                else:
                    # Otherwise, show matches for current input
                    self.matches = glob.glob(dirname + basename + '*')
                
                # Add trailing slash to directories
                self.matches = [f"{m}{os.sep if os.path.isdir(m) else ''}" for m in self.matches]
        
        # Return the state-th match or None if no more matches
        try:
            return self.matches[state]
        except IndexError:
            return None

def setup_tab_completion():
    """
    Set up tab completion for input
    """
    readline.set_completer(TabCompleter().complete)
    readline.parse_and_bind('tab: complete')
    # Set word delimiters to only include space
    readline.set_completer_delims(' ')

def validate_date(date_str):
    """
    Validate if the input string is a valid date in YYYYMMDD format
    
    Args:
        date_str (str): Date string to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, '%Y%m%d')
        return True
    except ValueError:
        return False

def check_existing_files(path):
    """
    Check for existing QC2 files in the directory
    
    Args:
        path (str): Path to check
    
    Returns:
        tuple: (has_megger, has_iv, has_pdf) indicating presence of existing files
    """
    has_megger = False
    has_iv = False
    has_pdf = False
    
    # Check main directory for megger and IV files
    for file in os.listdir(path):
        if file.startswith('QC2FAST_') and file.endswith('.txt'):
            has_megger = True
        if file.endswith('_IVplot.txt') or file.endswith('_IVplot.png'):
            has_iv = True
    
    # Check pdf_reports directory for PDF files
    pdf_dir = os.path.join(path, 'pdf_reports')
    if os.path.exists(pdf_dir):
        for file in os.listdir(pdf_dir):
            if file.startswith('QC2REPORT_') and file.endswith('.pdf'):
                has_pdf = True
                break
    
    return has_megger, has_iv, has_pdf

def get_user_confirmation(prompt):
    """
    Get yes/no confirmation from user
    
    Args:
        prompt (str): Prompt to show to user
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    while True:
        response = input(prompt).strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")

def validate_path(path):
    """
    Validate if the input path exists and contains required files
    
    Args:
        path (str): Path to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist")
        return False
    
    # Check for QC2LONG_PART1 files
    has_part1_files = False
    for file in os.listdir(path):
        if file.startswith('QC2LONG_PART1_') and file.endswith('.txt'):
            if 'IVplot' not in file:
                has_part1_files = True
                break
    
    if not has_part1_files:
        print(f"Error: No QC2LONG_PART1 files found in '{path}'")
        return False
    
    return True

def run_script(script_name, *args):
    """
    Run a Python script with given arguments
    
    Args:
        script_name (str): Name of the script to run
        *args: Variable number of arguments to pass to the script
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), script_name)] + list(args)
        print(f"\nRunning {script_name}...")
        process = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        return False

def main():
    print("Welcome to QC2 Processing")
    print("------------------------")
    
    # Set up tab completion
    setup_tab_completion()
    
    # Get data path
    while True:
        data_path = input("\nPlease enter the data path: ").strip()
        # Convert relative path to absolute path
        data_path = os.path.abspath(os.path.expanduser(data_path))
        if validate_path(data_path):
            break
        print("Please enter a valid path containing QC2LONG_PART1 files")
    
    # Check existing files
    has_megger, has_iv, has_pdf = check_existing_files(data_path)
    
    # Initialize step flags
    run_step1 = True
    run_step2 = True
    run_step3 = True
    
    # Ask about existing files and step skipping
    if has_megger:
        print("\nFound existing QC2FAST (megger) files in the directory.")
        if get_user_confirmation("Do you want to skip Step 1 (megger file generation)? (y/n): "):
            run_step1 = False
    
    if has_iv and not run_step1:  # Only ask about IV if we're skipping step 1
        print("\nFound existing IV plot files in the directory.")
        if get_user_confirmation("Do you want to skip Step 2 (IV plot generation)? (y/n): "):
            run_step2 = False
    
    if has_pdf and not run_step2:  # Only ask about PDF if we're skipping step 2
        print("\nFound existing PDF reports in the directory.")
        if get_user_confirmation("Do you want to skip Step 3 (PDF report generation)? (y/n): "):
            run_step3 = False
    
    # Get megger date if needed
    megger_date = None
    if run_step1:
        while True:
            megger_date = input("\nPlease enter the date info for QC2FAST (YYYYMMDD): ").strip()
            if validate_date(megger_date):
                break
            print("Please enter a valid date in YYYYMMDD format")
    
    # Run selected steps
    if run_step1:
        print("\nStep 1: Generating megger files")
        print("------------------------------")
        if not run_script('QC2_megger_generator.py', data_path, megger_date):
            print("Error in megger file generation. Stopping process.")
            return
    
    if run_step2:
        print("\nStep 2: Generating IV plots")
        print("-------------------------")
        if not run_script('QC2_IV-plot-generator.py', data_path):
            print("Error in IV plot generation. Stopping process.")
            return
    
    if run_step3:
        print("\nStep 3: Generating QC2 reports")
        print("----------------------------")
        if not run_script('QC2_report.py', data_path):
            print("Error in QC2 report generation. Stopping process.")
            return
    
    if not (run_step1 or run_step2 or run_step3):
        print("\nAll steps skipped. Process complete.")
    else:
        print("\nQC2 processing completed successfully!")
        print("Check the following directories for outputs:")
        if run_step1:
            print(f"- Megger files: {data_path}")
        if run_step2:
            print(f"- IV plots: {os.path.join(data_path, 'plots')}")
        if run_step3:
            print(f"- QC2 reports: {os.path.join(data_path, 'pdf_reports')}")

if __name__ == '__main__':
    main() 