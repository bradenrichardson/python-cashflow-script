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
import boto3
import re

## TODO: Catch invalid_grant: Token has been expired or revoked and delete token.json


## ------------------------------------------------------------------------------ ##

dynamodb_table_name = os.environ['dynamodb_table_name']
time_max = os.environ['time_max']
s3_bucket_name = os.environ['s3_bucket_name']


def get_calendar_events():
    s3_client = boto3.client("s3")
    object_key = 'token.json'
    file_content = s3_client.get_object(
        Bucket=s3_bucket_name, Key=object_key)["Body"].read()
    json_file_content = json.loads(file_content)
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None
    
    os.chdir('/tmp')
    if not os.path.exists(os.path.join('tokendir')):
        os.makedirs('tokendir')
    
    filename = 'token.json'
    save_path = os.path.join(os.getcwd(), 'tokendir', filename)
    with open(save_path, 'w') as fp:
        json.dump(json_file_content, fp)
    

    if file_content:
        creds = Credentials.from_authorized_user_file(save_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        s3_client.put_object(Bucket=s3_bucket_name, Key=object_key, Body=creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    start = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=start, timeMax=time_max,
                                        maxResults=2500, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    calendar_event_ids = []
    
    if not events:
        print('No upcoming events found.')
    for event in events:
            calendar_event_ids.append(
                event['id']
            )        
            
    dynamodb = boto3.resource('dynamodb',
                          region_name='ap-southeast-2'
                )
    table = dynamodb.Table(dynamodb_table_name)

    dynamodb_client = boto3.client('dynamodb')
    response = table.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    
    for item in data:
        if item.get('id') not in calendar_event_ids:
            response = dynamodb_client.delete_item(TableName=dynamodb_table_name, Key={
                    'id' : { 
                        'S': item.get('id')
                            }
                        })
            print(response)

        start = datetime.datetime.utcnow().isoformat() + 'Z'

        data = []


    for event in events:
        if re.findall('\((.*?)\)', event['summary']):
            if 'Income' not in event['summary'] and 'Due' not in event['summary'] and 'Spending' not in event['summary'] and 'Savings' not in event['summary'] and 'Debt' not in event['summary']:
                continue
    
            if 'Income' in event['summary']:
                value = re.findall('[0-9]+', event['summary'])
                type = 'Income'
    
            if 'Due' in event['summary']:
                value = re.findall('[0-9]+', event['summary'])
                type = 'Bills'
    
            if 'Debt' in event['summary']:
                value = re.findall('[0-9]+', event['summary'])
                type = 'Debt'
            
            if 'Spending' in event['summary']:
                value = re.findall('[0-9]+', event['summary'])
                type = 'Spending'
            
            if 'Savings' in event['summary']:
                value = re.findall('[0-9]+', event['summary'])
                type = 'Savings'
    
            title = re.findall('\((.*?)\)', event['summary'])
            dynamodb_client.put_item(TableName=dynamodb_table_name, Item={
                
                'id':{'S': event['id']},
                'date':{'S': event['start'].get('date')},
                'type':{'S': type},
                'value':{'N': value[0]},
                'title':{'S': title[0]}
                    })




## ------------------------------------------------------------------------------ ##


def lambda_handler(event, context):
    get_calendar_events()