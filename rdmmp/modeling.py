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
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV


# %% Random Forest


def random_forest(train_features, test_features, train_labels, test_labels, n, n_estimators_try_1,  max_features_try1, booleen, n_estimators_try_2, max_features_try_2):
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

#Nous convertissons les variables labels et features en numpy array pour un meilleur usage plus tard  
#
#    labels = np.array(labels)
#    features = np.array(features)

#Nous séparons le set d'entraînement et le set test
    
#    train_features, test_features, train_labels,  test_labels = train_test_split(features, labels, test_size = 0.25, random_state = 42)                                                                          

#Il s'agit d'un entraînement sur un modèle random forest, nous faisons donc appel à la fonction RandomForestRegressor 

    rf = RandomForestRegressor(n_estimators= n, random_state=42)  

#On entraîne le modèle sur le set d'entraînement

    rf.fit(train_features, train_labels) 

#Afin de trouver la combinaison des hyperparamètres qui permet d'obtenir le meilleur modèle de prédiction
#On essaie 12 (3*4) combinaisons d'hyperparamètres. n_estimators et max_features contiennent des listes. Puis on essaie 6 (2*3) combinaisons avec l'hyperparamètre bootstrap = False'''
    
    param_grid = [          
            {'n_estimators': n_estimators_try_1, 'max_features': max_features_try1 },
            
            {'bootstrap': booleen, 'n_estimators': n_estimators_try_2, 'max_features': max_features_try_2},
          ]
#On va évaluer le modèle en fonction des différents hyperparamètres définis dans param_grid. 
#On introduit comme paramètre dans la fonction GridSearch: la fonction random forest et param_grid 
   
    grid_search = GridSearchCV(rf, param_grid, cv=5,
                               scoring='r2', return_train_score=True)

#On entraîne le modèle avec chaque combinaison d'hyperparamètres  sur le set d'entraînement 
    grid_search.fit(train_features, train_labels)
    
#On effectue le paramétrage qui donne les meilleurs résultats sur les données d'entraînement.
    
    grid_search.best_params_ 

#On introduit la fonction qui permet d'obtenir le meilleur sstimateur choisi par la recherche, 
#c'est-à-dire qui a attribué le score le plus élevé (ou la plus petite perte, le cas échéant) aux données omises.
        
    rf_new =  grid_search.best_estimator_ 
    

#grid_search.cv_results_ permet d'obtenir un dictionnaire avec des clés comme en-tête de colonne et des valeurs comme colonne, pouvant être importées dans un pandas DataFrame.'''
    
    cvres = grid_search.cv_results_
    
    for mean_score, params in zip(cvres["mean_test_score"], cvres["params"]):
        print(mean_score, params)
        
#On entraîne le modèle disposant des meilleurs hyperparamètres sur le set d'entraînement
    
    rf_new.fit(train_features, train_labels)
    
#On évalue l'importance des features
    
    feature_importances = grid_search.best_estimator_.feature_importances_
    
    return   rf_new    
    
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
    
# %%
    

def modelize(X_train, X_test, y_train, y_test, dnan):
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
    # Kernel RBF
    # Determiner le df et cols_X
    obj_svrkrbf, num_score = gridperf(X_train, X_test, y_train, y_test, C_range=[34500], gamma_range=[0.4, 1])
    
    predictions_svrkrbf = pd.DataFrame(obj_svrkrbf.predict(X_test))
    
    # Random Forest
    obj_rf = random_forest(X_train, X_test, y_train, y_test, 100, [50,100,150],[4,8,12], [False], [25,40,120], [2,6,10])
    predictions_rf = pd.DataFrame(obj_rf.predict(X_test))
    
    return predictions_svrkrbf, predictions_rf
    
