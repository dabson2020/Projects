
# This project loads data with Kaggle API, cleans the data, and load the data into SQL Server for further analysis


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import kaggle
import zipfile


# We are loading the data from kaggle using kaggle api


def load_data():
    # Load data
    !kaggle datasets download ankitbansal06/retail-orders
    with zipfile.ZipFile('retail-orders.zip', 'r') as zip_ref:
        zip_ref.extractall('data')
        zip_ref.close()
        df = pd.read_csv('data/orders.csv',encoding='latin1')
        return df



# Extracting the zip file of the datsets downloaded from kaggle


df = load_data()



### Data Cleaning
# - Replace missing values  
#   - Replace NaN, 'Not Available' and 'unknown' in Ship_mode column
# - Convert column names to lowercase and replace whitespace with underscore
# - Compute the sales price and discount and profit
# - Drop the cost_price,list_price and discount_percent
# - Convert order_date into datetime data type

def data_cleaning(df):
    # replace missing values
    df['Ship Mode'] = df['Ship Mode'].fillna('Standard Class')
    df['Ship Mode'] = df['Ship Mode'].replace(['Not Available','unknown'],'Standard Class')

    # convert column names to lowercase, replace space with underscore
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # compute sales_price, profit and discount
    df['discount'] = (df['list_price'] * df['discount_percent'] / 100)
    df['sales_price'] = df['list_price'] - df['discount']
    df['profit'] = df['sales_price'] - df['cost_price']

    # drop cost_price, list_price and discount_percent columns
    df = df.drop(columns=['cost_price', 'list_price', 'discount_percent'])

    # convert order_date column into datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    
   
    return df


data=data_cleaning(df)

# Load data into MS SQL Server using msqlalchemy


import sqlalchemy as sqal
engine = sqal.create_engine('mssql://ADEOLA\SQLEXPRESS/retail?driver=ODBC+DRIVER+17+for+SQL+Server')
conn=engine.connect()
# The data will be loaded into the tables you already created in MMSQL

data.to_sql('orders',conn,if_exists='append',index=False)

# If you want the table to be created in the database, you can use the following code
#data.to_sql('orders',conn,if_exists='replace',index=False)





