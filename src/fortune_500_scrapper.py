import requests
import pandas as pd
from bs4 import BeautifulSoup
import boto3
from io import StringIO

def _upload_data_to_s3(df: pd.DataFrame, bucket_name: str, key: str) -> None:
   
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    
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


# URL from iframe
url = "https://sheet2site.com/api/v3/index.php?key=17uuPHv6jnV0xg9cpv5bvUqysZNTKehT_UbIOADgdXEc&g=1&e=1"

# Add headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
}

# Fetch the content
response = requests.get(url, headers=headers)
response.raise_for_status()  # Raise an error for bad status codes

# Check content type and parse appropriately
if "application/json" in response.headers["Content-Type"]:
    data = response.json()
    df = pd.DataFrame(data)  # Convert JSON to DataFrame
    print(df.head())
elif "text/csv" in response.headers["Content-Type"]:
    from io import StringIO
    df = pd.read_csv(StringIO(response.text))  # Parse CSV
    print(df.head())

elif "text/html" in response.headers["Content-Type"]:
    soup = BeautifulSoup(response.text, 'html.parser')  # Parse HTML content
    print(soup.prettify())

    table = soup.find('table')

    if table:
            # Extract table headers
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            
            # Extract table rows (skip the first row if it's the header)
            rows = []
            for tr in table.find_all('tr')[1:]:  # Skip the header row
                cells = tr.find_all('td')
                row = [cell.get_text(strip=True) for cell in cells]
                if row:
                    rows.append(row)
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=headers)
            _upload_data_to_s3(df=df, bucket_name='alpha-vantage-data-storage', key='stock-markets-dictionaries/fortune_500.csv')
            print(df.head())  # Print the DataFrame for inspection

    else:
        print("No table found in the HTML content.")

else:
    print(f"Unhandled content type: {response.headers['Content-Type']}")