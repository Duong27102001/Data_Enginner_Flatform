import os, sys, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.spark_utils import create_spark_session
from pyspark.sql.functions import col, year, month, dayofmonth, quarter, weekofyear, dayofweek, date_format

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Hiển thị log trên console
    ]
)

def process_date(date:str) -> None:
    """
    date = '2025-01-01'
    Tạo bảng dim_date từ ngày 2025-01-01 trong 3 năm và lưu vào S3.
    """
    logging.info("Starting dim_date processing...")
    try:
        spark = create_spark_session()

        # Tạo dải ngày từ 2025-01-01 trong 3 năm
        logging.info("Generating date range from 2025-01-01 for 3 years...")
        date_range = spark.range(0, 365 * 3).selectExpr(
            f"date_add('{date}', cast(id AS INT)) as full_date"
        )

        # Tạo các cột tương ứng với bảng dim_date
        logging.info("Transforming date range into dim_date format...")
        dim_date = date_range \
            .withColumn("day_id", date_format(col("full_date"), "yyyyMMdd").cast("int")) \
            .withColumn("day", dayofmonth(col("full_date"))) \
            .withColumn("month", month(col("full_date"))) \
            .withColumn("year", year(col("full_date"))) \
            .withColumn("quarter", quarter(col("full_date"))) \
            .withColumn("week_of_year", weekofyear(col("full_date"))) \
            .withColumn("day_of_week", dayofweek(col("full_date"))) \
            .withColumn("day_name", date_format(col("full_date"), "EEEE"))

        # Chọn các cột đúng thứ tự và tên như bảng
        dim_date = dim_date.select(
            "day_id",
            "full_date",
            "day",
            "month",
            "year",
            "quarter",
            "week_of_year",
            "day_of_week",
            "day_name"
        )

        # Log số lượng bản ghi trong bảng dim_date
        record_count = dim_date.count()
        logging.info(f"Generated dim_date with {record_count} records.")

        # Ghi ra S3 hoặc local
        s3_path = "s3a://financial-data-dev-2025/processed_data/date"
        logging.info(f"Saving dim_date to {s3_path}...")
        dim_date.write.mode("overwrite").parquet(s3_path)
        logging.info("dim_date created and saved successfully.")

    except Exception as e:
        logging.error(f"Error while creating dim_date: {e}")

# Chạy hàm
process_date()