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



def woo