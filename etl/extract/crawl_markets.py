import requests
import datetime
import json, os
import sys, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.constants import API_MARKET_KEY
from utils.api_utils import fetch_data, save_to_file

logging.basicConfig(
    level=logging.INFO,  # Hiển thị log từ mức INFO trở lên
    format="%(asctime)s - %(levelname)s - %(message)s",  # Định dạng log
    handlers=[
        logging.StreamHandler()  # Hiển thị log trên console
    ]
)
def crawl_markets() -> None:
    """
    Fetch current market status from Alpha Vantage API and save to a JSON file.
    
    The data includes closed/open status of major stock markets.
    """
    
        # Send a request to Alpha Vantage API to retrieve market status information
    url = f'https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={API_MARKET_KEY}'
        
    current_date = datetime.date.today()
    try:
        market = fetch_data(url, "markets") 
        if market:
            logging.info(f"[{current_date}] Fetched {len(market)} OHLC records")
        else:
            logging.info(f"[{current_date}] No OHLC records found")     
            
        path = "raw_data/markets"
        name_file = "crawl_markets"
        save_to_file(market, current_date, path,  name_file)
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data for {current_date}: {e}")
    except Exception as e:
        logging.error(f"[{current_date}] Unexpected error: {e}")
    return None

crawl_markets()
