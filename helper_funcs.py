import datetime as dt 
import pandas   as pd

def get_date_attr(date_item):
    """
    Assumes local time!
    """
    date_dt    = pd.to_datetime(date_item)
    date_str   = date_dt.strftime('%Y-%m-%d')
    month_year = date_dt.strftime('%b_%y')
    return date_str, month_year
