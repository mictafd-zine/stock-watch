import pandas as pd
import numpy as np
import datetime as dt
import boto3
from io import StringIO
import botocore.exceptions


S3_BUCKET_NAME = 'alpha-vantage-data-storage'

def _read_file_from_s3(object_key: str) -> pd.DataFrame:

    try:
        aws_s3_client = boto3.client("s3", region_name='eu-west-1')
        
        # Attempt to fetch the file from S3
        response = aws_s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=object_key)
        file_content = response['Body'].read().decode('utf-8')  # Convert bytes to string

        # Convert string data into a Pandas DataFrame
        df = pd.read_csv(StringIO(file_content))
        
        return df
    
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(f"The file {object_key} does not exist in the S3 bucket.")
            return None
        
def _generate_s3_key(date_: pd.Timestamp, ticker: str) -> str:
    return f'company={ticker}/year={date_.year}/month={date_.strftime("%Y%m")}/day={date_.strftime("%d")}/{ticker}_{date_.strftime("%Y-%m-%d")}.csv'


def _data_loader(tickers: list) -> pd.DataFrame:

    now_ = dt.datetime.now()
    today_ = now_.strftime('%Y-%m-%d')

    start_date = (now_ - pd.Timedelta(days=25)).strftime('%Y-%m-%d')
    ticker_col = 'ticker'
    time_col = 'utc_time'

    df = pd.DataFrame()
    for date_ in pd.date_range(start_date, today_, freq='D'):
        for ticker in tickers:
            ticker_day_data = _read_file_from_s3(_generate_s3_key(date_, ticker))
            
            if ticker_day_data is not None:
                ticker_day_data.columns = ['utc_time'] + list(ticker_day_data.columns[1:])
                ticker_day_data[ticker_col] = ticker
                df = pd.concat([df, ticker_day_data])
            else:
                pass

    return df.sort_values(by=time_col)

if __name__ == "__main__":
    tickers = ['GOOGL', 'NVDA']
    df = _data_loader(tickers)
    df.head()

