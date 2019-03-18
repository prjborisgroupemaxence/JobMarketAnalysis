# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""
Created on Tue Mar 12 12:22:58 2019

Code to clean the dataframe, to get useful data from posting column

@authors: Radia, David, Martial, Maxence, Philippe B
"""
import pandas as pd
import numpy as np
import re

# Start by cleaning the job title column
def clean_job(data, jobtitle=['Data Analyst', 'Data Scientist', 'Junior', 'Stage', 'Business Analyst', 'Data Engineer',
                        'Ingénieur Data', 'Alternance', 'Développeur']):
    """
    Create a new column with job title clean and ready to use by a ML model

    Parameter:
        jobtitle: list of job (ex: jobtitle = ['Data Analyst', 'Data Scientist', 'Junior', 'Stage', 'Business Analyst', 'Data Engineer', 'Ingénieur Data', 'Alternance', 'Développeur'])
        data : dataframe with a Title column to process

    Returns:
        data : a dataframe with a new clean column title
    """

    fulldata['CleanJob'] = " "  # Create new column

    for i, dirtytitle in enumerate(data['Title']):

        dirtytitle = dirtytitle.lower()  # in lower case for comparaison

        for clean_title in jobtitle:
            clean_title = clean_title.lower()

            if clean_title in dirtytitle:
                # add all key title in CleanJob column
                fulldata['CleanJob'][i] += clean_title + " "
            else:
                pass

    return data

# Clean salary column
def clean_salary(data):
    """
       Create a new column with salary clean and ready to use by a ML model

       Parameter:
           data : dataframe with a Salary column to process

       Returns:
           data : a dataframe with a new clean column salary (we take the mean for a range salary)

       Warnings : A value is trying to be set on a copy of a slice from a DataFrame
       BUT it's working and futher insight may be fix it.

       """
    pd.options.mode.chained_assignment = None  # default='warn'

    # match salary for : 30000 € - 45000 € per year
    pattern1 = r"(\d+) € - (\d+) € par an"
    # match 55000 € per year
    pattern2 = r"^(\d+)(?= € par an)"
    # macth 1750 € per month
    pattern3 = r"^(\d+)(?= € par mois)"
    # match salary for : 1750 € - 4500 € per month
    pattern4 = r"(\d+) € - (\d+) € par mois"

    data['CleanSalary'] = np.nan

    data['Salary'] = data['Salary'].astype(str)  # convert nan to str for regex

    for i, txtsal in enumerate(data['Salary']):

        # handle : xxxx € - xxxx € per year thus we take the mean
        if re.match(pattern1, txtsal):
            extract = re.findall(pattern1, txtsal)  # for a range salary, return a tuple ex: ('30000', '45000')
            mean = (int(extract[0][0]) + int(extract[0][1])) / 2
            data['CleanSalary'][i] = int(mean)

        # handle : xxxx € - xxxx € per month thus we take the mean*12
        elif re.match(pattern4, txtsal):
            extract = re.findall(pattern4, txtsal)  # for a range salary, return a tuple ex: ('3000', '4500')
            mean = ((int(extract[0][0]) + int(extract[0][1])) / 2) * 12
            data['CleanSalary'][i] = int(mean)

        # handle xxxx € per year
        elif re.match(pattern2, txtsal):
            extract = re.findall(pattern2, txtsal)  # return a list
            data['CleanSalary'][i] = int(extract[0])

            # handle xxxx € per month thus we *12
        elif re.match(pattern3, txtsal):
            extract = re.findall(pattern3, txtsal)  # return a list
            year = int(extract[0]) * 12  # convert in salary by year
            data['CleanSalary'][i] = int(year)

        else:
            data['CleanSalary'][i] = np.nan

    return data

# Clean City column
def clean_city(data):
    """
    Create a new column with city clean (CleanCity) and ready to use by a ML model

    Parameter:
        data : dataframe with a City column to process

    Returns:
        data : a dataframe with a new clean column city (we take the mean for a range salary)

    """
    pd.options.mode.chained_assignment = None  # default='warn'

    dpt = {'IleDeFrance': ['91', '92', '93', '94', '95', '77', '78'],
           'Nantes': ['44'],
           'Toulouse': ['31'],
           'Bordeaux': ['33'],
           'Lyon': ['69']
           }

    rownan = []

    data['CleanCity'] = 'nan'

    for i, city in enumerate(fulldata['City']):
        for key, value in dpt.items():

            # Start by check if the city contains a key name city
            if key in city:
                data['CleanCity'][i] = key
                rownan.append(i)

            # if not, we check for a zip code and replace by the key associated
            elif key not in city:
                for elm in value:
                    if elm in city:
                        data['CleanCity'][i] = key

    return data

# Clean Posting column
def clean_posting(data):
    """
        Create a new column with city clean (CleanCity) and ready to use by a ML model

        Parameter:
            data : dataframe with a posting column to process

        Returns:
            data : a dataframe with a new clean posting column  (Named CleanPosting)

    """


    return data


# Call all cleaner function
def clean(data):
    """
    Clean all Title Job, City, Salary, Posting

    Parameter:
        data : dataframe with Title, City, Salary, Posting columns to process

    Returns:
        cleanData : a dataframe with only columns clean

    """
    cleanJob = clean_job(data)
    cleanCity = clean_city(data)
    cleanSalary = clean_salary(data)
    # cleanPosting = clean_posting(data)

    cleanData = pd.concat([cleanJob['CleanJob'], cleanCity['CleanCity'], cleanSalary['CleanSalary']], axis=1,
                          keys=['Job', 'City', 'Salary'])
    return cleanData