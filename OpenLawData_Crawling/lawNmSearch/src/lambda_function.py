#-- coding:utf-8 --
import os
import json
import boto3
from src.config import Config
from src.modules.LawListSearch import LawListSearch

# Get Environment Variables & Parameters defined by src.config.py
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_S3_KEY_PATH = os.getenv('AWS_S3_KEY_PATH')
LAW_LIST_SEARCH = Config.LAW_LIST_SEARCH
REQUEST_PARSER = Config.REQUEST_PARSER

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
s3 = session.resource('s3')

def lambda_handler(event, context):
    lawListSearch = LawListSearch(**LAW_LIST_SEARCH)
    uri = lawListSearch.updateURIstring()
    lawResult = lawListSearch.xmlToDict(uri, REQUEST_PARSER)
    lawListSearch.getTotalItemPageNum(lawResult)
    lawNmList = lawListSearch.getLawList(REQUEST_PARSER)
    lawListSearch.saveLawListToS3(lawNmList, s3, AWS_S3_BUCKET_NAME, AWS_S3_KEY_PATH)
