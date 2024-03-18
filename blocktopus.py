# Imports
import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import time
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler

def fetch_prices():
    # Replace with your specific tariff
    url = 'https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/'
    # Replace with your API key
    api_key = 'YOUR_API_KEY_HERE'

    # Fetches the electricity prices using the API
    response = requests.get(url, auth=HTTPBasicAuth(api_key,""))

    if response.status_code == 200:
        data = response.json()
        print("Success:")
    else:
        print("Error:", response.status_code)
    
    # Initialize an empty dictionary
    time_price_dict = {}

    # Iterate over each item in the results and store it in the dictionary
    for record in data["results"]:
        time_period = record["valid_from"]
        price = record["value_inc_vat"]
        time_price_dict[time_period] = price

    return time_price_dict

def get_current_time():
    # Get the current local date and time
    now = datetime.now()

    # Subtract minutes and seconds to round down to the nearest half hour
    subtract_minutes = now.minute % 30
    subtract_seconds = now.second
    
    # Subtract the excess minutes and seconds from the current time
    rounded_down_time = now - timedelta(minutes=subtract_minutes, seconds=subtract_seconds)
    
    # Format the date and time in the format that matches the octopus price data
    current_time = rounded_down_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    return current_time

def get_price(time_str, time_price_dict):
    # Finds the price for a given half hour period
    price = time_price_dict.get(time_str)
    print(price)
    return(price)

def check_profitable():
    # Electircity price in pence/KwH at which mining is enabled
    threshold = 10
    
    # Saves all prices to a variable
    time_price_dict = fetch_prices()
    # Gets the current time in the correct format
    current_time = get_current_time()
    # Finds the price for the given half hour time period
    current_price = get_price(current_time, time_price_dict)    
    
    if current_price < threshold:
        enable_mining()
    else:
        disable_mining()

def enable_mining():
    # Enables mining through windows command shell 
    command = "cudominercli enable"
    try:
        # Execute the command in the shell
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def disable_mining():
    # Disables mining through windows command shell 
    command = "cudominercli disable"
    try:
        # Execute the command in the shell
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def main():
    # Check proftiable on launch
    check_profitable()
    
    # Create a scheduler
    scheduler = BackgroundScheduler()
    
    # Schedules function to run at every hour and half-hour mark
    scheduler.add_job(check_profitable, 'cron', minute='0,30')
    
    # Start the scheduler
    scheduler.start()
    
    try:
        # Keep the script running
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Shutdown the scheduler upon exiting the script
        scheduler.shutdown()

if __name__== "__main__" :
    main()
