# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 10:28:00 2019

@author: COLLARD M
"""
# %%
import pandas as pd
import numpy as np
import time
import rdmmp.helpgraph as helpgraph

import plotly 
# plotly.tools.set_credentials_file(username='mcollard', api_key='oMzhDLykT2GMtb9I5bAB')
from plotly.offline import plot
import plotly.graph_objs as go

# To plot pretty figures
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rc('axes', labelsize=14)
mpl.rc('xtick', labelsize=12)
mpl.rc('ytick', labelsize=12)

import os

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

# %% Basic stacled bar plot of city for each job
    
# I have no idea if its work
    
trace1 = go.Bar(x=salary_stats.columns,
    y=city_stats['Paris'][0],
    name='Paris',
    orientation = 'h',
    marker = dict(
        color = 'red',
    )
)
trace2 = go.Bar(x=salary_stats.columns
    y=city_stats['Lyon'][0],
    name='Lyon',
    orientation = 'h',
    marker = dict(
        color = 'yellow',
    )
)
trace3 = go.Bar(x=salary_stats.columns
    y=city_stats['Nantes'][0],
    name='Nantes',
    orientation = 'h',
    marker = dict(
        color = 'black',
    )
)
trace4 = go.Bar(x=salary_stats.columns
    y=city_stats['Toulouse'][0],
    name='Toulouse',
    orientation = 'h',
    marker = dict(
        color = 'whith',
    )
)    
trace5 = go.Bar(x=salary_stats.columns
    y=city_stats['Bordeaux'][0],
    name='Bordeaux',
    orientation = 'h',
    marker = dict(
        color = 'grey',
    )
)
data = [trace1, trace2, trace3, trace4, trace5]
layout = go.Layout(
    barmode='stack'
)

fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename=filename='graph/city_job_stats.html)
    

# %% Test of grouped (job) and stacked bar chart (city)
    
notStacked = go.Bar(x=salary_stats.columns,
                   y=salary_stats['mean'],
                   error_y=dict(type='data', array=salary_stats['std'],
                                visible=True),
                   orientation='h')

stacked1 = go.Bar(x=salary_stats.columns,
                  y=city_stats['Paris'][0],
                  name='Paris',
                  orientation='h',

)

stacked2 = go.Bar(

)

# %% go back to Matplotlib and save in graph folder .png

# Where to save the figures
IMAGES_PATH = "graph"

def save_fig(fig_id, tight_layout=True, fig_extension="png", resolution=300):
    date = time.strftime("%d%m%Y")
    path = os.path.join(date, IMAGES_PATH, fig_id + "." + fig_extension)
    print("Saving figure", fig_id)
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)

# %% 
salary_stats = helpgraph.salary_job_stats(df)
     
def plot_stats_salary(salary_stats):
    """
    Plot bar chart for mean/std salary of 5 jobs.
    The html code goes in the folder "/graph"

    Parameter:
        salary_stats : a dataframe get with salary_jo_stats function

    Returns:
        nothing : the .png fig is save in "/graph" folder
        """
    
    fig, ax = plt.subplots()
    
    job = list(salary_stats.columns.values)
    job_pos = np.arange(len(job))
    salary_mean = salary_stats['mean']
    salary_std = salary_stats['std']
    
    ax.barh(job_pos, salary_mean, xerr=salary_std, align='center')
    
    ax.set_yticks(job_pos)
    ax.set_yticklabels(job)
    ax.set_xlabel('Mean and standard deviation Salary for each Job')
    
    save_fig("stats_salary_job")
    
    return