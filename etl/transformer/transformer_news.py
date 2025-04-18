import os, sys, logging
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.spark_utils import create_spark_session
from pyspark.sql.functions import col,  sha2, concat_ws, explode, substring

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Hiển thị log trên console
    ]
)

def process_news():
    """
    Xử lý dữ liệu tin tức của ngày hôm qua.
    """
    logging.info("Starting news data processing...")
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
        input_path = f"s3a://financial-data-dev-2025/raw_data/news/year={year}/month={month}/crawl_news_{year}_{month}_{day}"
        df = spark.read.parquet(input_path).cache()

        # Log số lượng bản ghi khi load dữ liệu
        input_count = df.count()
        logging.info(f"Loaded {input_count} records from {input_path}")

        # Thêm các cột cần thiết
        df = df.withColumn("new_id", sha2(concat_ws("||", col("time_published"), col("title"), col("url"), col("summary")), 256)) \
               .withColumn("authors", concat_ws(", ", col("authors"))) \
               .withColumn("time_published", substring("time_published", 1, 8))

        # Process dim_news
        news = df.selectExpr(
            "new_id",
            "title as new_title",
            "url as new_url",
            "time_published as new_time_published",
            "authors as new_authors",
            "summary as new_summary",
            "source as new_source",
            "overall_sentiment_score as new_overall_sentiment_score",
            "overall_sentiment_label as new_overall_sentiment_label",
            "time_published as news_time_id"
        )

        news_output_path = f"s3a://financial-data-dev-2025/processed_data/news/year={year}/month={month}/day={day}"
        news.write.mode("overwrite").parquet(news_output_path)
        logging.info(f"Processed and saved news data to {news_output_path}")

        # Process company_sentiment
        company_sentiment = df.selectExpr(
            "new_id",
            "ticker_sentiment",
            "time_published as date_id"
        )
        company_sentiment = company_sentiment.withColumn("ticker_sentiment", explode("ticker_sentiment"))
        company_sentiment = company_sentiment.selectExpr(
            "ticker_sentiment.ticker as ticker",
            "ticker_sentiment.relevance_score as relevance_score",
            "ticker_sentiment.ticker_sentiment_label as sentiment_label",
            "ticker_sentiment.ticker_sentiment_score as sentiment_score",
            *[c for c in company_sentiment.columns if c != "ticker_sentiment"]
        )

        company_sentiment_output_path = f"s3a://financial-data-dev-2025/processed_data/company_sentiment/year={year}/month={month}/day={day}"
        company_sentiment.write.mode("overwrite").parquet(company_sentiment_output_path)
        logging.info(f"Processed and saved company sentiment data to {company_sentiment_output_path}")

        # Process topics
        news_topic = df.selectExpr(
            "new_id",
            "topics",
            "time_published as date_id"
        )
        news_topic = news_topic.withColumn("topics", explode("topics"))
        news_topic = news_topic.selectExpr(
            "topics.topic as topic_name",
            "topics.relevance_score as new_topic_relevance_score",
            *[c for c in news_topic.columns if c != "topics"]
        )

        news_topic_output_path = f"s3a://financial-data-dev-2025/processed_data/news_topic/year={year}/month={month}/day={day}"
        news_topic.write.mode("overwrite").parquet(news_topic_output_path)
        logging.info(f"Processed and saved news topic data to {news_topic_output_path}")

    except Exception as e:
        logging.error(f"Error processing data for {current_date.strftime('%Y-%m-%d')}: {e}")

    logging.info("Finished news data processing.")

# Chạy hàm
process_news()