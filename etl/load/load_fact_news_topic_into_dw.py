import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import logging
from datetime import datetime, timedelta
from utils.constants import URL, properties
from utils.spark_utils import create_spark_session
from utils.s3_utils import read_staging_data_from_S3, read_dim_table_from_redshift, load_processed_data_to_redshift

def load_news_topic_into_dw():
    """
    Load processed news topic data from S3 into Redshift fact table (fact_news_topic).
    """
    spark = create_spark_session()
   
    # Định nghĩa ngày hôm qua
    current_date = datetime.now() - timedelta(days=1)

    try:
        # Định dạng ngày
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%d")

        logging.info(f"Processing news topic data for date: {year}-{month}-{day}")

        # Đọc dữ liệu từ S3
        path = f"s3a://financial-data-dev-2025/processed_data/news_topic/year={year}/month={month}/day={day}"
        stg_news_topic = read_staging_data_from_S3(spark, path)

        # Log số lượng bản ghi trong staging
        stg_count = stg_news_topic.count()
        logging.info(f"Loaded {stg_count} records from {path}")

        # Lấy danh sách khóa chính từ staging
        news_keys = [row['new_id'] for row in stg_news_topic.select("new_id").distinct().collect()]
        news_keys_str = ",".join(f"'{cid}'" for cid in news_keys)

        # Truy vấn dữ liệu hiện tại từ Redshift (dim_news)
        dim_query = f'''(SELECT news_key, news_id as dim_news_id FROM dim_news 
            WHERE news_id IN ({news_keys_str})) AS dim_news_sub'''
        logging.info("Querying dim_news table from Redshift...")
        dim_news = read_dim_table_from_redshift(spark, dim_query, URL, properties)

        # Log số lượng bản ghi trong dim_news
        dim_news_count = dim_news.count()
        logging.info(f"Loaded {dim_news_count} records from dim_news table for comparison")

        # Join staging và dim_news
        logging.info("Joining staging data with dim_news...")
        joined = stg_news_topic.join(
            dim_news,
            stg_news_topic.new_id == dim_news.dim_news_id,
            "left"
        )

        # Chọn các cột cần thiết cho fact table
        new_records = joined.selectExpr(
            "news_key",
            "date_id as day_key",
            "new_topic_relevance_score as topic_relevance_score",
            "topic_name"
        )

        # Log số lượng bản ghi mới
        new_records_count = new_records.count()
        logging.info(f"Prepared {new_records_count} records to insert into fact_news_topic")

        # Ghi dữ liệu vào Redshift
        logging.info("Writing data to fact_news_topic table in Redshift...")
        load_processed_data_to_redshift(new_records, URL, properties, "fact_news_topic")
        logging.info(f"Inserted {new_records_count} records into fact_news_topic table")

    except Exception as e:
        logging.error(f"Error processing news topic data for {current_date.strftime('%Y-%m-%d')}: {e}")

    spark.stop()
    logging.info("Finished loading news topic data into fact_news_topic table.")

# Gọi hàm
load_news_topic_into_dw()