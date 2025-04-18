import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import logging
from pyspark.sql.functions import col
from utils.constants import (
    DATABASE_PASSWORD, DATABASE_USERNAME, properties,
    DATABASE_PORT, DATABASE_HOST, DATABASE_NAME, URL
)
from datetime import datetime
from utils.spark_utils import create_spark_session
from utils.connect_to_redshift import connect_to_redshift
from utils.s3_utils import read_staging_data_from_S3, read_dim_table_from_redshift, load_processed_data_to_redshift


def load_processed_data_into_dw():
    """
    Load processed company data from S3 into Redshift dimension table (dim_companies).
    """
    spark = create_spark_session()
    
    # Define path to processed data on S3
    current_year = datetime.now().year
    current_month = datetime.now().strftime("%m")  # giữ định dạng MM
    path = f"s3a://financial-data-dev-2025/processed_data/companies/year={current_year}/month={current_month}"


    try:
        logging.info(f"Reading staging data from S3 path: {path}")
        stg_companies = read_staging_data_from_S3(spark, path)
        stg_count = stg_companies.count()
        logging.info(f"Loaded {stg_count} records from staging data.")

        # Extract unique keys for join
        company_keys = [row['company_id'] for row in stg_companies.select("company_id").distinct().collect()]
        company_keys_str = ",".join(f"'{cid}'" for cid in company_keys)
        logging.info(f"Extracted {len(company_keys)} unique company keys for comparison.")

        # Query existing dim data for current active records with matching keys
        dim_query = f'''(SELECT * FROM dim_companies 
        WHERE is_current = TRUE AND company_id IN ({company_keys_str})) AS dim_companies_sub'''
        
        logging.info("Querying existing dimension data from Redshift...")
        
        dim_companies = read_dim_table_from_redshift(spark, dim_query,URL, properties)
        dim_count = dim_companies.count()
        logging.info(f"Loaded {dim_count} records from dim_companies table for comparison.")

        # Rename dim columns for comparison
        dim_companies = dim_companies.selectExpr(
            "company_id as dim_company_id",
            "company_name as dim_company_name",
            "company_ticker as dim_company_ticker",
            "company_is_delisted as dim_company_is_delisted",
            "company_category as dim_company_category",
            "company_currency as dim_company_currency",
            "company_location as dim_company_location",
            "company_exchange_name as dim_company_exchange_name",
            "company_region_name as dim_company_region_name",
            "company_industry_name as dim_company_industry_name",
            "company_sic_industry as dim_company_sic_industry",
            "company_sic_sector as dim_company_sic_sector"
        )

        # Join staging and dimension tables using company_id
        logging.info("Joining staging data with dimension data...")
        joined = stg_companies.join(
            dim_companies,
            stg_companies.company_id == dim_companies.dim_company_id,
            "left"
        )

        # Identify new records (not in dim table)
        new_records = joined.filter(col("dim_company_id").isNull()).select(stg_companies.columns)
        new_count = new_records.count()
        logging.info(f"Identified {new_count} new records.")

        # Identify changed records using column-wise comparison
        changed_records = joined.filter(
            (col("dim_company_id").isNotNull()) & (
                (col("company_name") != col("dim_company_name")) |
                (col("company_ticker") != col("dim_company_ticker")) |
                (col("company_is_delisted") != col("dim_company_is_delisted")) |
                (col("company_category") != col("dim_company_category")) |
                (col("company_currency") != col("dim_company_currency")) |
                (col("company_location") != col("dim_company_location")) |
                (col("company_exchange_name") != col("dim_company_exchange_name")) |
                (col("company_region_name") != col("dim_company_region_name")) |
                (col("company_industry_name") != col("dim_company_industry_name")) |
                (col("company_sic_industry") != col("dim_company_sic_industry")) |
                (col("company_sic_sector") != col("dim_company_sic_sector"))
            )
        ).select(stg_companies.columns)
        changed_count = changed_records.count()
        logging.info(f"Identified {changed_count} changed records.")

        # Update existing records in Redshift: set is_current = FALSE
        company_keys_to_update = [row["company_id"] for row in changed_records.select("company_id").distinct().collect()]
        if company_keys_to_update:
            keys_str = ",".join(f"'{cid}'" for cid in company_keys_to_update)
            update_query = f"""
                UPDATE dim_companies
                SET is_current = FALSE, end_date = CURRENT_DATE
                WHERE is_current = TRUE AND company_id IN ({keys_str});
            """
            try:
                logging.info("Updating existing records in Redshift (is_current = FALSE)...")
                conn = connect_to_redshift(DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USERNAME, DATABASE_PASSWORD)
                cur = conn.cursor()
                cur.execute(update_query)
                conn.commit()
                cur.close()
                conn.close()
                logging.info("Updated existing records in Redshift successfully.")
            except Exception as e:
                logging.error("Error updating records in Redshift: %s", str(e))
                raise

        # Append new and changed records to Redshift
        final_df = new_records.unionByName(changed_records)
        final_count = final_df.count()
        logging.info(f"Appending {final_count} records to dim_companies table in Redshift...")
        load_processed_data_to_redshift(final_df, URL,  properties, "dim_companies")
        logging.info(f"Loaded {final_count} records into dim_companies table successfully.")

        spark.stop()
        logging.info("Finished loading data into dim_companies table.")

    except Exception as e:
        logging.exception("Failed to load data into dimension table:")

# Gọi hàm
load_processed_data_into_dw()