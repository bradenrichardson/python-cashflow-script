from __future__ import print_function
import datetime
from os import error
import os.path
import json
from requests import api
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import argparse
import re

## TODO: Parse decimal dollar values
## TODO: Gracefully handle DUE/INCOME events with no dollar value
## TODO: Start date


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

parser = argparse.ArgumentParser(description="A tool to export UP transactions in a CSV file")
parser.add_argument('--end_date', type=str, required=True)
parser.add_argument('--start_date', type=str)
args = parser.parse_args()


def main():
    income = 0
    bills = 0.0
    debt = 0.0
    spending = 0.0
    savings = 0.0
    try:
        dtdate = datetime.datetime.strptime(args.end_date, '%Y-%m-%d')
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print('refreshing')
                creds.refresh(Request())
                print(creds.to_json())
            else:
                print('app-flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('calendar', 'v3', credentials=creds)
        if args.start_date:
            start_raw = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
            start = start_raw.isoformat() + 'Z'
            delta = dtdate - start_raw
        else:
            start = datetime.datetime.utcnow().isoformat() + 'Z'
            delta = delta = dtdate - datetime.datetime.utcnow()

        events_result = service.events().list(calendarId='primary', timeMin=start,
                                            maxResults=2000, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            if 'Income' not in event['summary'] and 'Due' not in event['summary'] and 'Spending' not in event['summary'] and 'Savings' not in event['summary'] and 'Debt' not in event['summary']:
                continue
            start = event['start'].get('dateTime', event['start'].get('date'))
            date_start = datetime.datetime.strptime(start, '%Y-%m-%d')
            if date_start < dtdate:
                if 'Income' in event['summary']:
                    value = re.findall('[0-9]+', event['summary'])
                    income = income + int(value[0])

                if 'Due' in event['summary']:
                    value = re.findall('[0-9]+', event['summary'])
                    bills = bills + int(value[0])
                
                if 'Debt' in event['summary']:
                    value = re.findall('[0-9]+', event['summary'])
                    debt = debt + int(value[0])
                
                if 'Spending' in event['summary']:
                    value = re.findall('[0-9]+', event['summary'])
                    spending = spending + int(value[0])
                
                if 'Savings' in event['summary']:
                    value = re.findall('[0-9]+', event['summary'])
                    savings = savings + int(value[0])

        days = delta.days
        
        cashflow = income - bills - savings - spending - debt
        total_expenses = debt + bills + savings + spending

        print('---INCOME---')
        print('Income : ${}\n'.format(income))
        print('---EXPENSES---')
        print('Spending: ${}'.format(spending))
        print('Saving: ${}'.format(savings))
        print('Bills: ${}'.format(bills))
        print('Debt: ${}\n'.format(debt))
        print('Total Expenses: ${}\n'.format(total_expenses))
        print('---CASHFLOW---')
        print('Cashflow: ${}'.format(cashflow))
        daily_spend = round(cashflow / days)
        weekly_spend = round(daily_spend * 7)
        print('Daily Spend: ${}'.format(daily_spend))
        print('Weekly Spend: ${}\n'.format(weekly_spend))

        returnDict = {
            'saving' : savings,
            'debt' : debt,
            'spending' : spending,
            'income' : income,
            'bills' : bills,
            'cashflow' : cashflow,
            'dailySpend' : daily_spend,
            'weeklySpend' : weekly_spend
        }
        return returnDict
    except error as E:
        print(E)

if __name__ == '__main__':
    main()