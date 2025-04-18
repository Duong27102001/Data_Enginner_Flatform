from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.transformer.transformer_companies import process_companies
from etl.load.load_companies_into_dw import load_processed_data_into_dw
from etl.extract.crawl_companies_by_exchange import crawl_companies_by_exchange
from etl.extract.crawl_markets import crawl_markets
from etl.load.load_raw_data_into_s3 import load_raw_data_to_s3
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
    dag_id = 'etl_to_dim_companies',
    default_args=default_args,
    description='ETL pipeline to process and load data into dim_companies table',
    schedule_interval= '@monthly',
    start_date=datetime(2025, 4, 18),
    catchup=False,
    tags=['etl', 'dim_companies'],
) as dag:

    # Define the ETL task
    extract_companies_task = PythonOperator(
        task_id='Extract companies data',
        # Extract companies data from exchange: NYSE, NASDAQ
        python_callable=crawl_companies_by_exchange
    )
    extract_markets_task = PythonOperator(
        task_id='Extract markets data',
        python_callable=crawl_markets
    )
    
    load_companies_data_into_s3_task = PythonOperator(
        task_id='Load companies data into S3',
        python_callable=load_raw_data_to_s3,
        op_kwargs={'path': 'raw_data/companies', 'bucket_name': 'financial-data-dev-2025'}
    )
    load_marets_data_into_s3_task = PythonOperator(
        task_id='Load markets data into S3',
        python_callable=load_raw_data_to_s3,
        op_kwargs={'path': 'raw_data/markets', 'bucket_name': 'financial-data-dev-2025'}
    )
    
    process_companies_task = PythonOperator(
        task_id='Process companies data',
        python_callable=process_companies
    )
    load_processed_comapanies_into_dw_task = PythonOperator(
        task_id='Load processed companies data into dim_companies',
        python_callable=load_processed_data_into_dw
    )
    
# Set task dependencies
[extract_companies_task >> load_companies_data_into_s3_task,
 extract_markets_task >> load_marets_data_into_s3_task] >> process_companies_task >> load_processed_comapanies_into_dw_task