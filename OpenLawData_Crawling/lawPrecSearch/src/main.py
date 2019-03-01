#-- coding:utf-8 --
import os
import json
import boto3
from modules.LawPrecSearch import LawPrecSearch
from config import Config

# Get Environment Variables & Parameters defined by src.config.py
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_S3_KEY_PATH = os.getenv('AWS_S3_KEY_PATH')
LAW_PREC_SEARCH = Config.LAW_PREC_SEARCH
REQUEST_PARSER = Config.REQUEST_PARSER

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
s3 = session.resource('s3')

if __name__ == "__main__":
    lawPrecSearch = LawPrecSearch(**LAW_PREC_SEARCH)
    uri = lawPrecSearch.updatePrecSearchURI()
    lawResult = lawPrecSearch.xmlToDict(uri, LAW_PREC_SEARCH['PrecSearch'], REQUEST_PARSER)
    lawPrecSearch.getTotalItemPageNum(lawResult)
    lawPrecSearch.getPrecList(s3, AWS_S3_BUCKET_NAME, AWS_S3_KEY_PATH, REQUEST_PARSER)
