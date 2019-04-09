# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""
Created on Tue Mar  5 10:25:35 2019

@authors: Radia, David, Martial, Maxence, Philippe B
"""

import sys
import logging
import time

import pandas as pd
import numpy as np

import rdmmp.scraping as scraping
import rdmmp.db as db
import rdmmp.cleaning as cleaning
import rdmmp.preprocessing as preprocessing
import rdmmp.modeling as modeling
import rdmmp.reporting as reporting
import rdmmp.configvalues as cv


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


def do_scraping(automatic, db_data):
    """ Handle the data scraping on Indeed

        If not in automatic mode ask for user inputs to let them choose to run the automatic scraping
            or to scrap data for the job and location they enter

        In automatic mode, Loop on the jobs and locations and call a scraping function for each tuple

    Args:
        automatic: boolean, ask for user inputs if false then scrap, otherwise scrap predefined lists of jobs and locations
        db_data: dataframe from database
    """
    log = logging.getLogger('main')

    log.info("")
    log.info("****************************************")
    log.info("*** do_scraping")
    log.info("****************************************")

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
                    log.error("Invalid number of pages! Please try again.")

            # Scrap inputs
            log.info("Scraping %s in %s...", job, location)
            scraping.get_data(job, num_pages, location, db_data)
        else:
            # answer is n or N or something else
            automatic = True

    if automatic:
        # Init job and location lists
        jobs = cv.CFG.targets
        locations = cv.CFG.locations

        # Scrap
        thread_list = []
        for location in locations:
            for job in jobs:
                log.info("Scraping %s in %s...", job, location)

                thread = scraping.ScrapingThread(job, -1, location, db_data)
                thread_list.append(thread)
                thread.start()
                time.sleep(3)

        for thread in thread_list:
            thread.join()


# %% GetWorkingData


def get_working_data(database_data):
    """
    Combine data from CSV and mongoDB

    Returns:
        A pandas dataframe
    """
    log = logging.getLogger('main')

    log.info("")
    log.info("****************************************")
    log.info("*** get_working_data")
    log.info("****************************************")

    # Get a dataframe from csv files created by the scraping
    csv_data = scraping.import_data_from_csv(cv.CFG.csv_dir, cv.CFG.targets, cv.CFG.locations)

    log.info('%d rows from database', database_data.shape[0])
    log.info('%d rows from csv files', csv_data.shape[0])

    # Concat the 2 dataframes
    dataframe = pd.concat([database_data, csv_data], join='inner')

    # drop duplicates except the first(database)
    dataframe.drop_duplicates(['Title', 'Company', 'Salary', 'City', 'Posting'], inplace=True)

    # reset index
    dataframe.reset_index(drop=True, inplace=True)

    log.info('%d rows in the merge', dataframe.shape[0])

    return dataframe

# %% Cleaner


def do_cleaning(data):
    """
    Clean the data to be used in the model

    Args:
        data: pandas dataframe to clean
    """
    log = logging.getLogger('main')

    log.info("")
    log.info("****************************************")
    log.info("*** do_cleaning")
    log.info("****************************************")
    return cleaning.clean(data)

# %% Preprocess


def pre_processing(data):
    """
    Preprocess the data to be used in the model

    Args:
        data: pandas dataframe to preprocessed
    """
    log = logging.getLogger('main')

    log.info("")
    log.info("****************************************")
    log.info("*** pre_process")
    log.info("****************************************")
    return preprocessing.preprocess(data)
    #return preprocessing.prepro(data)

# %% DoModel


def make_model(x_train, x_test, y_train, y_test, dnan):
    """
    Fit the model on the data and predict salary when it's unknown

    Args:
        data: pandas dataframe to train and predict our model on
    """
    log = logging.getLogger('main')

    log.info("")
    log.info("****************************************")
    log.info("*** make_model")
    log.info("****************************************")
    return modeling.modelize(x_train, x_test, y_train, y_test, dnan)

# %% UpdateDB


def update_db(dataframe, data_krbf, data_forest):
    """
    Save the data in the DB

    Args:
        data: pandas dataframe to be saved in mongoDB
    """
    log = logging.getLogger('main')

    log.info("")
    log.info("****************************************")
    log.info("*** update_db")
    log.info("****************************************")

    krbd_df = pd.DataFrame(index=dataframe.index)
    krbd_df['salaire_rbf'] = np.nan

    for idx, row in data_krbf.iterrows():
        krbd_df.loc[idx, 'salaire_rbf'] = row[0]

    rf_df = pd.DataFrame(index=dataframe.index)
    rf_df['salaire_forest'] = np.nan

    for idx, row in data_forest.iterrows():
        rf_df.loc[idx, 'salaire_forest'] = row[0]

    dataframe = pd.concat([dataframe, krbd_df, rf_df], axis=1)

    db.save_df(dataframe, 'TEMP_BASE', 'MODEL_DATA')
    
    return dataframe

# %% Report


def make_report(dataframe):
    """
    Create a report and send it by email

    Args:
        data: pandas dataframe, maybe not useful
    """
    log = logging.getLogger('main')

    log.info("")
    log.info("****************************************")
    log.info("*** make_report")
    log.info("****************************************")
    reporting.report(dataframe)

# %% Command line options


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

    log = logging.getLogger('main')
    log.debug(sys.argv)
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

# %% Log


def init_log():
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
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    file_handler = logging.handlers.RotatingFileHandler('logfile.log', maxBytes=1000000, backupCount=3)
    file_handler.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # create formatters and add them to the handlers
    formatter_f = logging.Formatter('%(asctime)s %(name)-15s %(levelname)-8s %(message)s')
    formatter_c = logging.Formatter('%(name)-15s: %(levelname)-8s: %(message)s')
    file_handler.setFormatter(formatter_f)
    console_handler.setFormatter(formatter_c)

    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# %% Main


def main():
    """
    Main function
    """

    # Initialize the log system
    init_log()
    log = logging.getLogger('main')

    log.info("")
    log.info("")
    log.info("================================================================================")
    log.info("Main Start")
    log.info("================================================================================")

    # Read config data and check if needed folders exist
    cv.CFG.read_ini()
    cv.CFG.ensure_folders_exist()

    auto, scrap, working_data, cleaner, pre_process, model, update, report = handle_options()

    # Get the previous raw data from database
    db_data = db.load_df('TEMP_BASE', 'RAW_DATA')

    if scrap:
        # Scrap
        do_scraping(auto, db_data)

    if working_data:
        # Get a dataframe to work with
        jobs_df = get_working_data(db_data)

        # Save the new raw data if it changed
        if jobs_df.shape != db_data.shape:
            db.save_df(jobs_df, 'TEMP_BASE', 'RAW_DATA')

    if cleaner:
        # Clean
        cleaned_df = do_cleaning(jobs_df)

    if pre_process:
        # Preprocessing
        x_train, x_test, y_train, y_test, dnan = pre_processing(cleaned_df)

    if model:
        # Modelization
        predict_krbf, predict_rf = make_model(x_train, x_test, y_train, y_test, dnan)

    if update:
        # Update DB with results from models
        predict_df = update_db(jobs_df, predict_krbf, predict_rf)

    if report:
        # Create and send report
        make_report(predict_df)

    log.info("")
    log.info("================================================================================")
    log.info("Main End")
    log.info("================================================================================")

    # End the logging system
    logging.shutdown()

# %% Unique starting point of the script


main()
