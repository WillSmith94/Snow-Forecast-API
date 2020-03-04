from bs4 import BeautifulSoup
from prettytable import PrettyTable
from twilio.rest import Client 
from dotenv import load_dotenv

import os
import requests

def run():

    # If SEND_MESSAGE = True, will send SMS message with snow report to your phone
    SEND_MESSAGE = True
    LOAD_DOTENV = False

    if LOAD_DOTENV:
        load_dotenv()

    # Get live snow report from SnowForecast.com and get html
    page = requests.get("https://www.snow-forecast.com/resorts/Meribel/6day/mid")
    soup = BeautifulSoup(page.text, features="lxml")

    # Extract the snow cm figures for each day in the week as a list
    snow_row = soup.find_all("tr", class_="forecast-table-snow")[1]
    cm = []
    NUMBEROFDAYS = 7

    for snow_column in snow_row.children:
        cm_value = snow_column.get_text()

        if cm_value == "-":
            cm_value = 0
        cm_value = int(cm_value)
        
        cm.append(cm_value)

    # Get today's date
    from datetime import datetime,timedelta
    today = datetime.now()

    # Create list of today's date and subsequent days for the week
    one_day = timedelta(days = 1)
    days = []
    for numberofdays in range(NUMBEROFDAYS):
        new_day = today + one_day*numberofdays
        new_day = new_day.strftime("%a-%d/%m")
        days.append(new_day)

    # Combine daily CM figures with dates as a list
    daily_cm = []

    for numberofdays in range(NUMBEROFDAYS):
        new_day = cm[numberofdays*3:numberofdays*3 + 3]
        daily_cm.append(new_day)

    data = list(zip(days,daily_cm))

    # Turn list of dates and daily CM figures into table
    table = PrettyTable()
    table.field_names = ["Date","AM","PM","Night","Total"]
    for datum in data:
        total = sum(datum[1])
        table.add_row([datum[0],*datum[1],total])

    # Send SMS message to your phone with table if SEND_MESSAGE is True
    if SEND_MESSAGE is True: 

        account_sid = os.getenv("ACCOUNT_SID")
        auth_token = os.getenv("AUTH_TOKEN")

        client = Client(account_sid, auth_token) 
        
        message = client.messages \
                    .create(
                        body= "```\n"+str(table)+"\n```",      
                        from_=os.getenv("TWILIO_PHONE_NUMBER"),
                        to=os.getenv("MY_PHONE_NUMBER")
                    )
    
        print(message.sid)

    # If not, print as table
    else:
        print(table)

def pubsub(event, context):
    run()