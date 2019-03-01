import os


class Config(object):

    # ----------------[ Custom Environment Variables in src.lambda_function.py ]----------------
    # Required Environment Variables for AWS Resources Access
    os.environ['AWS_ACCESS_KEY_ID'] = 'AWS_ACCESS_KEY_ID'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'AWS_SECRET_ACCESS_KEY'
    # ------------------------------------------------------------------------------------------