# Calculate Cashflow - Command Line
## What does it do?
* Forecast incoming and outgoing finances
    * Income
    * Bills Due
    * Savings
    * Spending
    * Debt

This simple tool uses the google api client to read the calendar events linked to your google account. By using the recurring event feature in google calendar and setting up your incoming and outgoing finances on schedules we can forecast cashflow into the future or for any time period. This is particularly useful if you are trying to figure out realistic savings goals, the best ways to accelerate your debt paydown or how a pay rise might affect your bottom line.

The calculate_cashflow.py file returns a command line response when run with --start_date and --end_date parameters passed through, or you can host the file in something like a lambda and feed it into a BI or data visualisation tool.


### How to use - Local Script
1. Register for Oauth2.0 authentication through google's API console: https://developers.google.com/calendar/api/guides/auth 
2. Download the credential file they gave you to this directory, save it as credentials.json
3. Create recurring or one-off calendar events that reflect your real life finance schedules with the following format
    * Income - <Payer> $AMOUNT
    ![Income Example](/img/income.PNG)
    * Due - <Payee> $AMOUNT
    ![Bills Due Example](/img/bills.PNG)
    * Savings - <Purpose> $AMOUNT
    ![Savings Example](/img/savings.PNG)
    * Debt - <Purpose> $AMOUNT
    ![Debt Example](/img/debt.PNG)
    * Spending - <Purpose> $AMOUNT
    ![Spending Example](/img/spending.PNG) 

4. Execute the script
    - --end_date - REQUIRED - example: 2021-10-31
    - --start_date - OPTIONAL - example 2021-10-14
        * If start date not specified then the current datetime is assumed as the start
    - Example: python3 calculate_cashflow.py  --end_date 2021-11-15 
    ![Output Example](/img/output.PNG)


# Calculate Cashflow Lambda

### Pre Requisites
* Perform all the steps for the Local Script


### How to use - AWS
1. Create lambda layer and upload to AWS
    * python3 -m pip install -r requirements.txt -t ./python --no-user
    * zip -r calculate_cashflow_layer.zip ./python/
2. Create lambda
    * calculate_cashflow_lambda.py
    * set all environment variables
3. Create S3 bucket
    * Upload the token.json you generated in the local script section
4. Create EventBridge rule
    * Create a rule that triggers your lambda once a day (or whatever time period you like)
5. Create Athena Data Source
    * Deploy the DynamoDB lambda application
6. Create Data Set in Quicksight with the Athena data source
    * Create a scheduled refresh that runs just after your EventBridge rule
7. Create analysis and start creating visuals!
