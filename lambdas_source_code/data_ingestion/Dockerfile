# Use AWS Lambda's Python 3.10 base image
FROM public.ecr.aws/lambda/python:3.10

# Set the working directory inside the container
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy application code and requirements
COPY data_ingestion/alpha_vantage_data_ingestion.py ${LAMBDA_TASK_ROOT}/
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies with pip
RUN pip install --no-cache-dir -r requirements.txt

# Command to specify the Lambda handler (file_name.function_name)
CMD ["alpa_vantage_data_ingestion.alpha_vantage_data_accessor"]
