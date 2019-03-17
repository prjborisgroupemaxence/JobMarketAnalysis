# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 12:13:03 2019

Python script file for miscellaneous general functions

@authors: Radia, David, Martial, Maxence, Philippe B
"""

import os

MAIN_DIR = 'D:/Formation/ML/GPRJ1'
CSV_DIR = MAIN_DIR + '/csv'
REPORT_DIR = MAIN_DIR + '/report'

def ensure_dir():
    """
    Checks if the MAIN_DIR, CSV_DIR and REPORT_DIR folders exist and create them if not
    """
    # Check and create
    if not os.path.exists(MAIN_DIR):
        os.makedirs(MAIN_DIR)

    # Vérification et création dossier des CSV
    if not os.path.exists(CSV_DIR):
        os.makedirs(CSV_DIR)

    # Vérification et création dossier des CSV
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
