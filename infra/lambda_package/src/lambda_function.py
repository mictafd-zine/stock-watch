import boto3
import pandas as pd
import datetime as dt
import numpy as np
import requests
import os
import json
import pytz
from botocore.exceptions import ClientError
import io
from io import StringIO


STORAGE_BUCKET_NAME = "alpha-vantage-data-storage"
MVP_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'BA', 'PLTR', 'TGT', 'NFLX', 'TEM']


def _upload_data_to_s3(df: pd.DataFrame, bucket_name: str, key: str) -> None:
   
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=True)

    
    try:
        s3 = boto3.client('s3')
        response = s3.put_object(Bucket=bucket_name, Key=key, Body=csv_buffer.getvalue())

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {
                f"{key} uploaded successfully to {bucket_name}"
                }
            
        else:
            return {
                    'response': response
                }
            
    except Exception as e:
        return {
                'error': str(e)
            }

def _get_url(symbol_: str,api_key_: str ,function_:str="TIME_SERIES_INTRADAY",interval_:str="5min"):
  """
  Generates the URL to be used to make the API query
  :param (str) function_ type of data required, default is "TIME_SERIES_INTRADAY"
  :param (str) symbol_ the company symbol
  :param (str) interval_ data granularity, default 5 minutes
  :param (str) api_key_ this is your alpha vintage API key
  :return (str) the url to be sent to the alpha vintage platform
  """
  return f'https://www.alphavantage.co/query?function={function_}&symbol={symbol_}&interval={interval_}&apikey={api_key_}'
  
def _send_query(url: str) -> pd.DataFrame:
    # TODO: need to remove the hard coded dictionary key
    return pd.DataFrame(requests.get(url).json()['Time Series (5min)']).transpose()
        

def _generate_s3_key(symbol_: str) -> str:
    time_now = dt.datetime.now(tz=pytz.UTC) - dt.timedelta(days=1)

    date_str = time_now.strftime('%Y-%m-%d')
    year_ = time_now.strftime('%Y')
    month_ = time_now.strftime('%Y%m')
    day_   = time_now.strftime('%d')

    return f'company={symbol_}/year={year_}/month={month_}/day={day_}/{symbol_}_{date_str}.csv'

def _check_day_data_availability(s3_path: str, aws_s3_client: boto3.client) -> bool:

    try:
        response = aws_s3_client.get_object(Bucket=STORAGE_BUCKET_NAME, Key=s3_path)
        return response['ResponseMetadata']['HTTPStatusCode'] == 200
    except ClientError as e:
        # Check if the error is a 'NoSuchKey' error, meaning the file does not exist
        if e.response['Error']['Code'] == 'NoSuchKey':
            return False
        # For other errors, re-raise the exception
        raise

def _load_fortune_500_tickers() -> list:

    aws_s3_client = boto3.client("s3", region_name='eu-west-1')
    response = aws_s3_client.get_object(Bucket='alpha-vantage-data-storage', Key='stock-markets-dictionaries/fortune_500.csv')
    (pd.read_csv(io.StringIO(response['Body'].read().decode('utf-8') )))['Ticker'].tolist()
    
    return MVP_TICKERS

def _get_ticker_to_process(tickers: list, aws_s3_client: boto3.client) -> str:

    index_ = 0
    max_index = len(tickers) - 1
    data_available = True
    while data_available:
        symbol_ = tickers[index_]
        s3_path = _generate_s3_key(symbol_)
        data_available = _check_day_data_availability(s3_path, aws_s3_client)
        index_ += 1
        if index_ > max_index:
            symbol_ = ''
            break

    return symbol_


def lambda_handler(event, context):
    secret_name = os.environ["SECRET_NAME"]
    region_name = os.environ["REGION"]

    # Create a Secrets Manager client
    aws_serects_manager_client = boto3.client("secretsmanager", region_name=region_name)
    aws_s3_client = boto3.client("s3", region_name=region_name)

    fortune_500_tickers = _load_fortune_500_tickers() 
    symbol_ = _get_ticker_to_process(fortune_500_tickers, aws_s3_client)

    if symbol_ == '':
        print("No more tickers to process")
        return
    else:
        print(f"Processing {symbol_}")
        api_key_ = json.loads(aws_serects_manager_client.get_secret_value(SecretId=secret_name)["SecretString"])["AlphaVantageAPIKey"]
        url_ = _get_url(symbol_, api_key_)
        df   = _send_query(url_)
        _upload_data_to_s3(df, STORAGE_BUCKET_NAME,_generate_s3_key(symbol_))

