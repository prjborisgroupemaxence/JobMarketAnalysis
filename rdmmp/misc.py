# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""
Created on Tue Mar 12 12:13:03 2019

Python script file for miscellaneous general functions

@authors: Radia, David, Martial, Maxence, Philippe B
"""

import os
import configparser
from pathlib import Path

# INI filename, sections and values
INI_FILE = 'JobMarketAnalysis.ini'

FOLDERS_SECTION = 'FOLDERS'
SCRAPING_OUTPUT_VALUE = 'Scraping Output'
REPORTING_INPUT_VALUE = 'Reporting Input'
GRAPH_VALUE = 'Graph'

TARGETS_SECTION = 'TARGETS'
JOBS_VALUE = 'Jobs'
LOCATIONS_VALUE = 'Locations'

EMAIL_SECTION = 'EMAIL'
ADDRESS_VALUE = 'Address'
SMTP_USER_VALUE = 'User'
SMTP_PASSWORD_VALUE = 'Password'

# %% Class ConfigValues


class ConfigValues:
    """
    Class publishing various values used in different parts of the scripts
    The values come from a .ini file
    Ideally should be a Singleton
    """
    def __init__(self):
        """
        Init the object
        """
        self.script_dir = Path(__file__).parents[1]
        self.csv_dir = Path()
        self.report_dir = Path()
        self.graph_dir = Path()
        self.targets = []
        self.locations = []
        self.email = ''
        self.smtp_user = ''
        self.smtp_pwd = ''

    def create_default_ini(self):
        """
        Create a default .ini file
        """
        config = configparser.ConfigParser()

        config[FOLDERS_SECTION] = {SCRAPING_OUTPUT_VALUE: 'CSV', REPORTING_INPUT_VALUE: 'Report', GRAPH_VALUE: 'Graph'}

        config[TARGETS_SECTION] = {}
        config[TARGETS_SECTION][JOBS_VALUE] = '\nData Scientist\nData Analyst\nBusiness Intelligence\nDeveloppeur'
        config[TARGETS_SECTION][LOCATIONS_VALUE] = '\nLyon\nToulouse\nNantes\nBordeaux\nParis'

        config[EMAIL_SECTION] = {}
        config[EMAIL_SECTION][ADDRESS_VALUE] = 'groupeMaxence@gmail.com'
        config[EMAIL_SECTION][SMTP_USER_VALUE] = 'groupeMaxence'
        config[EMAIL_SECTION][SMTP_PASSWORD_VALUE] = ''

        with open(self.script_dir.joinpath(INI_FILE), 'w') as configfile:
            config.write(configfile)

    def read_ini(self):
        """
        Read and init the object values from a .ini file
        If the file didn't exist, it's created with default values

        This function should be called before all others
        """
        # check if the ini file exists and create a default one if not
        ini_file = self.script_dir.joinpath(INI_FILE)
        if not ini_file.exists():
            self.create_default_ini()

        # read the ini
        config = configparser.ConfigParser()
        config.read(ini_file)

        # FOLDERS
        dir_name = config[FOLDERS_SECTION][SCRAPING_OUTPUT_VALUE]
        self.csv_dir = Path(self.script_dir.joinpath(dir_name))

        dir_name = config[FOLDERS_SECTION][REPORTING_INPUT_VALUE]
        self.report_dir = Path(self.script_dir.joinpath(dir_name))
        
        dir_name = config[FOLDERS_SECTION][GRAPH_VALUE]
        self.graph_dir = Path(self.script_dir.joinpath(dir_name))

        # TARGETS
        targets = config[TARGETS_SECTION][JOBS_VALUE].splitlines()
        self.targets = [j for j in targets if j]

        locations = config[TARGETS_SECTION][LOCATIONS_VALUE].splitlines()
        self.locations = [l for l in locations if l]

        # EMAIL
        self.email = config[EMAIL_SECTION][ADDRESS_VALUE]
        self.smtp_user = config[EMAIL_SECTION][SMTP_USER_VALUE]
        self.smtp_pwd = config[EMAIL_SECTION][SMTP_PASSWORD_VALUE]

    def ensure_folders_exist(self):
        """
        Checks if the csv_dir and report_dir folders exist and create them if not
        """
        # check if csv_dir exist and create it if not
        if not self.csv_dir.exists():
            os.makedirs(self.csv_dir)

        # check if csv_dir exist and create it if not
        if not self.report_dir.exists():
            os.makedirs(self.report_dir)
        
        # check if graph_dir exist and create it if not
        if not self.graph_dir.exists():
            log.info('Create Graph dir')
            os.makedirs(self.graph_dir)

# %%


CFG = ConfigValues()
