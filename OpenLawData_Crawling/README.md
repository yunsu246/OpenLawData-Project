# OpenLawData-Crawling

## 개요
* [국가법령정보 공동활용 OPEN API](http://open.law.go.kr/LSO/main.do "OPEN API 주소")로부터 법령/판례 등의 Raw Data를 조회/저장하기 위한 코드 입니다.

## API 구조
* 조건: 회원가입 및 [OPEN API 신청](http://open.law.go.kr/LSO/openApi/guideList.do "OPEN API 신청")을 통해 서버의 IP 주소를 등록하고나서 관리자의 승인을 받은 후에야 사용 가능
* 목록 및 REQUEST/RESPONSE 가이드: [OPEN API 활용가이드](http://open.law.go.kr/LSO/openApi/guideList.do "OPEN API 활용가이드") 참조

## 구분 및 기능
* [lawNmSearch](https://github.com/yunsu246/OpenLawData-Project/tree/master/OpenLawData_Crawling/lawNmSearch "lawNmSearch"): `법령 > 본문 > 현행법령 목록`을 조회하여 저장
* [lawNmTransfer](https://github.com/yunsu246/OpenLawData-Project/tree/master/OpenLawData_Crawling/lawNmTransfer "lawNmTransfer"): `법령 > 본문 > 현행법령 목록`이 저장될 때의 `event`를 `lawContentSearch`로 전달
* [lawContentSearch](https://github.com/yunsu246/OpenLawData-Project/tree/master/OpenLawData_Crawling/lawContentSearch "lawContentSearch"): `lawNmTransfer`로부터 `법령 > 본문 > 현행법령 목록`이 저장될 때를 `event`로 받아와 `법령 > 본문 > 현행법령 본문`을 조회하여 저장
* [lawPreSearch](https://github.com/yunsu246/OpenLawData-Project/tree/master/OpenLawData_Crawling/lawPreSearch "lawPreSearch"): `판례 > 본문 > 판례 목록`을 확인하고 `판례 > 본문 > 판례 본문`을 조회하여 저장

## 주요 리소스 및 아키텍쳐
* Serverless: AWS(S3, ECS(Fargate), Lambda)
* Crawler: Python
* TEST environment: docker, lambdaCI([docker-lambda](https://github.com/lambci/docker-lambda "docker-lambda"))
* CI/CD: aws-cli, zappa

* Diagram
    - 준비중