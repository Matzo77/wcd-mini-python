import requests
import boto3
import pandas as pd
import toml
from dotenv import load_dotenv
import os
from botocore.exceptions import NoCredentialsError

# Load the environment variables to .env file
load_dotenv();

def load_config(path='config.toml'):
    """"Loading configuration from .toml file"""
    with open(path,"r") as config_file:
        config = toml.load(config_file)
    return config

def read_url(api_url):
    """read the api response"""
    response = requests.get(api_url)
    print(response.status_code)
    return response.json()

def upload_to_s3(file_name,object_name=None):
    """Uploading files to S3 bucket"""

    #If S3 object name is not specified
    if object_name is None:
        object_name=file_name

    #Get all config and env variables
    accesskey=os.getenv('accesskey')
    accesssecret=os.getenv('accesssecret')
    bucket_name=config["s3"]["bucket_name"]
    region=config["s3"]["region_name"]

    #Initialize session with S3 and Boto3 session
    session = boto3.session.Session(
        aws_access_key_id=accesskey,
        aws_secret_access_key=accesssecret,
        region_name=region)
    
    s3_client=session.client('s3')

    try:
        response=s3_client.upload_file(file_name,bucket_name,object_name)
        return True
    except NoCredentialsError:
        print('Credentials not available')
        return False

def main():
    #Main function
    api_url = config["api"]["api_url"]
    json_data = read_url(api_url)['results']

    #Creating the data frame using json_normalize
    df = pd.json_normalize(json_data)

    #Transformatio steps

    #Creating lists for city and state/country using the locations
    city_list = [[location['name'].split(',')[0].strip() for location in d['locations']] for d in json_data]
    state_list = [[location['name'].split(',')[1].strip() for location in d['locations']] for d in json_data]
    df['city'] = city_list
    df['state/country'] = state_list

    #Cutting the date string...
    df['publication_date'] = df['publication_date'].apply(lambda x: x.split('T')[0])

    #...and converting it to datetime
    df['publication_date'] = pd.to_datetime(df['publication_date'])

    #Filtering and renaming the columns that we need
    df_filtered = df[['publication_date','type','name','company.name','city','state/country']].rename(columns={
    'type':'job_type',
    'name':'job',
    'company.name':'company',})

    #Since some job postings have multiple locations we will use .explode to show on location per each row
    df_exploded = df_filtered.explode(['city','state/country'],ignore_index=True)
    print(df_exploded.head())

    #Saving to csv file
    df_exploded.to_csv("py_muse.csv", index=False)

################## End of Function Declarations #####################

#Loading config file
config = load_config()

if __name__ == "__main__":
    main()

file_name = 'py_muse.csv'
object_name = None
upload_success = upload_to_s3(file_name,object_name)
if upload_success:
    print('Upload was successful!')
else:
    print('Upload failed!!!')