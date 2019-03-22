# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 10:28:00 2019

@author: COLLARD M
"""
# %%
import pandas as pd
import rdmmp.helpgraph as helpgraph

import plotly 
# plotly.tools.set_credentials_file(username='mcollard', api_key='oMzhDLykT2GMtb9I5bAB')
from plotly.offline import plot
import plotly.graph_objs as go


# %% Hello world plotly version
trace = {'x':[1, 2], 'y':[1, 2]}
data = [trace]
layout = go.Layout(title='Mean and standard deviation for each Salary',
                   xaxis=dict(title='Job'),
                   yaxis = dict(title='Salary in euros')
                   )
fig = go.Figure(data=data, layout=layout)

plotly.offline.plot(fig, filename='graph/hello.html')  # auto_open=False

# %% Basic plot : bar plot of salaries
salary_stats = helpgraph.salary_job_stats(df)


def html_stats_salary(salary_stats):
    """
    Plot bar chart for mean/std salary of 5 jobs.
    The html code goes in the folder "/graph"

    Parameter:
        salary_stats : a dataframe get with salary_jo_stats function

    Returns:
        nothing : the html code is save in "/graph" folder
        """

    trace = go.Bar(x=salary_stats.columns,
                   y=salary_stats['mean'],
                   error_y=dict(type='data', array=salary_stats['std'],
                                visible=True),
                   orientation='h')

    layout = go.Layout(title='Mean and standard deviation for each Salary',
                       xaxis=dict(title='Job'),
                       yaxis=dict(title='Salary in euros')
                       )
    data = [trace]

    fig = go.Figure(data=data, layout=layout)

    plotly.offline.plot(fig, filename='graph/salary_stats.html',
                        auto_open=False)

    return
