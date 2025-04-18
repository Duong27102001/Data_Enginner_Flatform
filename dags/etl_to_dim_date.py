from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.transformer.transformer_date import process_date
from etl.load.load_date_into_dw import  load_data_into_dim_date

# Define default arguments for the DAG
default_args = {
    'owner': 'Le Huynh Thanh Duong',
    'depends_on_past': False,
    'email': ['thanhduonglehuynh2001@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Define the DAG
with DAG(
    dag_id = 'etl_to_dim_date',
    default_args=default_args,
    description='ETL pipeline to process and load data into dim_date table',
    schedule_interval= None,
    start_date=datetime(2025, 4, 18),
    catchup=False,
    tags=['etl', 'dim_date'],
) as dag:

    # Define the ETL task
    process_date_task = PythonOperator(
        task_id='process date data',
        # Create from current date to 3 years later
        python_callable=process_date,
        op_kwargs={'date': '2025-01-01'}
    )
    
    load_data_to_dw_task = PythonOperator(
        task_id = 'Load processed data into dim_date',
        python_callable= load_data_into_dim_date
    )
    # Set task dependencies
    process_date_task >> load_data_to_dw_task