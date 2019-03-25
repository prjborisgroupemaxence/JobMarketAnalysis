# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 10:19:48 2019

@author: Administrateur
"""

#%% Imports
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

#%% ################## A suppr d'ici - Sert juste pour tester 'prepro' !
jobs = ['Data Scientist', 'Developpeur', 'Business Intelligence', 'Data Analyst']
locations = ['Lyon', 'Paris', 'Toulouse', 'Bordeaux', 'Nantes']

import re
def importdata(folderpath, jobs, locations):
    """
    Return a dataframe with all scrap for every jobs and locations
    
    Parameters:
        folderpath: the location of scrap csv (ex : /scraping)
        jobs : list of all jobs (ex: jobs = ['Data Scientist', 'Developpeur', 'Business Intelligence', 'Data Analyst'] )
        locations : list of all location (ex: locations = ['Lyon', 'Paris', 'Toulouse', 'Bordeaux', 'Nantes'])
    
    Returns:
        alldata merged and with no duplicates row
        
    Possible warning : 
        C:\ProgramData\Anaconda3\lib\site-packages\pandas\core\frame.py:6692: FutureWarning: Sorting because non-concatenation axis is not aligned. A future version
        of pandas will change to not sort by default.
        To accept the future behavior, pass 'sort=False'.
        To retain the current behavior and silence the warning, pass 'sort=True'.
    """
    try:
        alldata = pd.DataFrame()
        for job in jobs:
            for loc in locations:
                filepath = folderpath + '/' + job.lower().replace(' ','_') + '_' + loc.lower() + '.csv'
                temp = pd.read_csv(filepath, encoding='utf-8')
                alldata = alldata.append(temp, ignore_index=True)
    except:
        pass
    alldata.drop_duplicates(inplace=True)
    alldata.drop('Unnamed: 0', axis=1, inplace=True)
      
    return alldata

#%% ################## A suppr d'ici - Sert juste pour tester 'prepro' !

import cleaning as cl
#from sklearn.preprocessing import Imputer
data = importdata('C:\Formation\Simplon-Dev_Data_IA\ML\Projet_groupe_Boris\Data_csv', jobs, locations)
#data = cl.clean_salary(data)
#data = cl.clean_job(data)
#data = cl.clean_city(data)
#data = cl.clean_posting(data)

df = cl.clean(data)
df = pd.concat([df, data['Company']], axis=1)

#%% Functions used in 'prepro' !
def check_colsX(df, cols_X):
    '''
    Check if cols_X are column's names available in the df
    param : 
        df : the df to check
        cols_X : column's names to be checked
    No return
    '''
    for i in cols_X:
        if i not in df.columns:
            print("Colonne %s manquante dans le df (ou mal orthographiée), Modifiez le nom de colonne" % i)
            return i
    return 'ok'

# sp check
def input_cols():
    '''
    Used to correct an incorrect column name
    return a string with the name corrected by the user (human)
    '''
    col_X = input('noms colonnes')
    return col_X

def check_X(x, col_y):
    '''
    called in 'def prepro' to check that y or 'Salary' not in X
    param : x and name of column y in str format
    return : x if no matter, else None which will quit 'def prepro'
    '''
    if col_y in x.columns:
        x.drop(col_y, axis=1, inplace=True)
        print('Vous aviez mis votre colonne y dans X, cette colonne a été enlevée de X !')
    if 'Salary' in x:
        Sal = input('Attention ! vous avez mis la colonne Salary dans X, voulez-vous continuer ?\nyes or no')
        if Sal != 'yes' and Sal != 'y':
            print('Enlever Salary de votre X')
            return 1
    return x

def multidum(X):
    '''
    GetDummies(GD), with drop_first, on np.ndarray or pd.DataFrame with ONLY categorical
    Parameter : array/df to be GD
    Return : New Dataframe modified by GD
    '''
    if isinstance(X, pd.DataFrame):
        X = X.values
    if isinstance(X, np.ndarray):
        try:
            if X.shape[1] > 0: pass
        except:
            X = np.array(X).reshape(len(X),1)
        rs, cs = X.shape
        X_temp = [0]*cs
        for i in range(cs):
            X_temp[i] = pd.get_dummies(X[:, i], drop_first=True)
        Final_X = X_temp[0]
        if len(X_temp) >1:
            for l in range(1, cs):
                Final_X = pd.concat([Final_X,X_temp[l]],axis=1)
    else: return print("Parameter X should be np.array or pd.DataFrame")
    return Final_X

def divtraintest(X, y, test_size=0.25):
    '''
    Do the train/test with prints and size by default 0.25
    param : X, y and the test_size
    return : X_train, X_test, y_train, y_test
    '''
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    print("Nb rows dans X_train: %d" % len(X_train), "\tNb rows dans X_test: %d" % len(X_test))
    print("Nb rows dans y_train: %d" % len(y_train), "\tNb rows dans y_test: %d" % len(y_test))
    return X_train, X_test, y_train, y_test

#%%
def prepro(df, cols_X, col_y='Salary'):
    '''
    Preprocessing of a dataset which every columns must be categorical
    For Data supervised, y is needed
    
    Parameters:
        df: The Dataframe which will be preprocessed
        cols_X: List with the names of the columns (string) that should be in X
            ie:['CleanCity','Company','CleanJob']
        col_y: string with the target y column name, ie: 'Salary'
        
    Returns:
        X_train, X_test, y_train, y_test
        dn : df with the NAN in col_y
    '''
    chtemp1 = check_colsX(df, cols_X)
    if chtemp1 != 'ok':
        return print('Error in check_cols_X')
    else: del chtemp1
    
    # Split rows between 'col_y' == 'NAN' and filled ones
    dn = df[df[col_y].isnull()]
    if len(dn) == 0:
        print("Warning, it's strange cause no 'NAN' in", col_y)
    df = df[df[col_y].notnull()]
    
    # Delete rows with 'NAN' value
    if df.isnull().sum().sum() != 0:
        df.dropna(inplace = True)
    
    ###### On se decidera sur : soit on vire la ligne et cols_X est passé en param ######
    # soit on vire le '#' ci-dessous, cols_X est déduit, et le param 'cols_X' degage dans la def !
    
    #cols_X = list(data.drop([col_y], axis=1))
    X = df[cols_X]
    X = check_X(X, col_y)
    try:
        if X == 1:
            return print('Error : check_X')
    except ValueError:
        pass
    
    y = df[col_y].values
    X = X.values
    
    # Ready for getdummies via multidum(X) with a categorical X
    Final_X = multidum(X)
    
    if 'nan' in Final_X.columns:
        Final_X = Final_X.drop(['nan'], axis=1)
    
    
    
    X_train, X_test, y_train, y_test = divtraintest(Final_X, y)
    
    return X_train, X_test, y_train, y_test, dn

#%% Utilisation de prepro

def start_prepro(df, cols_X, col_y='Salary'):
    cc = check_colsX(df, cols_X)
    while cc != 'ok':
        print('Noms de colonnes %s inexistantes dans df, recommencez !' % cc)
        cols_X[cols_X.index(cc)] = input_cols()
        cc = check_colsX(df, cols_X)
    X_train, X_test, y_train, y_test, df_y_only_nan = prepro(df, cols_X, col_y='Salary')

#%%
df
col_y = 'Salary'
cols_X = ['City','Job']

