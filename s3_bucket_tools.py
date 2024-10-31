import pandas as pd
import numpy as np

from io import StringIO
import boto3 # boto3 package is the package that is used to connect to S3 bucket in python. 
import os

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


aws_keys={
  "access_key": os.environ.get("ACCESS_KEY"),
  "secret_key": os.environ.get("SECRET_KEY"),
  "region":"eu-west-1"}


class S3_class():
  
  service = 's3' # all instances of this class will have the service name as s3 since the purpose of this class is to interact with S3
  
  def __init__(self,region_name=aws_keys['region'], aws_access_key_id=aws_keys['access_key'], aws_secret_access_key=aws_keys['secret_key']): 
    """
    Each instance of the class should have the specifed variables here passed as arguments to the class instance. 
    """
    self.region_name = region_name 
    self.aws_access_key_id = aws_access_key_id
    self.aws_secret_access_key = aws_secret_access_key
    
  
  def connect(self):
    """
    This function makes a connection to the S3 bucket.
    """
    s3 = boto3.resource(
      service_name = self.service, 
      region_name=self.region_name,
      aws_access_key_id=self.aws_access_key_id,
      aws_secret_access_key=self.aws_secret_access_key
    )
    return s3 
  
  def list_all_buckets(self):
    """
    This function prints all buckets in the current S3 instance
    """
    # call the connect function to connect to the resource 
    s3 = self.connect()
    
    # now get all the buckets
    for bucket in s3.buckets.all():
      print(bucket.name)
    
      
  def read_from_S3(self,bucket_name,file_path, status_print  = True,**kwargs):
    """
    This function is for reading files from S3 bucket. If the file path is not known, we try to help you get the file.
    :param (str) file_path - file path
    :param (str) bucket_name - the name of the bucket we want to read from
    """
    # call the connect function to connect to the resource 
    s3 = self.connect()
    
    
    try:      
      # fetch the object
      obj = s3.Bucket(bucket_name).Object(file_path).get()
      
      # determine the file type
      file_type = file_path.split('.')[-1]
      
      if file_type == 'csv':
        # read the file into a dataframe
        obj_df = pd.read_csv(obj['Body'], **kwargs)

      if file_type == 'xlsx':
        obj_df = pd.read_excel(obj['Body'], **kwargs)
      
      if status_print == True:
        print(f'{file_path} file read successfully')
      
      return obj_df
    except Exception as e:
      
#       print(e.response['Error'])
      
      if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
        
        if e.response['Error']['Code'] == 'NoSuchBucket':
          print("bucket doesn't exist! Here is a list of the buckets:")
          print('---------------------------------------------------')
          self.list_all_buckets()
          
        elif e.response['Error']['Code'] == 'NoSuchKey':
          print("invalid S3 bucket file path!")
        
      else:
        raise
        
  def bucket_create(self, bucket_name):
    """
    This function creates a bucket. 
    :param (str) bucket_name, the name of the bucket to be created. 
    """
    # call the connect function to connect to the resource 
    s3 = self.connect()

    # create a list with the current bucket 
    try:
#       s3.create_bucket(Bucket=bucket_name,)
      s3.create_bucket(
        Bucket=bucket_name, 
        
        # the default location is the US, we have to specify the location to Europe
        CreateBucketConfiguration={'LocationConstraint': "eu-west-2"}
      ) 
      
      # confirm bucket was successfully created
      if bucket_name in s3.buckets.all():
        print('Great! bucket:',bucket_name,'successfully created')
        
    except Exception as e:
      print(e.response['Error']['Code'])
      
  def file_upload(self, bucket_name, s3_path, df=None, local_path='',delete_local=True):
    """
    Uploads the specified file to S3 bucket using the key provided, i.e., s3_path
    :param (str) bucket_name
    :param (dataframe) df, dataframe to be converted to csv and uploaded to the s3 path.
    :param (str) local_path, if not specified, dataframe will be uploaded.
    :param (str) s3_path, INCLUDING THE FILENAME!
    """
    # call the connect function to connect to the resource
    s3 = self.connect()

    if local_path == '':
      filename = s3_path.split('/')[-1]
      local_path = str(os.getcwd()) + filename
      df.to_csv(local_path)
    s3.Bucket(bucket_name).upload_file(local_path, s3_path)
    if delete_local:
      os.remove(local_path)
    else:
      pass # want to keep the file for some reason!
      
      
  def list_keys(self, bucket_name,prefix='',suffix=''):
    """
    list all objcts in the bucket with the specified suffix and/or prefix
    :param (str) bucket_name
    :param (str) prefix, if not specified, read all objects. if  specified, reads only object starting with prefix 
    :param (str) suffix, same as prefix except this is for ending with
    :return list of keys i.e., object names.
    """
    # call the connect function to connect to the resource
    s3 = self.connect()
    
    # read the bucket
    my_bucket = s3.Bucket(bucket_name)
    
    # initialize the list of keys to be returned
    keys_list = []
    
    # read the keys. use file.Objects() to get more information about the object
    for file in my_bucket.objects.all(): 
      
        # filter the objects to include only objects with suffix and prefix specified. 
        if file.key.startswith(prefix) and file.key.endswith(suffix):
          keys_list.append(file.key)
    
    return keys_list
  
  def delete_objects(self, bucket_name, objs_to_del=[]):
    """
    iteratively delete the objects
    :param (str) bucket_name, name of the bucket 
    :param (list) objs_to_del, objects to delete
    """
    # call the connect function to connect to the resource
    s3 = self.connect()
    
    for obj in objs_to_del:
      
      try:
        s3.Object(bucket_name, obj).delete()
        
      except Exception as ex:
        print('could not delete:',obj)
        print(str(ex))
    
  def delete_s3_bucket(self,buckets = []):
  
    assert isinstance(buckets, (list)), 'Buckets must be a list!'
    
    # call the connect function to connect to the resource
    s3 = self.connect()

    for bucket_name in buckets:
      # delete the bucket 
      try:
        s3.Bucket(bucket_name).delete()
      except Exception as e:
        print(e.response['Error']['Code'])
    
if __name__ == '__main__':
    s3 = S3_class()
    print(s3)

      


# In[ ]:




