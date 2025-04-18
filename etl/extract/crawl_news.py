import requests, logging
import datetime
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.constants import API_NEWS_KEY
from utils.api_utils import fetch_data, save_to_file

def crawl_news_full_days():
    """
    Fetch news data from Alpha Vantage API for the previous day,
    dividing the day into multiple time slots to bypass the per-request limit.

    The function saves the news data of the previous day into a JSON file.
    """
 
    limit = 1000  # Maximum allowed limit per API call
    # Define time slots to split a day (e.g., 00:00-12:00, 12:00-23:59)
    time_slots = ["0000", "1200", "2359"]

    # Define the date to collect data (yesterday)
    current_date = datetime.date.today() - datetime.timedelta(days=1)  # Yesterday

    all_news_in_a_day = []  # Store news for the current day

    for i in range(len(time_slots) - 1):
        time_from = current_date.strftime("%Y%m%d") + "T" + time_slots[i]
        time_to = current_date.strftime("%Y%m%d") + "T" + time_slots[i + 1]

        url = (
            f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
            f"&apikey={API_NEWS_KEY}&limit={limit}&time_from={time_from}&time_to={time_to}"
        )

        try:
            news = fetch_data(url, "feed")
            if news:
                logging.info(f"[{current_date}] Fetched {len(news)} news between {time_from[-4:]} and {time_to[-4:]}")
                all_news_in_a_day.extend(news)
            else:
                logging.info(f"[{current_date}] No news found between {time_from[-4:]} and {time_to[-4:]}")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data for {current_date}: {e}")
        except Exception as e:
            logging.error(f"[{current_date}] Unexpected error: {e}")
        
    path = "raw_data/news"
    name_file = "crawl_news"
    
    logging.info(f"Saving news data for {current_date} with {len(all_news_in_a_day)} records")
    save_to_file(all_news_in_a_day, current_date, path, name_file)