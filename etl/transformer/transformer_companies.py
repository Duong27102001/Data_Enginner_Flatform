import os, sys, logging
from pyspark.sql.functions import when, col, array_contains, split
from datetime import datetime
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

def process_companies():
    """
    Xử lý dữ liệu công ty và thị trường, chuẩn hóa và lưu kết quả vào S3.
    """
    logging.info("Starting companies data processing...")
    spark = create_spark_session()

    try:
        current_year = datetime.now().year
        current_month = datetime.now().strftime("%m")  # giữ định dạng MM

        # Đọc dữ liệu công ty
        input_companies_path = f"s3a://financial-data-dev-2025/raw_data/companies/year={current_year}/month={current_month}/*/*"
        logging.info(f"Reading companies data from {input_companies_path}")
        df = spark.read.parquet(input_companies_path).cache()

        # Log số lượng bản ghi trong dữ liệu công ty
        companies_count = df.count()
        logging.info(f"Loaded {companies_count} records from companies data")

        companies = df.selectExpr(
            "id as company_id",
            "name as company_name",
            "ticker as company_ticker",
            "isDelisted as company_is_delisted",
            "category as company_category",
            "currency as company_currency",
            "location as company_location",
            "exchange as company_exchange_name",
            "industry as company_industry_name",
            "sicIndustry as company_sic_industry",
            "sicSector as company_sic_sector"
        )

        # Chuẩn hoá tên sàn giao dịch
        companies = companies.withColumn(
            "company_exchange_name",
            when(col("company_exchange_name").startswith("NYSE"), "NYSE")
            .when(col("company_exchange_name").startswith("NASDAQ"), "NASDAQ")
            .otherwise("OTHER")
        )

        # Đọc dữ liệu thị trường
        input_markets_path = f"s3a://financial-data-dev-2025/raw_data/markets/year={current_year}/month={current_month}/*/*"
        logging.info(f"Reading markets data from {input_markets_path}")
        df_market = spark.read.parquet(input_markets_path).cache()

        # Log số lượng bản ghi trong dữ liệu thị trường
        markets_count = df_market.count()
        logging.info(f"Loaded {markets_count} records from markets data")

        df_market = df_market.withColumn("primary_exchanges", split("primary_exchanges", ",\\s*"))

        markets = df_market.selectExpr(
            "region",
            "primary_exchanges as primary_exchange_array"
        )

        # Join dữ liệu công ty và thị trường
        logging.info("Joining companies and markets data...")
        joined_df = companies.join(
            markets,
            array_contains(col("primary_exchange_array"), col("company_exchange_name")),
            "inner"
        )

        # Log số lượng bản ghi sau khi join
        joined_count = joined_df.count()
        logging.info(f"Joined data contains {joined_count} records")

        # Lấy kết quả cuối
        result = joined_df.selectExpr(
            "company_id",
            "company_name",
            "company_ticker",
            "company_is_delisted",
            "company_category",
            "company_currency",
            "company_location",
            "company_exchange_name",
            "region as company_region_name",
            "company_industry_name",
            "company_sic_industry",
            "company_sic_sector"
        )

        # Ghi dữ liệu ra S3
        output_path = f"s3a://financial-data-dev-2025/processed_data/companies/year={current_year}/month={current_month}"
        logging.info(f"Writing processed data to {output_path}")
        result.write.mode("overwrite").parquet(output_path)
        logging.info("Companies data processing completed successfully.")

    except Exception as e:
        logging.error(f"Error processing companies data: {e}")

# Chạy hàm
process_companies()