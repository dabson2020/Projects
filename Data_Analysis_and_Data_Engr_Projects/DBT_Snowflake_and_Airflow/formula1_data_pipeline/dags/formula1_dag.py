from datetime import datetime
import os
from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import SnowflakeUserPasswordProfileMapping


profile_config = ProfileConfig(profile_name="default",
                               target_name="dev",
                               profile_mapping=SnowflakeUserPasswordProfileMapping(conn_id="snowflake_conn", 
                                                    profile_args={
                                                        "database": "car_race",
                                                        "schema": "car_schema"
                                                        },
                                                    ))


dbt_snowflake_dag = DbtDag(project_config=ProjectConfig("/usr/local/airflow/dags/car_pipeline"),
                    operator_args={"install_deps": True},
                    profile_config=profile_config,
                    execution_config=ExecutionConfig(dbt_executable_path=f"{os.environ['AIRFLOW_HOME']}/dbt_venv/bin/dbt"),
                    schedule_interval="@daily",
                    start_date=datetime(2023, 9, 10),
                    catchup=False,
                    dag_id="dbt_snowflake_dag")