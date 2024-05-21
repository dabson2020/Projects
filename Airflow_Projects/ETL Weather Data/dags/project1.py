## Import all the required libraries

import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
import json
import os


## Define the functions to transform the data

def kelvin_to_fahrenheit(temp_in_kelvin):
    temp_in_fahrenheit = (temp_in_kelvin - 273.15) * (9/5) + 32
    return temp_in_fahrenheit

def kelvin_to_celsius(temp_in_kelvin):
    temp_in_celsius = temp_in_kelvin - 273.15
    return temp_in_celsius

def transform_load_data(task_instance):
    data = task_instance.xcom_pull(task_ids="get_weather_data")
    city = data["name"]
    weather_description = data["weather"][0]['description']
    temp_fahrenheit = round(kelvin_to_fahrenheit(data["main"]["temp"]),2)
    feels_like_fahrenheit= round(kelvin_to_fahrenheit(data["main"]["feels_like"]),2)
    min_temp_fahrenheit = round(kelvin_to_fahrenheit(data["main"]["temp_min"]),2)
    max_temp_fahrenheit = round(kelvin_to_fahrenheit(data["main"]["temp_max"]),2)
    temp_celcius = round(kelvin_to_celsius(data["main"]["temp"]),2)
    feels_like_celsius= round(kelvin_to_celsius(data["main"]["feels_like"]),2)
    min_temp_celsius = round(kelvin_to_celsius(data["main"]["temp_min"]),2)
    max_temp_celsius = round(kelvin_to_celsius(data["main"]["temp_max"]),2)
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    time_of_record = datetime.fromtimestamp(data['dt'] + data['timezone'])
    sunrise_time = datetime.fromtimestamp(data['sys']['sunrise'] + data['timezone'])
    sunset_time = datetime.fromtimestamp(data['sys']['sunset'] + data['timezone'])

    transformed_data = {"City": city,
                    "Description": weather_description,
                    "Temperature (F)": temp_fahrenheit,
                    "Feels Like (F)": feels_like_fahrenheit,
                    "Minimun Temp (F)":min_temp_fahrenheit,
                    "Maximum Temp (F)": max_temp_fahrenheit,
                    "Temperature (C)": temp_celcius,
                    "Feels Like (C)": feels_like_celsius,
                    "Minimun Temp (C)":min_temp_celsius,
                    "Maximum Temp (C)": max_temp_celsius,
                    "Pressure": pressure,
                    "Humidty": humidity,
                    "Wind Speed": wind_speed,
                    "Time of Record": time_of_record,
                    "Sunrise (Local Time)":sunrise_time,
                    "Sunset (Local Time)": sunset_time                        
                    }
    transformed_data_list = [transformed_data]
    df_data = pd.DataFrame(transformed_data_list)

    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")
    dt_string = 'current_weather_data_calgary_' + dt_string
    df_data.to_csv(f"transformed_data/{dt_string}.csv", index=False)

    print("Data transformed and loaded")

## Define the function to concatenate the CSV files    
def concat_csv_files():
# Directory containing the CSV files
    directory = 'concat_data/'
    
# Get a list of all CSV files in the directory
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]
    
# Concatenate the CSV files into a single DataFrame if there are multiple CSV files and no duplicate files
    dfs = []
    for file in csv_files:
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path)
        dfs.append(df)
    concatenated_df = pd.concat(dfs, ignore_index=True)

        # Save the concatenated DataFrame to a new CSV file
    concatenated_df.to_csv('concat_data/concatenated.csv', index=False)    

## Define the DAG

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2020, 1, 1),
    'retries': 2,
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retry_delay': timedelta(minutes=2)
}

with DAG('project1', 
         default_args=default_args, 
         schedule_interval='@daily', 
         catchup=False) as dag:
        
        is_weather_data_available = HttpSensor(
            task_id='is_weather_data_available',
            method='GET',
            http_conn_id='weathermap_api',
            endpoint='data/2.5/weather?q=Calgary&appid=8b02968db63ac5ceb9945f775e31c533'   
        )

        get_weather_data = SimpleHttpOperator(
            task_id='get_weather_data',
            method='GET',
            http_conn_id='weathermap_api',
            endpoint='data/2.5/weather?q=Calgary&appid=8b02968db63ac5ceb9945f775e31c533',
            response_filter=lambda response: json.loads(response.text),
            log_response=True
        )
        
        transform_load_weather_data = PythonOperator(
            task_id='transform_load_weather_data',
            python_callable=transform_load_data
        )

            
        concat_data = PythonOperator(
            task_id='concat_data',
            python_callable=concat_csv_files
        )

is_weather_data_available >> get_weather_data >> transform_load_weather_data >> concat_data