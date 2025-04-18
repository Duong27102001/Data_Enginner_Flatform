from pyspark.sql import SparkSession
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.constants import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID
def create_spark_session() -> SparkSession:
    try:
        spark = SparkSession.builder \
        .appName("Findata_ETL_Pipeline") \
        .master("spark://spark-master:7077") \
        .config("spark.sql.caseSensitive", "true") \
        .config("spark.hadoop.fs.s3a.access.key", AWS_ACCESS_KEY_ID) \
        .config("spark.hadoop.fs.s3a.secret.key", AWS_SECRET_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .config("spark.jars", "C:\\jars\\hadoop-aws-3.3.4.jar," \
                          "C:\\jars\\aws-java-sdk-bundle-1.12.262.jar," \
                          "C:\\jars\\jets3t-0.9.7.jar," \
                          "C:\\jars\\redshift-jdbc42-2.1.0.32.jar") \
    .getOrCreate()
        
        print("Spark session created successfully!")
        return spark

    except Exception as e:
        print(f"Failed to create spark session: {e}")
        return None
