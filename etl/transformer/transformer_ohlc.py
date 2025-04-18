import os, sys
import logging
from datetime import datetime, timedelta
from pyspark.sql.functions import col, date_format, date_sub, from_unixtime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.spark_utils import create_spark_session

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Hiển thị log trên console
    ]
)

def process_ohlc():
    """
    Xử lý dữ liệu OHLC của ngày hôm qua.
    """
    logging.info("Starting OHLC data processing...")
    spark = create_spark_session()

    # Định nghĩa ngày hôm qua
    current_date = datetime.now() - timedelta(days=1)

    try:
        # Định dạng ngày
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%d")

        logging.info(f"Processing data for date: {year}-{month}-{day}")

        # Đọc dữ liệu từ S3
        input_path = f"s3a://financial-data-dev-2025/raw_data/ohlc/year={year}/month={month}/crawl_ohlc_{year}_{month}_{day}"
        df = spark.read.parquet(input_path).cache()

        # Log số lượng bản ghi khi load dữ liệu
        input_count = df.count()
        logging.info(f"Loaded {input_count} records from {input_path}")

        # Xử lý dữ liệu
        stock_price = df.selectExpr(
            "T as ticket",
            "t as stock_time",
            "o as open_price",
            "h as high_price",
            "l as low_price",
            "c as close_price",
            "v as volume",
            "vw as vwap",
            "n as num_transaction",
            "otc as is_otc"
        )

        stock_price = stock_price.withColumn(
            "stock_time",
            date_format(date_sub(from_unixtime(col("stock_time") / 1000), 1), "yyyyMMdd")
        )

        # Log số lượng bản ghi sau khi xử lý
        processed_count = stock_price.count()
        logging.info(f"Processed {processed_count} records for date: {year}-{month}-{day}")

        # Ghi dữ liệu đã xử lý vào S3
        output_path = f"s3a://financial-data-dev-2025/processed_data/stock_prices/year={year}/month={month}/day={day}"
        stock_price.write.mode("overwrite").parquet(output_path)

        logging.info(f"Data for {year}-{month}-{day} processed and saved to {output_path}")

    except Exception as e:
        logging.error(f"Error processing data for {current_date.strftime('%Y-%m-%d')}: {e}")

    logging.info("Finished OHLC data processing.")

# Chạy hàm
process_ohlc()