# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 10:51:31 2019

Code to help for ploting useful graph.

@authors: Maxence
"""

def salary_job_stats(df):
    """
    Get the stats (count, mean, std, min, 25%, 50%, 75%, max) for each job
    (Data Scientist, BI, Data Analyst, Developpeur, Data Engineer)

    Parameter:
        df : a dataframe with salary and job title

    Returns:
        salary_df : a dataframe with mean/std salary for each job
    """

    # Stats for each job (even junior, alternance, etc)
    salary_stats = df.groupby('Job')['Salary'].describe().reset_index()

    salary_df = salary_stats.T  # To have job title columns

    # Keep only 5 jobs titles
    col_to_keep = ['data scienstist', 'data analyst', 'business intelligence',
                   'developpeur']
    salary_df.drop(salary_df.columns.difference(col_to_keep), axis=1,
                   inplace=True)

    return salary_df


<<<<<<< HEAD
def stats_city_job(df):
    """
    Get the stats (count, mean, std, min, 25%, 50%, 75%, max) for each city
    (Paris, Nantes, etc..)

    Parameter:
        df : a dataframe with job and city columns

    Returns:
        salary_df : a dataframe with count each job per city
    """
    # Stats on 5 basic job
    row_to_keep = ['data scienstist', 'data analyst', 'business intelligence',
                   'developpeur']
    
    df = df[df['Job'].isin(row_to_deep)]
    
    # Stats for each city (even junior, alternance, etc)
    city_stats = df.groupby('City')['Job'].describe().reset_index()

    city_df = city_stats.T  # To have job title columns
    
    return city_df['count']