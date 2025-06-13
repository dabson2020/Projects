## Import all the required libraries



import pandas as pd
import pymysql
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import HttpOperator
import json
import os
import base64
import requests



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
                    "Temperature_F": temp_fahrenheit,
                    "Feels_Like_F": feels_like_fahrenheit,
                    "Minimun_Temp_F":min_temp_fahrenheit,
                    "Maximum_Temp_F": max_temp_fahrenheit,
                    "Temperature_C": temp_celcius,
                    "Feels_Like_C": feels_like_celsius,
                    "Minimum_Temp_C":min_temp_celsius,
                    "Maximum_Temp_C": max_temp_celsius,
                    "Pressure": pressure,
                    "Humidty": humidity,
                    "Wind_Speed": wind_speed,
                    "Time_of_Record": time_of_record,
                    "Sunrise_Local_Time":sunrise_time,
                    "Sunset_Local_Time": sunset_time                        
                    }
    transformed_data_list = [transformed_data]
    df_data = pd.DataFrame(transformed_data_list)

    

    df_data = df_data[['City', 'Description', 'Temperature_F', 'Feels_Like_F', 'Minimun_Temp_F',
                       'Maximum_Temp_F', 'Temperature_C', 'Feels_Like_C', 'Minimum_Temp_C',
                       'Maximum_Temp_C', 'Pressure', 'Humidty', 'Wind_Speed', 'Time_of_Record',
                       'Sunrise_Local_Time', 'Sunset_Local_Time']]
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")
    dt_string = 'current_weather_data_calgary_' + dt_string
    df_data.to_csv(f"~/data/transformed_weather_data/{dt_string}.csv", index=False)

    print("Data transformed and loaded")

## Define the function to concatenate the CSV files    
def concat_csv_files():
# Directory containing the CSV files
    directory = '/home/adeola2020/data/transformed_weather_data'
    
# Get a list of all CSV files in the directory
    csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]
    
# Concatenate the CSV files into a single DataFrame if there are multiple CSV files and no duplicate files
    dfs = []
    for file in csv_files:
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path)
        dfs.append(df)

    concatenated_df = pd.concat(dfs, ignore_index=True)

    #Convert Time_of_Record to dateteime and data by Time_of_Record in descending order
    concatenated_df['Time_of_Record'] = pd.to_datetime(concatenated_df['Time_of_Record'])
    concatenated_df.sort_values(by='Time_of_Record', ascending=False, inplace=True)
    concatenated_df.reset_index(drop=True, inplace=True)
    return concatenated_df


def save_to_csv(dataframe, output_path='/home/adeola2020/data/concat_weather_data/concatenated.csv'):
    # Save the DataFrame to CSV
    dataframe.to_csv(output_path, index=False)
    print(f"CSV saved to {output_path}")

def load_data():
    concatenated_df = concat_csv_files()
    save_to_csv(concatenated_df)
    print("Data concatenated and saved to CSV")
  



