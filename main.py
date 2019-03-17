# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 10:25:35 2019

@authors: Radia, David, Martial, Maxence, Philippe B
"""

import sys

import pandas as pd

import rdmmp.scraping as scraping
import rdmmp.db as db
import rdmmp.cleaning as cleaning
import rdmmp.modeling as modeling
import rdmmp.reporting as reporting
import rdmmp.misc as misc

def test():
    """
    This is an example of Google style.

    Args:
        param1: This is the first param.
        param2: This is a second param.

    Returns:
        This is a description of what is returned.

    Raises:
        KeyError: Raises an exception.
    """

#%% DoScraping
def do_scraping(automatic):
    """ Handle the data scraping on Indeed

        If not in automatic mode ask for user inputs to let them choose to run the automatic scraping
            or to scrap data for the job and location they enter

        In automatic mode, Loop on the jobs and locations and call a scraping function for each tuple

    Args:
        automatic: boolean, ask for user inputs if false then scrap, otherwise scrap predefined lists of jobs and locations
    """

    print("\n****************************************")
    print("*** do_scraping")
    print("****************************************")

    if not automatic:
        # Ask if they want to choose what to scrape
        choose = input("Do you want to choose what to scrape (y/n) ? ")
        if choose in ("y", "Y"):
            # Ask the job and location
            job = input("Please enter the title to scrape data for: \n").lower()

            location = input("Please enter the location to scrape data for: \n").lower()

            # Ask the amount of pages to scrap
            while True:
                num_pages = input("Please enter the number of pages needed (integer only, negative or 0 for all): \n")
                try:
                    num_pages = int(num_pages)
                    break
                except:
                    print("Invalid number of pages! Please try again.")

            # Scrap inputs
            print("\nScraping {} in {}...".format(job, location))
            scraping.get_data(job, num_pages, location)
        else:
            # answer is n or N or something else
            automatic = True

    if automatic:
        # Init job and location lists
        jobs = ["data scientist", "data analyst", "business intelligence", "developpeur"]
        #locations = ["Lyon", "Toulouse", "Nantes", "Bordeaux", "Paris"]
        locations = ["Toulouse", "Nantes", "Bordeaux", "Paris"]

        # Scrap
        for location in locations:
            for job in jobs:
                print("\nScraping {} in {}...\n".format(job, location))
                scraping.get_data(job, -1, location)

#%% GetWorkingData
def get_working_data():
    print("\n****************************************")
    print("*** get_working_data")
    print("****************************************")
    return db.import_data()

#%% Cleaner
def do_cleaning(df):
    print("\n****************************************")
    print("*** do_cleaning")
    print("****************************************")
    cleaning.clean(df)

#%% DoModel
def make_model(df):
    print("\n****************************************")
    print("*** make_model")
    print("****************************************")
    modeling.modelize(df)

#%% UpdateDB
def update_db(df):
    print("\n****************************************")
    print("*** update_db")
    print("****************************************")
    db.update(df)

#%% Report
def make_report(df):
    print("\n****************************************")
    print("*** make_report")
    print("****************************************")
    reporting.report(df)

#%% Code principal
    
def handle_options():
    """
    Define default options for a complete and automatic process
    then check the command line arguments for parts of the process to skip

    Returns:
        auto: whether or not we accept user inputs on job and location
        scrap: whether or not we do the scraping
        working_data: whether or not we get working data from csv and mongoDB
        cleaner: whether or not we do the cleaning of data
        model: whether or not we do the model part
        update: whether or not we update the DB with our findings
        report: whether or not we do the reporting to the CEO
    """

    auto = False
    scrap = True
    working_data = True
    cleaner = True
    model = True
    update = True
    report = True
    
    print(sys.argv)
    if sys.argv:
        # there are command line arguments, we must handle them
        for a in sys.argv:
            if a == '-noScrap':
                scrap = False
            elif a == '-noReport':
                report = False
            
    return auto, scrap, working_data, cleaner, model, update, report
    
    
def main():
    """
    Main function
    """

    print("================================================================================")
    print("Main Start")
    print("================================================================================")

    auto, scrap, working_data, cleaner, model, update, report = handle_options()

    # Check if necessary directories exist
    misc.ensure_dir()

    if scrap:
        # Scrap
        do_scraping(auto)

    if working_data:
        # Get dataframe to work with
        jobs_df = get_working_data()

    if cleaner:
        # Clean
        do_cleaning(jobs_df)

    if model:
        # Modelization
        make_model(jobs_df)

    if update:
        # Update DB with results from models
        update_db(jobs_df)

    if report:
        # Create and send report
        make_report(jobs_df)

    print("\n\n================================================================================")
    print("Main End")
    print("================================================================================")

#%% Point d'entrée unique du script
main()