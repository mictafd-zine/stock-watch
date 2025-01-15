# STOCK PRICE MONITOR
#### Problem Statement
- User has limited time to look at stock prices to buy/sell. 
- User is interested in monitoring as many stock prices as possible.
- On a daily basis user would like to know which stocks dropped the most to buy and which one increased the most to sell.
- User wants to do this completely free of charge or minimal costs.

### Project Overview
The project will be divided into 3 parts:
- Data ingestion
- Analytics
- Alerting


### Data Ingestion
- We will use the Alpha Vantage API to get the stock price data.
- We get stock price for specified organisation for D-1. 
- We iterate through the Fortune500 csv trying to read a csv for each company.
- If the csv does not exist, we query the API to get data and save on the specified path
- *Limitation*: Free tier on the API is limited to 25 requests per day
- Backfilling from start of 2024.
- Data will be Partitioned by organisation, year, month. Each month will have daily files for ech company.

### Analytics
- User will get a summary of biggest movers on the market daily, month-on-month, year-on-year
- read daily file for the 500 companies.
- For each company, compare closing price with opening price.
- This way you get companies with largest movements.
- query the data for the the last 30 days. specific metrics to follow
- query the data for the year to date. specific metrics to follow
- More Analytics to be added, once initial prototype is done.
- Measure stock volatility in the future

### Alerting 
- The best way to send these notifications will be decided.
- Proposed methodology: email with a table and relevant metrics limited to the top x biggest movers. 
- Big movers year-on-year
- Big movers month-on-month 
- Big movers day-on-day


### Security and Authentication

### Next Steps
- Setup a CD pipeline to deploy the python code lambda function everytime python code changes.
- Update pipeline to deploy the lambda function everytime the python code changes.
- Remove root user access on AWS account!!! after testing.
- Develop API calls using free tier For top 25 companies. [Free API tier limitation]
- Develop lambda function that reads alerts biggest movers on the market (absolute value change and percentage)
- Setup Email Alerts on the big movers (D-1)? Is this too late? 
- Can we build a dashboard?
- Setup role for Michael for authentication to deploy resources.
- Remove root user access on AWS account!!!
- Separate Python Codes from Infra Code in order to setup Github actions to upload new package to s3 everytime python code changes. 
- Configure automated python code formatting for repositoy using ruff
- Setup a ci pipeline to run the python code formatting and linting
- Make a lambda function that updates Fortune500 regualarly and updates the data in the s3 bucket
- Automate detecting environment detection for development and production.

### Python Code deployment 
Starting from project root directory:
```bash

cd infra
terraform plan
terraform apply

```


### Cost Estimation and Technology Stack
1. Amazon Lambda
AWS Free Tier: The Free Tier provides 1 million free requests and 400,000 GB-seconds of compute time per month, which is enough for many small to moderate workloads.
Cost Outside Free Tier:
$0.20 per 1 million requests.
$0.00001667 per GB-second of compute time.
Estimate for this setup: A function running every 5 minutes will execute 8,640 times per month. If the function is light (e.g., 128 MB memory, running for 1 second), it would use roughly 1.1 GB-seconds per month—well within the Free Tier for light usage.
2. Amazon CloudWatch Events (EventBridge)
AWS Free Tier: The Free Tier offers 1 million events per month at no cost.
Cost Outside Free Tier:
$1.00 per million custom events published.
Estimate for this setup: One event every 5 minutes results in about 8,640 events per month, which would still be within the Free Tier.
3. Amazon Secrets Manager
AWS Free Tier: AWS Secrets Manager offers no free tier for secret storage.
Cost:
Secrets Manager charges $0.40 per secret per month.
Additional charges apply for API calls to retrieve secrets beyond the first 10,000 requests per month, which are free.
Estimate for this setup: For one secret (the API key), expect a $0.40 monthly charge if this usage exceeds AWS promotional periods or credits.
4. Amazon S3
AWS Free Tier: The Free Tier provides 5 GB of standard storage and 20,000 GET/2,000 PUT requests per month.
Cost Outside Free Tier:
$0.023 per GB for Standard storage.
$0.005 per 1,000 PUT, COPY, POST, or LIST requests.
$0.0004 per 1,000 GET requests.
Estimate for this setup: For minimal storage (e.g., storing small API responses), usage could stay within the Free Tier. However, with frequent or large data outputs, costs may accrue.
5. Amazon CloudWatch Logs
AWS Free Tier: Offers 5 GB of log data ingestion and 5 GB of archived storage per month.
Cost Outside Free Tier:
$0.50 per GB ingested for log data.
$0.03 per GB archived per month.
Estimate for this setup: Log data usage should be minimal if only basic logs are written. However, extensive logging or longer retention periods could incur costs beyond the Free Tier.
#### Summary of Expected Monthly Costs (Outside Free Tier)
Lambda: Free for minimal usage.
CloudWatch Events: Likely free for this setup.
Secrets Manager: ~$0.40 per month for one secret.
S3: Potentially free for small storage amounts; otherwise, minimal.
CloudWatch Logs: Likely free unless logging extensively.
#### Total Expected Costs
For typical usage under this setup, expect no or minimal costs beyond the $0.40 per month for Secrets Manager if your usage stays within Free Tier limits and is optimized for low storage and logging.


