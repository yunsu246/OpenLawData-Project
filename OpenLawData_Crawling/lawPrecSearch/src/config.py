import os


class Config(object):

    # ---------------------[ Custom Environment Variables in src.main.py ]----------------------
    # Required Environment Variables for AWS Resources Access
    os.environ['AWS_ACCESS_KEY_ID'] = 'AWS_ACCESS_KEY_ID'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'AWS_SECRET_ACCESS_KEY'

    # Remote(Custom) Environment Variables
    os.environ['AWS_S3_BUCKET_NAME'] = 'AWS_S3_BUCKET_NAME'
    os.environ['AWS_S3_KEY_PATH'] = 'precCnt'
    # ------------------------------------------------------------------------------------------
    

    # ------------------[ Custom Parameters in src.modules.LawPrecSearch.py ]-------------------
    LAW_PREC_SEARCH = {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36",
            "Content-Type": "application/json; charset=utf-8"
        },
        "OC": "사용자 이메일의 ID(g4c@korea.kr일경우 OC값=g4c)",
        "target": "prec",
        "Type": "XML",
        "display": 100,
        "sort": "lasc",
        "page": 1,
        "PrecSearch": "PrecSearch",
        "PrecService": "PrecService",
        "totalPrecCnt": ["@id", "판례일련번호", "사건명", "사건번호", "선고일자", "법원명", "법원종류코드", "사건종류명", "사건종류코드", "판결유형", "선고", "판례상세링크", "참조조문", "참조판례", "판결요지", "판례내용", "판시사항"],
        "updatePrecCnt": ["법원종류코드","사건종류코드","참조조문","참조판례","판결요지","판결유형","판례내용","판시사항"]
    }
    # ------------------------------------------------------------------------------------------


    # -----------------[ Custom Parameters in src.modules.request_parser.py ]-------------------
    REQUEST_PARSER = {
        "HOST": "http://open.law.go.kr",
        "HEADERS": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36",
            "Content-Type": "application/json; charset=utf-8"
        },
        "HREF": {
            "login": "LSO/login.do",
            "cuAskList": "LSO/openApi/cuAskList.do"
        },
        "LOGIN_DATA": {
            "usrId": "사용자 ID(이메일, g4c@korea.kr) ",
            "pw": "사용자 비밀번호"
        },
        "CONTENTS": {
            "mobileYn": "Y",
            "internetYn": "Y",
            "srvYn": "Y",
            "srvAplYn": "Y",
            "orgNm": "기관명",
            "odUsrNm": "신청자명",
            "telNo": "전화번호",
            "stmNm": "시스템/홈페이지명",
            "stmUrl": "도메인주소(url)",
            "devMonth": "구축기간(개월)",
            "devNum": "투입인력(명)",
            "purpose": "국가법령정보 활용 목적, 적용 분야 또는 사업 모델"
        }        
    }
    # ------------------------------------------------------------------------------------------