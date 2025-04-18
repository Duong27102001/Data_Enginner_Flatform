import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import logging
from pyspark.sql.functions import col, broadcast
from utils.constants import properties, URL

from datetime import datetime, timedelta

from utils.spark_utils import create_spark_session
from utils.s3_utils import read_staging_data_from_S3, read_dim_table_from_redshift, load_processed_data_to_redshift

def load_stock_price_into_dw():
    """
    Load processed stock price data from S3 into Redshift fact table (fact_stock_price).
    """
    spark = create_spark_session()

    # Định nghĩa ngày hôm qua
    current_date = datetime.now() - timedelta(days=1)

    try:
        # Định dạng ngày
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%d")

        logging.info(f"Processing stock price data for date: {year}-{month}-{day}")

        # Đọc dữ liệu từ S3
        path = f"s3a://financial-data-dev-2025/processed_data/stock_prices/year={year}/month={month}/day={day}"
        stg_stock_price = read_staging_data_from_S3(spark, path)

        # Log số lượng bản ghi trong staging
        stg_count = stg_stock_price.count()
        logging.info(f"Loaded {stg_count} records from {path}")

        # Lấy danh sách ticker và tạo truy vấn
        company_ticker_str = ",".join(f"'{row['ticket']}'" for row in stg_stock_price.select("ticket").distinct().collect())
        dim_query = f"(SELECT company_key, company_ticker FROM dim_companies WHERE company_ticker IN ({company_ticker_str})) AS dim_companies_sub"

        # Đọc bảng dim_company
        logging.info("Querying dim_companies table from Redshift...")
        dim_company = read_dim_table_from_redshift(spark, dim_query, URL, properties)

        # Log số lượng bản ghi trong dim_companies
        dim_company_count = dim_company.count()
        logging.info(f"Loaded {dim_company_count} records from dim_companies table for comparison")

        # Join dữ liệu
        logging.info("Joining staging data with dim_companies...")
        joined_company = stg_stock_price.join(
            broadcast(dim_company),
            stg_stock_price.ticket == dim_company.company_ticker,
            "inner"
        )

        # Chọn và xử lý dữ liệu
        new_records = joined_company.selectExpr(
            "company_key",
            "stock_time as day_key",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "coalesce(volume, 0) as volume",
            "coalesce(vwap, 0) as vwap",
            "coalesce(num_transaction, 0) as num_transaction",
            "is_otc"
        )

        # Log số lượng bản ghi mới
        new_records_count = new_records.count()
        logging.info(f"Prepared {new_records_count} records to insert into fact_stock_price")

        # Ghi dữ liệu vào Redshift
        logging.info("Writing data to fact_stock_price table in Redshift...")
        load_processed_data_to_redshift(new_records, URL, properties, "fact_stock_price")   
        logging.info(f"Inserted {new_records_count} records into fact_stock_price table")

    except Exception as e:
        logging.error(f"Error processing stock price data for {current_date.strftime('%Y-%m-%d')}: {e}")

    spark.stop()
    logging.info("Finished loading stock price data into fact_stock_price table.")

# Gọi hàm
load_stock_price_into_dw()