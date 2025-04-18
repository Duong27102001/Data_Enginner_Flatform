import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import logging
from utils.constants import properties, URL
from utils.spark_utils import create_spark_session
from utils.s3_utils import read_staging_data_from_S3, load_processed_data_to_redshift


def load_data_into_dim_date():
    """
    Load data into the dim_date table in Redshift from S3.
    """
    try:
        logging.info("Starting ETL process for dim_date...")

        # Create a Spark session
        spark = create_spark_session()
        logging.info("Spark session created successfully.")

        # Đường dẫn dữ liệu trên S3
        path = "s3a://financial-data-dev-2025/processed_data/date"
        logging.info(f"Reading data from S3 path: {path}")

        # Đọc dữ liệu từ S3
        stg_date = read_staging_data_from_S3(spark, path)
        stg_count = stg_date.count()
        logging.info(f"Loaded {stg_count} records from S3.")

        # Chọn các cột cần thiết
        stg_date = stg_date.selectExpr(
            "day_id as day_key",
            "full_date",
            "day",
            "month",
            "year",
            "quarter",
            "week_of_year",
            "day_of_week",
            "day_name"
        )
        logging.info("Transformed staging data for dim_date.")

        # Ghi dữ liệu vào Redshift
        logging.info("Writing data to dim_date table in Redshift...")
        load_processed_data_to_redshift(
            stg_date,
            "dim_date",
            URL,
            properties
        )
        logging.info(f"Successfully loaded {stg_count} records into dim_date table.")

    except Exception as e:
        logging.error(f"An error occurred during the ETL process for dim_date: {e}")
    finally:
        logging.info("ETL process for dim_date completed.")

# Gọi hàm
load_data_into_dim_date()