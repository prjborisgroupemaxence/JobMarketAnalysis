# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""
Created on Tue Mar  5 10:25:35 2019

@authors: Radia, David, Martial, Maxence, Philippe B
"""

import sys

import rdmmp.scraping as scraping
import rdmmp.db as db
import rdmmp.cleaning as cleaning
import rdmmp.preprocessing as preprocessing
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

# %% DoScraping


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
                except ValueError:
                    print("Invalid number of pages! Please try again.")

            # Scrap inputs
            print("\nScraping {} in {}...".format(job, location))
            scraping.get_data(job, num_pages, location)
        else:
            # answer is n or N or something else
            automatic = True

    if automatic:
        # Init job and location lists
        jobs = misc.CFG.targets
        locations = misc.CFG.locations

        # Scrap
        for location in locations:
            for job in jobs:
                print("\nScraping {} in {}...\n".format(job, location))
                scraping.get_data(job, -1, location)

# %% GetWorkingData


def get_working_data():
    """
    Combine data from CSV and mongoDB

    Returns:
        A pandas dataframe
    """
    print("\n****************************************")
    print("*** get_working_data")
    print("****************************************")
    return db.import_data()

# %% Cleaner


def do_cleaning(data):
    """
    Clean the data to be used in the model

    Args:
        data: pandas dataframe to clean
    """
    print("\n****************************************")
    print("*** do_cleaning")
    print("****************************************")
    return cleaning.clean(data)

# %% Preprocess


def pre_processing(data):
    """
    Preprocess the data to be used in the model

    Args:
        data: pandas dataframe to preprocessed
    """
    print("\n****************************************")
    print("*** pre_process")
    print("****************************************")
    return preprocessing.prepro(data)

# %% DoModel


def make_model(X_train, X_test, y_train, y_test, dnan):
    """
    Fit the model on the data and predict salary when it's unknown

    Args:
        data: pandas dataframe to train and predict our model on
    """
    print("\n****************************************")
    print("*** make_model")
    print("****************************************")
    return modeling.modelize(X_train, X_test, y_train, y_test, dnan)

# %% UpdateDB


def update_db(data_krbf, data_rf):
    """
    Save the data in the DB

    Args:
        data: pandas dataframe to be saved in mongoDB
    """
    print("\n****************************************")
    print("*** update_db")
    print("****************************************")
    db.update(data_krbf, data_rf)

# %% Report


def make_report(data_krbf, data_rf):
    """
    Create a report and send it by email

    Args:
        data: pandas dataframe, maybe not useful
    """
    print("\n****************************************")
    print("*** make_report")
    print("****************************************")
    reporting.report(data_krbf, data_rf)

# %% Code principal


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
    pre_process = True
    model = True
    update = True
    report = True

    print(sys.argv)
    if sys.argv:
        # there are command line arguments, we must handle them
        for arg in sys.argv:
            if arg == '-auto':
                auto = True
            elif arg == '-noScrap':
                scrap = False
            elif arg == '-noReport':
                report = False

    return auto, scrap, working_data, cleaner, pre_process, model, update, report


def main():
    """
    Main function
    """

    print("================================================================================")
    print("Main Start")
    print("================================================================================")

    auto, scrap, working_data, cleaner, pre_process, model, update, report = handle_options()

    # Read config data and check if needed folders exist
    misc.CFG.read_ini()
    misc.CFG.ensure_folders_exist()

    if scrap:
        # Scrap
        do_scraping(auto)

    if working_data:
        # Get dataframe to work with
        jobs_df = get_working_data()

    if cleaner:
        # Clean
        cleaned_df = do_cleaning(jobs_df)
        
    if pre_process:
        # Preprocessing
        X_train, X_test, y_train, y_test, dnan = pre_processing(cleaned_df)

    if model:
        # Modelization
        predict_krbf, predict_rf = make_model(X_train, X_test, y_train, y_test, dnan)

    if update:
        # Update DB with results from models
        update_db(predict_krbf, predict_rf)

    if report:
        # Create and send report
        make_report(predict_krbf, predict_rf)

    print("\n\n================================================================================")
    print("Main End")
    print("================================================================================")

# %% Point d'entrée unique du script


main()
