## Tree
```bash
lawNmTransfer
    ├── src
    │     ├── lambda_function.py: AWS lambda 실행 스크립트, event 전달자 역할
    │     └── config.py: configure 모음
    │
    ├── Pipfile: pipenv를 사용한 Python virtualenv & 라이브러리 의존성 관리(for Deployment)
    └── zappa_settings.json: zappa deploy & zappa update 시 필요한 settings(for Deployment)
```

## Configures (./src/config.py)

* Required Environment Variables for AWS Resources Access
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY

## Deployment Settings (./zappa_settings.json)

* OPTIONAL, otherwise start with `zappa init`
* dev
    - events: receive `events` as a trigger when object is created at the target S3 bucket. 
    - s3_bucket: Pre-created s3 bucket for deploying application from s3 bucket to AWS Lambda.

## Deployment

``` bash
# install dependencies
pipenv install

# start virtual environment mode
pipenv shell

# deploy application
zappa deploy

# update deployed application
zappa update
```