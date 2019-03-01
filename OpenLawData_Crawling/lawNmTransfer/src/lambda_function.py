#-- coding:utf-8 --
import os
import boto3
from src.config import Config

# Get Environment Variables & Parameters defined by src.config.py
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Create ECS Client
ecs = session.client('ecs')

def lambda_handler(event, context):
    s3_trigger_bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3_trigger_object_key = event['Records'][0]['s3']['object']['key']
    print(f's3_trigger_bucket_name: {s3_trigger_bucket_name}')
    print(f's3_trigger_object_key: {s3_trigger_object_key}')
    
    response = ecs.run_task(
        cluster='default', # name of the cluster
        launchType = 'FARGATE',
        taskDefinition='openlawdata-datapipeline-lawcontentsearch:1', # replace with your task definition name and revision
        overrides={
            'containerOverrides': [
                {
                    'name': 'openlawdata-datapipeline-lawcontentsearch',
                    'environment': [
                        {
                            'name': 's3_trigger_bucket_name',
                            'value': s3_trigger_bucket_name
                        },
                        {
                            'name': 's3_trigger_object_key',
                            'value': s3_trigger_object_key
                        }
                    ],
                },
            ],
        },
        count = 1,
        platformVersion='LATEST',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    'subnet-05d5a55adb971a3bd', # replace with your public subnet or a private with NAT
                    'subnet-0d9cd8168feb42a79' # Second is optional, but good idea to have two
                ],
            'assignPublicIp': 'ENABLED'
            }
        }
    )
    print(response)
    
    return str(response)
