import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import logging
from datetime import datetime, timedelta
from utils.constants import URL, properties
from utils.spark_utils import create_spark_session
from utils.s3_utils import read_staging_data_from_S3, read_dim_table_from_redshift, load_processed_data_to_redshift



def load_company_sentiment_into_dw():
    """
    Load processed company sentiment data from S3 into Redshift fact table (fact_company_sentiment).
    """
    spark = create_spark_session()
    
    # Định nghĩa ngày hôm qua
    current_date = datetime.now() - timedelta(days=1)

    try:
        # Định dạng ngày
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")
        day = current_date.strftime("%d")

        logging.info(f"Processing company sentiment data for date: {year}-{month}-{day}")

        # Đọc dữ liệu từ S3
        path = f"s3a://financial-data-dev-2025/processed_data/company_sentiment/year={year}/month={month}/day={day}"
        stg_company_sentiment = read_staging_data_from_S3(spark, path)

        # Log số lượng bản ghi trong staging
        stg_count = stg_company_sentiment.count()
        logging.info(f"Loaded {stg_count} records from {path}")

        # Lấy danh sách khóa chính từ staging
        news_keys = [row['new_id'] for row in stg_company_sentiment.select("new_id").distinct().collect()]
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
        joined_news = stg_company_sentiment.join(
            dim_news,
            stg_company_sentiment.new_id == dim_news.dim_news_id,
            "left"
        )
        joined_news = joined_news.selectExpr(
            "ticker",
            "news_key",
            "date_id as day_key",
            "sentiment_score",
            "sentiment_label",
            "relevance_score"
        )

        # Lấy danh sách ticker từ joined_news
        company_ticker = [row['ticker'] for row in joined_news.select("ticker").distinct().collect()]
        company_ticker_str = ",".join(f"'{cid}'" for cid in company_ticker)

        # Truy vấn dữ liệu hiện tại từ Redshift (dim_companies)
        dim_query = f'''(SELECT company_key, company_ticker FROM dim_companies 
            WHERE company_ticker IN ({company_ticker_str})) AS dim_companies_sub'''
        logging.info("Querying dim_companies table from Redshift...")
        dim_company = read_dim_table_from_redshift(spark, dim_query, URL, properties)

        # Log số lượng bản ghi trong dim_companies
        dim_company_count = dim_company.count()
        logging.info(f"Loaded {dim_company_count} records from dim_companies table for comparison")

        # Join joined_news và dim_companies
        logging.info("Joining joined_news with dim_companies...")
        joined_company = joined_news.join(
            dim_company,
            joined_news.ticker == dim_company.company_ticker,
            "inner"
        )

        # Chọn các cột cần thiết cho fact table
        new_records = joined_company.selectExpr(
            "company_key",
            "day_key",
            "news_key",
            "sentiment_score",
            "sentiment_label",
            "relevance_score"
        )

        # Log số lượng bản ghi mới
        new_records_count = new_records.count()
        logging.info(f"Prepared {new_records_count} records to insert into fact_company_sentiment")

        # Ghi dữ liệu vào Redshift
        logging.info("Writing data to fact_company_sentiment table in Redshift...")
        load_processed_data_to_redshift(new_records, URL, properties, "fact_company_sentiment")
        logging.info(f"Inserted {new_records_count} records into fact_company_sentiment table")

    except Exception as e:
        logging.error(f"Error processing company sentiment data for {current_date.strftime('%Y-%m-%d')}: {e}")

    spark.stop()
    logging.info("Finished loading company sentiment data into fact_company_sentiment table.")

# Gọi hàm
load_company_sentiment_into_dw()