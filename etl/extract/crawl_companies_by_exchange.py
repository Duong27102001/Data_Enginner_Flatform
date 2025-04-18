import requests
import datetime
import json, logging
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.constants import API_COMPANY_KEY
from utils.api_utils import fetch_data, save_to_file
# Cấu hình logging
# logging.basicConfig(
#     level=logging.INFO,  # Hiển thị log từ mức INFO trở lên
#     format="%(asctime)s - %(levelname)s - %(message)s",  # Định dạng log
#     handlers=[
#         logging.StreamHandler()  # Hiển thị log trên console
#     ]
# )
def crawl_companies_by_exchange():
    # Define a list of stock exchanges to fetch data from
    exchanges = ["NYSE", "NASDAQ"]
    # Initialize an empty list to store company data
    all_companies = []
    try:
        # Loop through each exchange and retrieve the list of companies
        for exchange in exchanges:
            url = f'https://api.sec-api.io/mapping/exchange/{exchange}?token={API_COMPANY_KEY}'
            companies = fetch_data(url, None)
            if companies:
                logging.info(f"[{exchange}] Fetched {len(companies)} companies")
            else:
                logging.info(f"[{exchange}] No companies found")
            
            all_companies.extend(companies)
                
        # Generate file name with current date
        current_date = datetime.date.today()
        path = "raw_data/companies"
        name_file = "crawl_companies"
        logging.info(f"[{current_date}] Saving {len(all_companies)} companies to file")
        # Save the data to a file
        save_to_file(all_companies, current_date, path,  name_file)
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data for {current_date}: {e}")
    except Exception as e:
        logging.error(f"[{current_date}] Unexpected error: {e}")
    
    return None

# crawl_companies_by_exchange()
