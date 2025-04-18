from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.transformer.transformer_news import process_news
from etl.load.load_news_into_dw import load_news_into_dw
from etl.extract.crawl_news import crawl_news_full_days
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
    schedule_interval= '@daily',
    start_date=datetime(2025, 4, 18),
    catchup=False,
    tags=['etl', 'dim_news'],
) as dag:

    # Define the ETL task
    extract_news_task = PythonOperator(
        task_id='Extract news data',
        # Extract companies data from exchange: NYSE, NASDAQ
        python_callable=crawl_news_full_days
    )
    load_news_data_into_s3_task = PythonOperator(
        task_id='Load news data into S3',
        python_callable=load_raw_data_to_s3,
        op_kwargs={'path': 'raw_data/news', 'bucket_name': 'financial-data-dev-2025'}
    )
    
    process_news_task = PythonOperator(
        task_id='Process news data',
        python_callable=process_news
    )
    load_processed_news_into_dw_task = PythonOperator(
        task_id='Load processed news data into dim_news',
        python_callable=load_news_into_dw
    )
    
    # Set task dependencies
    extract_news_task >> load_news_data_into_s3_task >> process_news_task >> load_processed_news_into_dw_task