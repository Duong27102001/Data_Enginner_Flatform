import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import logging
from pyspark.sql.functions import col
from utils.constants import properties, URL
from datetime import datetime, timedelta
from utils.spark_utils import create_spark_session
from utils.s3_utils import read_staging_data_from_S3, read_dim_table_from_redshift, load_processed_data_to_redshift



def load_news_into_dw():
    """
    Load processed news data from S3 into Redshift dimension table (dim_news).
    """
    spark = create_spark_session()

    # Định nghĩa ngày hôm qua
    current_date = datetime.now() - timedelta(days=1)

    try:
        # Định dạng ngày
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%d")

        logging.info(f"Processing news data for date: {year}-{month}-{day}")

        # Đọc dữ liệu từ S3
        path = f"s3a://financial-data-dev-2025/processed_data/news/year={year}/month={month}/day={day}"
        stg_new = read_staging_data_from_S3(spark, path)
        stg_news = stg_new.selectExpr(
                "new_id as news_id",
                "new_title as news_title",
                "new_url as news_url",
                "new_time_published as news_time_published",
                "new_authors as news_authors",
                "new_summary as news_summary",
                "new_source as news_source",
                "new_overall_sentiment_score as news_overall_sentiment_score",
                "new_overall_sentiment_label as news_overall_sentiment_label"
            )

        # Log số lượng bản ghi trong staging
        stg_count = stg_news.count()
        logging.info(f"Loaded {stg_count} records from {path}")

        # Lấy danh sách khóa chính từ staging
        news_keys = [row['news_id'] for row in stg_news.select("news_id").distinct().collect()]
        news_keys_str = ",".join(f"'{cid}'" for cid in news_keys)

        # Truy vấn dữ liệu hiện tại từ Redshift
        dim_query = f'''(SELECT news_id as dim_news_id FROM dim_news 
            WHERE news_id IN ({news_keys_str})) AS dim_news_sub'''
        logging.info("Querying existing dimension data from Redshift...")
        dim_news = read_dim_table_from_redshift(spark, dim_query, URL,  properties)
        
        # Log số lượng bản ghi trong dimension
        dim_count = dim_news.count()
        logging.info(f"Loaded {dim_count} records from dim_news table for comparison")

        # Join staging và dimension
        logging.info("Joining staging data with dimension data...")
        joined = stg_news.join(
            dim_news,
            stg_news.news_id == dim_news.dim_news_id,
            "left"
        )

        # Xác định bản ghi mới
        new_records = joined.filter(col("dim_news_id").isNull()).select(stg_news.columns)
        new_count = new_records.count()
        
        logging.info(f"Identified {new_count} new records to insert into dim_news")

        # Ghi các bản ghi mới vào Redshift
        load_processed_data_to_redshift(new_records, URL, properties, "dim_news")
        logging.info(f"Inserted {new_count} new records into dim_news table")

    except Exception as e:
        logging.error(f"Error processing news data for {current_date.strftime('%Y-%m-%d')}: {e}")

    spark.stop()
    logging.info("Finished loading news data into dim_news table.")

# Gọi hàm
load_news_into_dw()