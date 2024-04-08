import streamlit as st

from s3_bucket_tools import *
from helper_funcs    import *

# Initialize s3 class
s3          = S3_class()
bucket_name = 'expenses-bucket-348826608386'

# Add a title to the app
st.title("Welcome to Your Expenses Tool!")

# Create an input for the user's name
exp_date = st.date_input('Enter the date you want to track for')
date_str, month_year = get_date_attr(exp_date) 

month_file = f'expenses_{month_year}.csv'.lower()
df = s3.read_from_S3(bucket_name=bucket_name, file_path=month_file)

if df is None:
    st.write(f'{month_file} doe snot exist, creating a new one')
    df = pd.DataFrame(columns=['date_str','item_bought','category', 'shop', 'cost'])


item     = st.text_input('What did you buy?')
location = st.text_input('Where did you buy it?')
price    = st.number_input('How much was the item')
category = st.selectbox('What is the category for this item?', ('uncatgorised','Necessary Car Bills', 'Car Penalties','Food','Necessary Bills', 'Social', 'Girlfriend', 'Optional Bills'))


