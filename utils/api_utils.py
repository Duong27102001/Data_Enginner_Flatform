import requests
import json
import os
import logging

def fetch_data(url, atribute):
    "Guing yêu cầu GET đến API và trả về dữ liệu JSON"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        if atribute is None:
            return data
        return data.get(atribute, [])
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        return []
    
def save_to_file(data, current_date, path, name_file):
    """Lưu dữ liệu vào tệp JSON"""
    
    year = current_date.strftime("%Y")
    month = current_date.strftime("%m")
    day = current_date.strftime("%Y_%m_%d")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_path = os.path.join(base_dir, path, f"year={year}", f"month={month}")
    os.makedirs(dir_path, exist_ok=True)
    
    file_path = os.path.join(dir_path, f"{name_file}_{day}.json")
    
    with open(file_path, "w") as output_file:
        json.dump(data, output_file, indent=3)
    
    logging.info(f"Data saved to: {file_path}")