#Dags for extract, transform and load

#For extract

from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, date
import pandas as pd

default_args = {
    'owner': 'adeola',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}

with DAG(
    dag_id = 'complete_etl_task',
    default_args=default_args,
    description='extract, transform and load top domain names!',
    schedule_interval=None) as dag:

    extract_task = BashOperator(
    task_id='extract_task',
    bash_command='wget -c https://datahub.io/core/top-level-domain-names/r/top-level-domain-names.csv.csv -O /home/adeola/airflow/twitter_dag/extract_data.csv',
    dag=dag)

    #For transform

    def transform():
        df = pd.read_csv('/home/adeola/airflow/twitter_dag/extract_data.csv')
        generic_df = df[df['Type']=='generic']
        today = date.today()
        generic_df['Date']=today.strftime("%Y-%m-%d")
        generic_df.to_csv('/home/adeola/airflow/twitter_dag/transform_data.csv', index = False)

    transform_task = PythonOperator(
    task_id='transform_task',
    python_callable=transform,
    dag=dag
    )

    #For load
    load_task = BashOperator(
    task_id='load_task',
    bash_command='echo -e ".separator ","\n.import --skip 1 /home/adeola/airflow/twitter_dag/transform_data.csv top_domain" | sqlite3 /home/adeola/airflow/twitter_dag/load_domain.db',
    dag=dag)    

    extract_task>>transform_task>>load_task
    
