import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.s3_utils import create_bucket_if_not_exists, connect_to_s3
from utils.spark_utils import create_spark_session
from datetime import datetime, timedelta
import logging

def load_raw_data_to_s3(bucket_name: str, path: str):
    """
    Load raw data from local JSON files into S3 as Parquet files for the previous day.
    
    Parameters:
        bucket_name (str): Name of the S3 bucket.
        path (str): Path to the local raw data folder.
    """
    try:
        spark = create_spark_session()
        # Lấy đường dẫn cha
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        dir_path = os.path.join(BASE_DIR, path)

        # Kiểm tra thư mục tồn tại
        if not os.path.exists(dir_path):
            logging.warning(f"Directory {dir_path} does not exist. Skipping...")
            return

        # Định nghĩa ngày hôm qua
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")

        for filename in os.listdir(dir_path):
            # Chỉ xử lý các file có chứa ngày hôm qua trong tên file
            if filename.endswith(".json") and date_str in filename:
                try:
                    # Lấy đường dẫn tới file JSON
                    file_path = os.path.join(dir_path, filename)

                    # Lấy tên file (không bao gồm phần mở rộng)
                    folder_name = filename.replace(".json", "")
                    df = spark.read.option("multiline", "true").json(file_path)

                    # Đếm số lượng bản ghi
                    record_count = df.count()
                    logging.info(f"Loaded {record_count} records from {file_path}")

                    # Load dữ liệu vào S3 với path + folder_name
                    s3_path = f"s3a://{bucket_name}/{path}/{folder_name}"
                    df.write.mode("overwrite").parquet(s3_path)
                    logging.info(f"Data successfully uploaded to {s3_path}")

                except Exception as e:
                    logging.error(f"Error processing file {filename}: {e}")

        logging.info(f"Finished uploading data for date {date_str} from {dir_path} to S3.")

    except Exception as e:
        logging.error(f"Error uploading data to S3: {e}")