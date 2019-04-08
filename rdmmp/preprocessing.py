# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 10:19:48 2019

@author: Administrateur
"""

#%% Imports
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
<<<<<<< HEAD
import rdmmp.cleaning
import rdmmp.db
import rdmmp.misc as misc
=======

def data_read():        
    #from sklearn.preprocessing import Imputer
    misc.CFG.read_ini()
    data = rdmmp.db.import_data()#'C:\Formation\Simplon-Dev_Data_IA\ML\Projet_groupe_Boris\Data_csv', jobs, locations)
    #data = cl.clean_salary(data)
    #data = cl.clean_job(data)
    #data = cl.clean_city(data)
    #data = cl.clean_posting(data)
    
    df = rdmmp.cleaning.clean(data)
    #df = pd.concat([df, data['Company']], axis=1)
    return df

#%% Functions used in 'prepro' !
##################################### DANS Check_Cols
# Check, utile dans le check des colonnes

# Check, utile dans le check des cols
def input_cols():
    '''
    Used to correct an incorrect column name \n
    return String, a string with the name corrected by the user (human)
    '''
    col_X = input('noms colonnes\t')
    return col_X

# Check, check col y
def check_col_y_name(df, col_y):
    '''
    check if col_y is a column's name in the df \n
    param : df, col_y: String, name of the column y \n
    return : String, column y's name (col_y)
    '''
    while col_y not in df:
        print('Error : col_y incorrect : %s is not in the df\'s names, pls enter a correct name' % col_y)
        col_y = input_cols()
    return col_y

# Check, utile dans le check des cols de X
def Help_check_colsX(df, cols_X):
    '''
    Check if cols_X are column's names available in the df
    
    param : 
        df : the df to check
        cols_X : List of Strings, column's names to be checked
        
    return : String, 'ok' if all is ok, else return the bad name to correct
    '''
    for i in cols_X:
        if i not in df.columns:
            #print("Colonne %s manquante dans le df (ou mal orthographiée), Modifiez le nom de colonne" % i)
            return i
    return 'ok'

def check_cols_X_names(df, col_y, cols_X=None):
    '''
    Check the column's names for X \n
    param :
        df : DF with, at least, the columns needed for X and y \n
        col_y : String,  name of the column y \n
        cols_X=None : If None, cols_X will be deduced, else List of Strings, which will be checked
        
    return : List of Strings with the correct names of X (cols_X)
    '''
    #soit déduit de df grace a col_y
    if cols_X == None:
        cols_X = list(df.drop([col_y], axis=1))
        
    #soit choisi par l'utilisateur
    else:
        if col_y in cols_X:
            print('Vous avez mis votre colonne y dans vos colonnes X, recommencez X')
            return None
        cc = Help_check_colsX(df, cols_X)
        while cc != 'ok':
            print('Nom de colonne: %s est inexistant dans le df, modifiez le nom !' % cc)
            cols_X[cols_X.index(cc)] = input_cols()
            cc = Help_check_colsX(df, cols_X)
        
    return cols_X

##################################### Dans prepa_1
# Etape, Check, Check le noms des colonnes
def Check_Cols(df, col_y, cols_X=None):
    '''
    Main of the checks cols for X and y \n
    param :
        df : DF with, at least, the columns needed for X and y \n
        col_y : String,  name of the column y \n
        cols_X=None : If None, cols_X will be deduced, else List of Strings, which will be checked
        
    return : Tuple with :
        List of Strings with the correct names of X (cols_X)
        String, column y's name (col_y)
    '''
    col_y = check_col_y_name(df, col_y)
    cols_X = check_cols_X_names(df, col_y, cols_X)
    if cols_X == None:
        return print('y in X'), col_y
    return cols_X, col_y


# Special
def convert_to_nan(string):
    '''
    replace a cell string by np.nan value \n
    param : String \n
    return : NAN \n
    Used with apply()
    '''
    if (string == '') or (string =="nan") or (string ==" "):
        string = None
    return string

# Convert every special Xnan with None or nan
def conv_nan_none(df, cols):
    '''
    Call a function which will apply a value to each column of the df
    param : DF, cols: List of Strings with the names of the columns you want to apply
    return DF
    '''
    for i in cols:
        df[i] = df[i].apply(convert_to_nan)
    return df

# Etape, Action, suppression des NAN de X
def delr_nan_X(df, cols_X):
    '''
    Delete rows of X with 'NAN' value (don't care about NAN in col_y) \n
    param : df, col_y = String, name of column y \n
    return : df without the rows which got NAN in X (df - col_y)
    '''
    df = conv_nan_none(df, cols_X)
    if df[cols_X].isnull().sum().sum() != 0:
        df.dropna(subset=cols_X, inplace=True)
    return df

# Etape, Action, Separation des lignes contenant les y NAN et les y valeur
def splr_nan_y(df, col_y):
    '''
    Split rows between 'col_y' == 'NAN' and filled ones \n
    param : df, col_y = String, name of column y \n
    return both dfs : 1st df with col_y filled, 2nd dn with col_y with NAN \n
    Warning : print a Warning if no NAN in col_y, cause this function is unuseful
    '''
    df[col_y] = df[col_y].apply(convert_to_nan) # Ou aussi df = conv_nan_none(df, [col_y])
    if df[col_y].notnull().all():
        print("Warning, it's strange cause no 'NAN' in", col_y)
        dn = pd.DataFrame()
        return df, dn
    else:
        dn = df[df[col_y].isnull()]
        df = df[df[col_y].notnull()]
    return df, dn

# Etape, Action, Separation des lignes entre X_train, X_test, y_train, y_test
def divtraintest(X, y, test_size=0.25):
    '''
    Do the train/test with prints and size by default 0.25 \n
    param : X = DF, y = DF and the test_size = Float, the % of test rows \n
    return : DF : X_train, X_test, y_train, y_test
    '''
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    print("Nb rows dans X_train: %d" % len(X_train), "\tNb rows dans X_test: %d" % len(X_test))
    print("Nb rows dans y_train: %d" % len(y_train), "\tNb rows dans y_test: %d" % len(y_test))
    return X_train, X_test, y_train, y_test

##################################### DANS Prepro

def prepa_1(df, col_y, cols_X=None, delrnanx=True, forpred=False):
    '''
    First part of the preprocessing \n
    Parameters:
        df: The Dataframe which will be preprocessed
        col_y = String with the y column's name, ie: 'Salary'
        cols_X=None, List of Strings, names of the columns that should be in X
            ie:['CleanCity','Company','CleanJob']
            If cols_X is None : cols_X is deduced (df - col_y)
        delrnanx=true : if NANs in X should delete the rows
        forpred=False : if True, you use the function for prediction which y are NAN

    Returns:
        DF : X_train, X_test, y_train, y_test
        dn = DF with the NAN in col_y
        With forpred=True : return: 2 DF: dn, X
        
    Warning with the first function 'delr_nan_X' cause NAN in X will delete rows
    '''
#Check_Cols :
    cols_X, col_y = Check_Cols(df, col_y, cols_X)
    if cols_X == None:
        raise TypeError("pbm with cols_X") ###########################
#GNX : On supprime les NAN de X :
    if delrnanx:
        df = delr_nan_X(df, cols_X) # Attention avec un autre DF
        
#Synan : Separation des lignes : les y NAN et les y Valeur
    # df is the DF to train and test cause every y are values
    # dn is the DF to predict cause every y are NAN
    df, dn = splr_nan_y(df, col_y)
    
#ScolXy : Separation des colonnes : les colonnes X d'un coté et la colonne y de l'autre
    
    if forpred:
        X = dn[cols_X]
        return X, dn
    
    # Determine X
    X = df[cols_X]
    
    # Determine y :
    y = df[col_y]

#Split_tt : Split train_X, ..., y_test
    X_train, X_test, y_train, y_test = divtraintest(X, y)
    return X_train, X_test, y_train, y_test, dn, df

################################

def search_missing_col(dfa, dfb, string=True):
    '''
    return the name(s) of dfb's columns which are not in dfa
    params : both df witch will return (dfa - dfb) names
        string : True if you want to return a string instead of a list of strings
    return : String OR List with the column names that are in dfb but missing in dfa
    '''
    g = str(','.join(set( dfa.columns ) - set( dfb.columns )))
    if string: return g
    else:
        g = g.split(',')
        return g

def double_search_missing_col(dfa, dfb):
    '''
    return the names of 2 df columns with difference between them \n
    params : 2 DF which column's names will be compared \n
        
    return : 2 Lists of String OR 1 List of Strings and 1 empty List OR 2 empty lists
    
    Warning, if all the columns of 2 df are in the other one, this list will return empty
    '''
    lab = search_missing_col(dfa, dfb, string=False)
    lba = search_missing_col(dfb, dfa, string=False)
    if len(lab) == 1:
        if lab[0] == '':lab = []
    if len(lba) == 1:
        if lba[0] == '':lba = []
    return lab, lba

def add_val_to_dfcol(df, name_col, val=0):
    '''
    Modify all the values of 1 column of the df, if column does not exists, it'll be created \n
    param: DF
        name_col: String or List with 1 String
        val=0 : Value to fill the column \n
    return: the DF modified OR not mofified if Error
    
    Warning, the DF will really be modified, use .copy() before if you want to save it
    '''
    if not isinstance(name_col, list) and not isinstance(name_col, str):
        print('Error: name_col should be a string or List of string, no modification on df')
        return df
    else:
        if isinstance(name_col, list):
            if len(name_col) != 1:
                print('Error: only 1 column name in your list: name_col, no modification on df')
                return df
            else:
                name_col = str(name_col[0])
    df[name_col] = val
    return df

def add_missing_cols(dfa, dfb, both=True):
    '''
    Between 2 DF : Add columns which are missing in dfb from dfa \n
    If both=True, it will add in both DF completing each other missing columns \n
    param: Both DF
        both=True : If will add in both DF and not only in dfb \n
    return: both DF
    '''
    dfa_dfb, dfb_dfa = double_search_missing_col(dfa, dfb)
    if not not dfa_dfb:
        for i in dfa_dfb:
            add_val_to_dfcol(dfb, i)    
    if both:
        if not not dfb_dfa:
            for i in dfb_dfa:
                add_val_to_dfcol(dfa, i)
    else: print('1st DF (dfa) has not been modified ! cause both=False')
    return dfa, dfb

################################

# Etape, Action, GD
def action_X(Xt, drop1=True):
    '''
    GetDummies(GD), with drop_first by default, on pd.DataFrame with ONLY categorical \n
    param: DF with X columns (not y) to be GD, ONLY categorical columns ! \n
        drop1: Boolean, True if GD with drop_first
    return: new DF converted by get_dummies
        return None if problem
    
    Warning ONLY for DF with CATEGORICAL FEATURES !
    '''    
    # Ready for getdummies via multidum(X) with a categorical Xt
    if not isinstance(Xt, pd.DataFrame): return print("Parameter Xt should be pd.DataFrame")
    else:
        X_gd = pd.get_dummies(Xt, drop_first=drop1)
        # Deletion column named NAN if exists
        if 'nan' in X_gd.columns:
            X_gd = X_gd.drop(['nan'], axis=1)
            
    return X_gd

#%% Preprocessing at the beginning
# Preprocessing for pred
def prepro_pred(dn, col_y='Salary', cols_X=None, delrnanx=True):
    '''
    Preprocessing of a pred dataset which every columns should be categorical !
    
    Parameters:
        df: The Dataframe which will be preprocessed
        col_y = String with the y column's name, ie: 'Salary'
        cols_X=None, List of Strings, names of the columns that should be in X
            ie:['CleanCity','Company','CleanJob']
            If cols_X is None : cols_X is deduced (df - col_y)
        delrnanx=true, if NANs in X should delete the rows
        
    return:
        DF : X_pred, X ready to accept the model object to predict y NAN
        dn = DF with the NAN in col_y
        
    Warning with the first function of prepa_1 'delr_nan_X' cause NAN in X will delete rows
    '''
    forpred=True
    if not isinstance(dn, pd.DataFrame):
        raise TypeError("Error: process stopped cause dn is not a DF")###################
    

    X, dn = prepa_1(dn, col_y, cols_X, delrnanx, forpred)
#    raise TypeError('Error, read precedent message, maybe y is in X')
    
    
    
    X_pred_gd = action_X(X)
    
    return X_pred_gd, dn


def prepro(df, col_y='Salary', cols_X=None, delrnanx=True):
    '''
    Preprocessing of a dataset which every columns should be categorical !
    For remind : For Data supervised, y is needed
    
    Parameters:
        df: The Dataframe which will be preprocessed
        col_y = String with the y column's name, ie: 'Salary'
        cols_X=None, List of Strings, names of the columns that should be in X
            ie:['CleanCity','Company','CleanJob']
            If cols_X is None : cols_X is deduced (df - col_y)
        delrnanx=true, if NANs in X should delete the rows
        
    Return:
        DF : X_train, X_test, y_train, y_test
        dn = DF with the NAN in col_y
        
    Warning with the first function of prepa_1 'delr_nan_X' cause NAN in X will delete rows
    '''
    #df_orig = df.copy()

    X_train, X_test, y_train, y_test, dn, df = prepa_1(df, col_y, cols_X, delrnanx)

    X_train_gd = action_X(X_train)
    X_test_gd = action_X(X_test)
    if not isinstance(X_train_gd, pd.DataFrame):
        raise TypeError("Error: process stopped cause X_train is not df")
    if not isinstance(X_test_gd, pd.DataFrame):
        raise TypeError("Error: process stopped cause X_test is not df")
    
    add_missing_cols(X_train_gd, X_test_gd)
    
    if not dn.empty:
        X_pred_gd, dn = prepro_pred(dn, col_y, cols_X)
        if set(X_pred_gd.columns) != set(X_train_gd.columns):
            print('Some categorical values does not match with a Salary and so had been deleted')
            pdst, tdsp = double_search_missing_col(X_pred_gd, X_train_gd)
            for i in pdst:
                del X_pred_gd[i]
            if not not tdsp:
                for j in tdsp:
                    print('Careful the feature %s will be deleted from the train and test' %j)
                    del X_train_gd[j]; del X_test_gd[j]
    else: X_pred_gd = pd.DataFrame()
    
    return X_train_gd, X_test_gd, y_train, y_test, X_pred_gd, dn, df


#%% Pour modifier les parametres
if __name__ == "__main__":
        
    df = data_read()
    col_y = 'Salary'
    cols_X = ['City','Job']
    
    Final_X_train, Final_X_test, y_train, y_test, X_pred, dn, df = prepro(df, col_y, cols_X)


################################################################################
# Tests des sous_fonctions
def try1():
    df = data_read()
    col_y = 'Salary'
    
    # Check, check col y
    col_y = check_col_y_name(df, col_y)
    
    cols_X = check_cols_X_names(df, col_y, cols_X)
    
    cols_X, col_y = Check_Cols(df, col_y, cols_X)
    
    # Convert every special Xnan with None
    df = conv_nan_none(df, cols_X)
    
    # Etape, Action, suppression des NAN de X
    df = delr_nan_X(df, cols_X)
    
    # Etape, Action, Separation des lignes contenant les y NAN et les y valeur
    df, dn = splr_nan_y(df, col_y)
    
    X = df[cols_X]
    y = df[col_y]
    
    # Etape, Action, Separation des lignes entre X_train, X_test, y_train, y_test
    X_train, X_test, y_train, y_test = divtraintest(X, y, test_size=0.25)

#RESET
def try2():
    df = data_read()
    col_y = 'Salary'
    
    X_train, X_test, y_train, y_test, dn, df = prepa_1(df, col_y)
    
    FX_train = action_X(X_train)

# PREPRO !!! Reset
def try3():
    df = data_read()
    col_y = 'Salary'
    cols_X = ['City','Job']
    
    return prepro(df, col_y, cols_X)

###############
