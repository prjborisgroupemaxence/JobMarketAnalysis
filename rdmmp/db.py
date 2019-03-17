# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 12:22:57 2019

Code to get data from CSVs and the mongo database and to update it after the model

@authors: Radia, David, Martial, Maxence, Philippe B
"""

import pandas as pd

import rdmmp.misc as misc


def update(drf):
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

    pass

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
            filepath = folderpath + '/' + job.lower().replace(' ', '_') + '_' + loc.lower() + '.csv'
            try:
                temp = pd.read_csv(filepath, encoding='utf-8')
                
                # backward compatibility : 
                if temp.shape[1] == 8:
                    temp.drop(temp.columns[0], axis=1, inplace=True)
                    
                alldata = alldata.append(temp, ignore_index=True)
            except:
                print("Error reading {}...".format(filepath))

    alldata.drop_duplicates(inplace=True)

    return alldata

def import_data():
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

    jobs = ['Data Scientist', 'Developpeur', 'Business Intelligence', 'Data Analyst']
    locations = ['Lyon', 'Paris', 'Toulouse', 'Bordeaux', 'Nantes']

    return import_data_from_csv(misc.CSV_DIR, jobs, locations)
