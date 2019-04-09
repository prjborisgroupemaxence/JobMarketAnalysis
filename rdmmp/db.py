# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""
Created on Tue Mar 12 12:22:57 2019

Code to get data from CSVs and the mongo database and to update it after the model

@authors: Radia, David, Martial, Maxence, Philippe B
"""
import timeit
import logging

import pandas as pd
import pymongo


# %% Helper functions


#Pour alleger la memoire lors de l'insertion dans la bdd
def slice_generator(df, chunk_size=2):
    current_row = 0
    total_rows = df.shape[0]
    while current_row < total_rows:
        yield df[current_row:current_row + chunk_size]
        current_row += chunk_size

def inser_light(df, mycoll):
    xids = []
    for df_chunk in slice_generator(df):
        records = df_chunk.to_dict(orient='records')
        inser_many = mycoll.insert_many(records)
        xids.append(inser_many.inserted_ids)
    return inser_many, xids

# %% Save a dataframe to a mongoDB collection


def save_df(dataframe, db_name, collection_name):
    """
    Connect to a MongoDB client, get the db, delete the collection, then save the new data in the collection

    Args:
        dataframe: Dataframe to save
        db_name: Name of the database
        collection_name: Collection to save the data in
    """
    # Saving starting time
    time_start = timeit.default_timer()

    conn_mdb_str = 'mongodb://localhost:27017/'

    # creation d'une instance mongo
    myclient = pymongo.MongoClient(conn_mdb_str)
    # creation de la db
    mydb = myclient[db_name]

    # Suppression d'une collection
    # au cas où elle existe
    mydb.drop_collection(collection_name)

    # creation de la collection
    mycollec = mydb[collection_name]
    docs, docids = inser_light(dataframe, mycollec)
    
    # Get the duration of the code above
    duration = timeit.default_timer() - time_start
    # Log it
    logging.getLogger('main.db').info('Save_df: %.3fs', duration)

# %% Load data from a mongoDB collection


def load_df(db_name, collection_name):
    """
    Connect to a MongoDB client, get the db, get the collection, load the data in the collection in a dataframe

    Args:
        db_name: Name of the database
        collection_name: Collection to read the data from

    Returns:
        a dataframe of the data in the collection
    """
    # Saving starting time
    time_start = timeit.default_timer()
    
    conn_mdb_str = 'mongodb://localhost:27017/'

    # creation d'une instance mongo
    myclient = pymongo.MongoClient(conn_mdb_str)
    # creation de la db
    mydb = myclient[db_name]
    # creation de la collection
    mycollec = mydb[collection_name]

    # Pour voir les documents
    data = mydb.data
    data = pd.DataFrame(list(mycollec.find()))
    
    # Drop the _id column mongoDB automatically added
    data.drop('_id', axis=1, inplace=True)
    
    # Get the duration of the code above
    duration = timeit.default_timer() - time_start
    # Log it
    logging.getLogger('main.db').info('Load_df: %.3fs', duration)

    return data
