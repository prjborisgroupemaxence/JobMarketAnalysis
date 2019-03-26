# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""
Created on Tue Mar 12 12:22:58 2019

Script file for the ML part

@authors: Radia, David, Martial, Maxence, Philippe B
"""

import pandas as pd
import numpy as np
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV


#%% Fonction Gridsearch avec SVR et kernel RBF, retourne le score

def gridperf(X_train_scaled, X_test_scaled, y_train, y_test, C_range = np.logspace(-2, 3, 6), gamma_range = np.logspace(-5, 3, 10), meth_score='r2', cvval=3):
    '''
    Apply a gridsearch with estimator SVR kernel RBF
    Param :
        Usual X_train, X_test, y_train, y_test
        C_range and gamma_range : range for C and gamma parameters, useful for SVR estimator
        meth_score and cvval : scoring and cv parameters useful for gridsearch
    return :
        clfk : estimator (SVR Kernel RBF) object
        the_score : the score of the object on 'y_test' from 'X_test'
    '''
    # Modify if needed y to get format (y,)
    try:
        if y_train.shape[1] == 1: y_train = y_train[:, 0]
    except IndexError:
        pass
    try:
        if y_test.shape[1] == 1: y_test = y_test[:, 0]
    except IndexError:
        pass
    
    # Tests gridsearch with C & gamma
    param_grid = dict(gamma=gamma_range, C=C_range) # parametres testés lors du gridsearch
    
    clf = GridSearchCV(SVR(), param_grid=param_grid, scoring=meth_score, cv=cvval)
    clf.fit(X_train_scaled, y_train)
    y_true, y_pred = y_test, clf.predict(X_test_scaled)
    
    # Kernel RBF model with the best parameters & print the score
    clfk = SVR(kernel='rbf', C=clf.best_params_['C'], gamma=clf.best_params_['gamma'])
    #A tester: clfk = clf.best_estimator_ # A la place de la ligne du dessus
    clfk.fit(X_train_scaled, y_train)
    #y_pred = clfk.predict(X_test_scaled)
    the_score = clfk.score(X_test_scaled,y_test)
    return clfk, the_score
    
#%%
import preprocessing as pp

# Determiner le df et cols_X

X_train, X_test, y_train, y_test, dnan = pp.start_prepro(df, cols_X, col_y='Salary')
obj_svrkrbf, num_score = gridperf(X_train, X_test, y_train, y_test, C_range=[34500], gamma_range=[0.4, 1])

predictions = pd.DataFrame(obj_svrkrbf.predict(X_test))

#%%
def modelize(df):
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
