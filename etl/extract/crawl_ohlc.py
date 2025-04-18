import requests, logging
import time
from datetime import datetime, timedelta
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.constants import API_OHLC_KEY
from utils.api_utils import fetch_data, save_to_file

def crawl_ohlcs():
    """
    Crawl OHLC data for the previous day and save it to a file.
    """
    # Set whether to use adjusted OHLC data
    adjusted = "true"
    # Set the date to fetch data (yesterday)
    current_date = datetime.today() - timedelta(days=1)
    formatted_date = current_date.strftime("%Y-%m-%d")

    # Build the request URL for the current date
    url = (
        f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/"
        f"{formatted_date}?adjusted={adjusted}&include_otc=true&apiKey={API_OHLC_KEY}"
    )

    try:
        ohlcs = fetch_data(url, "results")
        if ohlcs:
            logging.info(f"[{current_date}] Fetched {len(ohlcs)} OHLC records")
        else:
            logging.info(f"[{current_date}] No OHLC records found")
            
        # Save the data to a file
        path = "raw_data/ohlc"
        name_file = "crawl_ohlc"
        save_to_file(ohlcs, current_date, path, name_file)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data for {current_date}: {e}")
    except Exception as e:
        logging.error(f"[{current_date}] Unexpected error: {e}")

    logging.info("Finished crawling OHLC data for the previous day.")

# crawl_ohlcs()