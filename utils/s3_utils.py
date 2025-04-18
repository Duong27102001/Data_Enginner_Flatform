import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import boto3
import os
import sys
import logging
from utils.constants import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, AWS_REGION
def connect_to_s3() -> boto3.client:
    try:
        s3 = boto3.client(
        's3',
        aws_access_key_id = AWS_ACCESS_KEY_ID,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
        region_name = AWS_REGION)
    except Exception as e:
        print(e)
    return s3

def create_bucket_if_not_exists(s3: boto3.client, bucket_name: str) -> None:
    try:
        existing_buckets = [bucket['Name'] for bucket in s3.list_buckets().get('Buckets', [])]
        if bucket_name in existing_buckets:
            print(f"Bucket {bucket_name} already exists.")
            return
        else:
            s3.create_bucket(Bucket = bucket_name, CreateBucketConfiguration={"LocationConstraint": AWS_REGION} )
            print(f"Bucket {bucket_name} has been successfully created!")
    except Exception as e:
        print(e)
    
def read_staging_data_from_S3(spark, path: str):
    """ Đọc dữ liệu từ S3"""
    try:
        logging.info(f"Reading data from {path}")
        return spark.read.parquet(path).cache()
    except Exception as e:
        logging.error(f"Error reading data from {path}: {e}")
        raise

def read_dim_table_from_redshift(spark, query: str, url ,properties: dict):
    """ Đọc dữ liệu từ Redshift"""
    try:
        logging.info(f"Reading data from Redshift with query: {query}")
        return spark.read.format("jdbc") \
            .option("url", url) \
            .option("dbtable", query) \
            .option("user", properties["user"]) \
            .option("password", properties["password"]) \
            .option("driver", properties["driver"]) \
            .load()
    except Exception as e:
        logging.error(f"Error reading data from Redshift: {e}")
        raise

def load_processed_data_to_redshift(dataframe, URL_PATH, properties, table_name: str):
    """ Ghi dữ liệu vào Redshift"""
    try:
        logging.info(f"Writing data to Redshift table {table_name}")
        dataframe.write.jdbc(
            url= URL_PATH,
            table=table_name,
            mode="append",
            properties=properties
        )
    except Exception as e:
        logging.error(f"Error writing data to Redshift: {e}")
        raise