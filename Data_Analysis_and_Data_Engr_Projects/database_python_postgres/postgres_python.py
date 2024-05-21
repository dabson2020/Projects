
# Data Engineering Project
# - In this project, the following functions were created:
#  - create the database
#  - drop tables
#  - create tables
#  - Read data from multiple files
#  - Data cleaning
#  The cleaned data is inserted into the tables created in the database
# 
#  - Postgres database was utilized to warehouse the clean data


# Pip Install the libraries if you dont have them previously installed

# %%
import psycopg2 as pg
import pandas as pd
import os
import glob
import warnings
warnings.filterwarnings('ignore')


# Create a function to connect to the database

# %%
def create_database():
    # connect to default database
    conn = pg.connect(host = '127.0.0.1', dbname='postgres', user='postgres', password='your_password')
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    # create sparkify database with UTF8 encoding
    cur.execute('DROP DATABASE IF EXISTS accounts')
    cur.execute('CREATE DATABASE accounts')

    # Close connection to default database
    conn.close()

    # connect to sparkify database
    conn = pg.connect(host = '127.0.0.1', dbname='accounts', user='postgres',   password='your_password')
    cur = conn.cursor()

    return cur, conn


# Function to drop tables

# %%
def drop_tables(cur, conn):
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()   


def create_tables(cur, conn):
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


# Read all the csv files

def get_files(folder_path):
    #list all files in the folder
    file_list = os.listdir(folder_path)
    dataframes = []
    for file in file_list:
        if file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path)
            dataframes.append((file,df))
    return dataframes

folder_path = 'your_folder_path_for_the_data'
dataframes = get_files(folder_path)



# Data Cleaning
# - For AccountCountry:
#     - Select only the following features:
#         - Country Code, Short Name, Table Name, Long Name, Currency Unit
# - For AccountData:
#     - Rename the columns and remove unwanted columns
#     - Convert the values into billions
# - For AccountSeries:
#     - Select only the following columns:
#         - 'Series Code, Topic, Indicator Name, Short Definition


def data_cleaning():
    acct_country = dataframes[1][1]
    acct_country = acct_country[['Code', 'Short Name', 'Table Name', 'Long Name', 'Currency Unit']]
    acct_country.rename(columns = {'Code':'country_code','Short Name':'short_name','Table Name':'table_name','Long Name':'long_name','Currency Unit':'currency_unit'}, inplace = True) 
    acct_country = acct_country.dropna()

    # clear the acc_data data
    acc_data = dataframes[0][1]
    # rename the columns to lower case
    acc_data.rename(columns = {'Country Name':'country_name','Country Code':'country_code','Series Name':'series_name','Series Code':'series_code'}, inplace = True)
    # clean the acc_data columns by removing the [YRxxxx] suffix from each column name and add 'year_' to the beginning of year columns
    acc_data.columns = [column.split(' [')[0] for column in acc_data.columns]
    acc_data.columns = ['year_' + column if column.isdigit() else column for column in acc_data.columns]
    #Remove the rows that contains unwanted character
    acc_data = acc_data[(acc_data != '..').all(axis=1)]
    acc_data = acc_data.dropna()
    
    
    #clean the acc_series data
    acc_series = dataframes[2][1][['Code', 'Topic', 'Indicator Name']]
    acc_series.rename(columns = {'Code':'series_code','Topic':'topic','Indicator Name':'indicator_name'}, inplace = True)
    acc_series = acc_series.dropna()
    
    return acc_data, acct_country, acc_series


acc_data, acct_country, acc_series = data_cleaning()


acc_data.columns


# Call the function to create database 'accounts'


cur,conn = create_database()


# Creating the tables in the database to store these data


acc_data_create = ("""CREATE TABLE IF NOT EXISTS acc_data (
                        country_name VARCHAR,
                        country_code VARCHAR,
                        series_name VARCHAR,
                        series_code VARCHAR,
                        year_1995 FLOAT,
                        year_1996 FLOAT,
                        year_1997 FLOAT,
                        year_1998 FLOAT,
                        year_1999 FLOAT,
                        year_2000 FLOAT,
                        year_2001 FLOAT,
                        year_2002 FLOAT,
                        year_2003 FLOAT,
                        year_2004 FLOAT,
                        year_2005 FLOAT,
                        year_2006 FLOAT,
                        year_2007 FLOAT,
                        year_2008 FLOAT,
                        year_2009 FLOAT,
                        year_2010 FLOAT,
                        year_2011 FLOAT,
                        year_2012 FLOAT,
                        year_2013 FLOAT,
                        year_2014 FLOAT,
                        year_2015 FLOAT,
                        year_2016 FLOAT,
                        year_2017 FLOAT,
                        year_2018 FLOAT
                    )""")


cur.execute(acc_data_create)
conn.commit()


# Create the acc_series and acc_country tables in the database


acc_country_create = ("""CREATE TABLE IF NOT EXISTS acc_country (
                            country_code VARCHAR PRIMARY KEY,
                            short_name VARCHAR,
                            table_name VARCHAR,
                            long_name VARCHAR,
                            currency_unit VARCHAR
                        )""")


cur.execute(acc_country_create)
conn.commit()


acc_series_create = ("""CREATE TABLE IF NOT EXISTS acc_series ( 
                            series_code VARCHAR PRIMARY KEY,
                            topic VARCHAR,
                            indicator_name VARCHAR
                        )""")


cur.execute(acc_series_create)
conn.commit()


# Write data to database


acc_country_insert = ("""INSERT INTO acc_country (
                      country_code, short_name, table_name, long_name, currency_unit) 
                      VALUES (%s, %s, %s, %s, %s)""")

for i, row in acct_country.iterrows():
    cur.execute(acc_country_insert, row)
    conn.commit()


acc_data_insert = ("""INSERT INTO acc_data (
                        country_name, country_code, series_name, series_code, year_1995, year_1996, year_1997, year_1998, year_1999, year_2000, year_2001, year_2002, year_2003, year_2004, year_2005, year_2006, year_2007, year_2008, year_2009, year_2010, year_2011, year_2012, year_2013, year_2014, year_2015, year_2016, year_2017, year_2018) 
                        VALUES (%s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s)""")
for i, row in acc_data.iterrows():
    cur.execute(acc_data_insert, row)
    conn.commit()


acc_series_insert = ("""INSERT INTO acc_series (
                        series_code, topic, indicator_name) 
                        VALUES (%s, %s, %s)""")
for i, row in acc_series.iterrows():
    cur.execute(acc_series_insert, row)
    conn.commit()





