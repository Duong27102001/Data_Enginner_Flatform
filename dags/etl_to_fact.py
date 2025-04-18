from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os, sys
from airflow.sensors.external_task import ExternalTaskSensor
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.transformer.transformer_ohlc import process_ohlc
from etl.extract.crawl_ohlc import crawl_ohlcs
from etl.load.load_fact_news_topic_into_dw import load_news_topic_into_dw
from etl.load.load_fact_company_sentiment import load_company_sentiment_into_dw
from etl.load.load_fact_stock_price import load_stock_price_into_dw
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
    dag_id='etl_to_fact',
    default_args=default_args,
    description='ETL pipeline to process and load data into fact_company_sentiment, fact_news_topic, fact_stock_price table',
    schedule_interval='@daily',
    start_date=datetime(2025, 4, 18),
    catchup=False,
    tags=['etl', 'fact_company_sentiment', 'fact_news_topic', 'fact_stock_price'],
) as dag:
    
    # Wait for the completion of DAG 'etl_to_dim_news' (chạy hàng ngày)
    wait_for_etl_to_dim_news = ExternalTaskSensor(
        task_id='wait_for_etl_to_dim_news', 
        external_dag_id='etl_to_dim_news',  # The DAG to wait for
        external_task_id=None,  # The task to wait for
        mode="poke",
        poke_interval=60,  # Check every 60 seconds
        timeout=None
    )
    
    # Define the ETL task
    extract_ohlcs_task = PythonOperator(
        task_id='Extract companies data',
        python_callable=crawl_ohlcs
    )
  
    process_ohlcs_task = PythonOperator(
        task_id='Process ohlc data',
        python_callable=process_ohlc
    )
    
    load_ohlc_data_into_s3_task = PythonOperator(
        task_id='Load ohlc data into S3',
        python_callable=load_raw_data_to_s3,
        op_kwargs={'path': 'raw_data/ohlc', 'bucket_name': 'financial-data-dev-2025'}
    )
    
    load_fact_stock_price_into_dw_task = PythonOperator(
        task_id='Load processed data into fact_stock_price',
        python_callable=load_stock_price_into_dw
    )
    
    load_fact_company_sentiment_into_dw_task = PythonOperator(
        task_id='Load processed data into fact_company_sentiment',
        python_callable=load_company_sentiment_into_dw
    )
    
    load_fact_news_topic_into_dw_task = PythonOperator(
        task_id='Load processed data into fact_news_topic',
        python_callable=load_news_topic_into_dw
    )
    
    # Set task dependencies
    extract_ohlcs_task >> load_ohlc_data_into_s3_task >> wait_for_etl_to_dim_news >> process_ohlcs_task
    process_ohlcs_task >> [
        load_fact_stock_price_into_dw_task,
        load_fact_company_sentiment_into_dw_task,
        load_fact_news_topic_into_dw_task
    ]