def load_mysql(table):
    # Connect to MySQL
    conn = pymysql.connect(
        host="localhost",
        database="weather_data",
        user="root",
        password="Tokunbo@12",
        port=3306
    )
    cursor = conn.cursor()

    table_name = 'all_data'

    # Load CSV data
    data = pd.read_csv('~/data/concat_weather_data/concatenated.csv')

    # Get existing (City, Time_of_Record) from the database
    cursor.execute(f"SELECT City, Time_of_Record FROM {table_name}")
    existing_records = set(cursor.fetchall())

    # Filter only new rows (not in existing_records)
    new_rows = []
    for _, row in data.iterrows():
        key = (row['City'], row['Time_of_Record'])
        if key not in existing_records:
            new_rows.append(tuple(row))

    if new_rows:
        insert_query = """
        INSERT INTO all_data (City, Description, Temperature_F, Feels_Like_F, Minimun_Temp_F, 
        Maximum_Temp_F, Temperature_C, Feels_Like_C, Minimum_Temp_C, Maximum_Temp_C, Pressure, Humidty, 
        Wind_Speed, Time_of_Record, Sunrise_Local_Time, Sunset_Local_Time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, new_rows)
        conn.commit()
        print(f"{len(new_rows)} new rows inserted into {table_name}")
    else:
        print("No new data to insert.")

    cursor.close()
    conn.close()



import base64
import requests
from airflow.models import Variable

def upload_csv_to_github(
    repo_owner,
    repo_name,
    file_path,
    commit_message,
    github_token,
    path_in_repo="Data_Analysis_and_Data_Engr_Projects/Airflow_Projects/ETL_Weather_Data/concat_data/weather.csv",
    branch="master"
):
    """
    Upload or update a file (CSV) to a GitHub repository via API.

    Parameters:
        repo_owner (str): GitHub username or organization name.
        repo_name (str): GitHub repository name.
        file_path (str): Local path to the CSV file.
        commit_message (str): Commit message for GitHub.
        github_token (str): Personal access token for GitHub.
        path_in_repo (str): Target path in the repository.
        branch (str): Branch to commit to. Default is 'main'.
    """

    # GitHub API URL for file content
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path_in_repo}"

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }

    # Read and encode file content
    try:
        with open(file_path, "rb") as file:
            content = file.read()
        encoded_content = base64.b64encode(content).decode("utf-8")
    except Exception as e:
        raise Exception(f"❌ Failed to read file: {file_path}. Error: {e}")

    # Step 1: Check if file already exists (get SHA)
    sha = None
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            json_data = response.json()
            if isinstance(json_data, dict):
                sha = json_data.get("sha")
            elif isinstance(json_data, list):
                raise Exception(f"❌ Path points to a folder, not a file: {url}")
            else:
                raise Exception(f"❌ Unexpected GitHub response format:\n{json_data}")
        except requests.exceptions.JSONDecodeError as e:
            raise Exception(f"❌ Invalid JSON response from GitHub:\n{response.text}")
    elif response.status_code == 404:
        sha = None  # File does not exist, so it will be created
    else:
        raise Exception(f"❌ Failed to access GitHub API:\nStatus Code: {response.status_code}\nResponse: {response.text}")

    # Step 2: Upload or update the file
    payload = {
        "message": commit_message,
        "content": encoded_content,
        "branch": branch,
    }

    if sha:
        payload["sha"] = sha

    upload_response = requests.put(url, headers=headers, json=payload)

    if upload_response.status_code in [200, 201]:
        print("✅ File uploaded successfully.")
    else:
        raise Exception(f"❌ Failed to upload file:\nStatus Code: {upload_response.status_code}\nResponse: {upload_response.text}")

def task_upload_github():
    upload_csv_to_github(
        repo_owner="dabson2020",
        repo_name="Projects",
        file_path="/home/adeola2020/data/concat_weather_data/concatenated.csv",
        commit_message="Add today's weather data",
        github_token=Variable.get("github_token"),
        path_in_repo="Data_Analysis_and_Data_Engr_Projects/Airflow_Projects/ETL_Weather_Data/concat_data/weather.csv"
)
    


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

with DAG('Calgary_weather_data', 
         default_args=default_args, 
         schedule_interval='@dailyhourly', 
         catchup=False) as dag:
        
        is_weather_data_available = HttpSensor(
            task_id='is_weather_data_available',
            method='GET',
            http_conn_id='weathermap_api',
            endpoint='data/2.5/weather?q=Calgary&appid=8b02968db63ac5ceb9945f775e31c533'   
        )

        get_weather_data = HttpOperator(
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

        load_data = PythonOperator(
            task_id='load_data',
            python_callable=load_data
        )

        load_data_to_mysql = PythonOperator(
            task_id='load_data_to_mysql',
            python_callable=load_mysql,
            op_kwargs={'table': 'all_data'}
        )
        upload_data_to_github= PythonOperator(
        task_id='upload_csv_to_github',
        python_callable=task_upload_github
        )

    
# Define the task dependencies

is_weather_data_available >> get_weather_data >> transform_load_weather_data >> concat_data >> load_data
concat_data >> load_data_to_mysql 
concat_data >> upload_data_to_github