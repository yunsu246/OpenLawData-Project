## Tree
```bash
lawContentSearch
    ├── lib: 설치된 Python 라이브러리 저장소
    ├── src
    │     ├── main.py: 크롤러 실행 스크립트
    │     ├── config.py: configure 모음
    │     └── modules: 크롤러 실행을 위한 모듈 모음
    │              ├── LawContentSearch.py: OPEN API 호출 결과 조회/저장 등 크롤링 프로세스 관리
    │              └── requests_parser.py: OPEN API 호출(request) 프로세스 관리
    │
    ├── Dockerfile: Docker image(구성) 정의
    ├── requirements.txt: Python 라이브러리 관리
    └── Makefile: Local Development & Deployment 명령어 관리
```

## Configures (./src/config.py)

* Required Environment Variables for AWS Resources Access
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY

* Remote(Custom) Environment Variables
    - AWS_S3_BUCKET_NAME: 파일을 저장할 S3 Bucket 이름
    - AWS_S3_KEY_PATH: S3 Bucket 내 파일의 경로

* Custom Parameters
    * LAW_CONTENT_SEARCH 
        - OC: 사용자 이메일의 ID(g4c@korea.kr일경우 OC값=g4c)

    * REQUEST_PARSER
        * LOGIN_DATA
            - usrId: 사용자 ID(이메일, g4c@korea.kr) 
            - pw: 사용자 비밀번호

        * CONTENTS
            - orgNm: 기관명
            - odUsrNm: 신청자명
            - telNo: 전화번호
            - stmNm: 시스템/홈페이지명
            - stmUrl: 도메인주소(url)
            - devMonth: 구축기간(개월)
            - devNum: 투입인력(명)
            - purpose: 국가법령정보 활용 목적, 적용 분야 또는 사업 모델

## Local Development Env Setup & Deployment

```bash
# clear up caches
make clean

# build docker image
make docker-build

# run docker container
make docker-run

# push docker image to AWS ECR registry
make docker-push
```