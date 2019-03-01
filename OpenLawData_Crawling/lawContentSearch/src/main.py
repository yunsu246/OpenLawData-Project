#-- coding:utf-8 --
import os
import json
import time
import boto3
import socket
import pandas as pd
from random import randint
from datetime import datetime
from modules.LawContentSearch import LawContentSearch
from config import Config

# Get Environment Variables & Parameters defined by src.config.py
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_S3_KEY_PATH = os.getenv('AWS_S3_KEY_PATH')
LAW_CONTENT_SEARCH = Config.LAW_CONTENT_SEARCH
REQUEST_PARSER = Config.REQUEST_PARSER

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
s3 = session.resource('s3')

s3_trigger_bucket_name = os.environ['s3_trigger_bucket_name']
s3_trigger_object_key = os.environ['s3_trigger_object_key']
content_object = s3.Object(s3_trigger_bucket_name, s3_trigger_object_key)
file_content = content_object.get()['Body'].read().decode('utf-8')
json_content = json.loads(file_content)

lawCategory = LAW_CONTENT_SEARCH["lawCategory"]
df = pd.DataFrame(json_content)
df = df.loc[df['법령구분명'].isin(lawCategory), '법령ID'].reset_index(drop=True)
lawIDs = df.values

if __name__ == "__main__":
    lawContentSearch = LawContentSearch(**LAW_CONTENT_SEARCH['LawContentSearch'])
    lawContentSearch.getLawContent(lawIDs, s3, AWS_S3_BUCKET_NAME, AWS_S3_KEY_PATH, REQUEST_PARSER)