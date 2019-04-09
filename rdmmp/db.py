# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""
Created on Tue Mar 12 12:22:57 2019

Code to get data from CSVs and the mongo database and to update it after the model

@authors: Radia, David, Martial, Maxence, Philippe B
"""

import pandas as pd
import numpy as np

import rdmmp.misc as misc


def update(data_krbf, data_rf):
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


def import_data_from_csv(folderpath, jobs, locations):
    """
    Return a dataframe with all scrap for every jobs and locations

    Parameters:
        folderpath: the location of scrap csv (ex : /scraping)
        jobs : list of all jobs (ex: jobs = ['Data Scientist', 'Developpeur', 'Business Intelligence', 'Data Analyst'] )
        locations : list of all location (ex: locations = ['Lyon', 'Paris', 'Toulouse', 'Bordeaux', 'Nantes'])

    Returns:
        alldata merged and with no duplicate rows
    """

    alldata = pd.DataFrame()
    for job in jobs:
        for loc in locations:
            # version temporaire pour récupérer tous les fichiers scrapés
            # bon code en commentaire après
            for i in range(2):
                if i == 0:
                    filepath = folderpath.joinpath(job.lower().replace(
                        ' ', '_') + '_' + loc.lower() + '.csv')
                else:
                    filepath = folderpath.joinpath(job.lower().replace(
                        ' ', '_') + '_' + loc.lower() + str(i) + '.csv')

                try:
                    temp = pd.read_csv(filepath, encoding='utf-8')

                    # backward compatibility :
                    if temp.shape[1] == 8:
                        temp.drop(temp.columns[0], axis=1, inplace=True)

                    temp['Job_Category'] = job
                    temp['Location_Category'] = loc

    # Get the duration of the code above
    duration = timeit.default_timer() - time_start
    # Log it
    logging.getLogger('main.db').info('Load_df: %.3fs', duration)

    return data
