#-- coding:utf-8 --
import os
import io
import json
import time
import socket
import requests
import xmltodict
from datetime import datetime
from math import ceil
from random import randint
from src.modules.requests_parser import LSOIpController

socket.create_connection(('open.law.go.kr', 80), timeout=2)

class LawListSearch():
    def __init__(self, headers, OC, target, Type, page, display, sort, searchType, updateLawNm):
        self.headers = headers
        self.OC = OC
        self.target = target
        self.Type = Type
        self.page = page
        self.sort = sort
        self.display = display
        self.searchType = searchType
        self.updateLawNm = updateLawNm
        self.uri = None
        self.total_item_num = None
        self.total_page_num = None

    def updateURIstring(self):
        params = {
            "OC": self.OC,
            "target": self.target,
            "Type": self.Type,
            "page": self.page,
            "display": self.display,
            "sort": self.sort
        }
        uri = 'http://www.law.go.kr/DRF/lawSearch.do?OC={OC}&target={target}&type={Type}&page={page}&display={display}&sort={sort}'.format(**params)
        self.uri = uri
        return uri
        
    def xmlToDict(self, uri, REQUEST_PARSER_CONFIG):
        req = requests.get(uri, headers=self.headers)
        OrderedDict = xmltodict.parse(req.text)
        strDict = json.dumps(OrderedDict, ensure_ascii=False)
        LawResult = json.loads(strDict)

        if LawResult.get('html', {}).get('body', {}).get('table', {}).get('caption', None) == '미등록 IP 접근 제한 레이아웃':
            print(
                '\n-> KeyError:', self.searchType,
                '\n-> Reason:', LawResult.get('html', {}).get('body', {}).get('table', {}).get('caption', None) +'\n',
                '\n'+ '-'*50,
                '\nUpdate selIP in putCuAskUpdate to Current IP',
                '\n'+ '-'*50 +'\n'
            )

            host = REQUEST_PARSER_CONFIG['HOST']
            headers = REQUEST_PARSER_CONFIG['HEADERS']
            href = REQUEST_PARSER_CONFIG['HREF']
            login_data = REQUEST_PARSER_CONFIG['LOGIN_DATA']
            contents = REQUEST_PARSER_CONFIG['CONTENTS']

            parser = LSOIpController(host, headers)
            parser.logIn(href, login_data)
            value = parser.getCuAskItem(href)
            parser.putCuAskUpdate(value, contents, 'appendSelIp')
            parser.logOut()
            parser.close()
            print('\n-> CONTINUE Convert xml To dict...' +'\n')
            
            req = requests.get(uri, headers=self.headers)
            OrderedDict = xmltodict.parse(req.text)
            strDict = json.dumps(OrderedDict, ensure_ascii=False)
            LawResult = json.loads(strDict)
        
        LawSearch = None
        
        if LawResult.get(self.searchType, None) != None:
            LawSearch = LawResult[self.searchType]
        elif LawResult.get('html', {}).get('head', {}).get('title', None) == '국가법령정보센터 | 오류페이지':
            LawSearch = {key: "None" for key in self.updateLawNm}
        elif LawResult.get('Law', None) != None:
            LawSearch = {key: "None" for key in self.updateLawNm}

        return LawSearch
    
    def getTotalItemPageNum(self, data):
        total_item_num = data["totalCnt"]
        total_page_num = ceil(int(total_item_num) / self.display)
        self.total_item_num = int(total_item_num)
        self.total_page_num = int(total_page_num)
        return total_page_num, total_item_num
    
    def getLawList(self, REQUEST_PARSER_CONFIG):
        total_item_num = self.total_item_num
        total_page_num = self.total_page_num
        
        t_start = time.time()
        print(
            '-'*50,
            '\nStart :', datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            '\nTotal Item Number :', total_item_num,
            '\nTotal Page Number :', total_page_num,
            '\n'+ '-'*50 +'\n'
        )
        
        LawList = []
        for page_num in range(self.page, total_page_num + 1):
            self.page = page_num
            self.updateURIstring()
            print('{} th {}: {}'.format(page_num, self.searchType, self.uri))
            result = self.xmlToDict(self.uri, REQUEST_PARSER_CONFIG)
            LawList += result[self.target]
            time.sleep(randint(2,3))
        
        t_end = time.time()
        m, s = divmod(t_end-t_start, 60)
        h, m = divmod(m, 60)
        print(
            '\n'+ '-'*50,
            '\nEnd :', datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            '\nDuration : %02d:%02d:%02d' % (h, m, s),
            '\nTotal {} Items :'.format(self.searchType), len(LawList),
            '\nVerification of Total Item Number :', len(LawList) == total_item_num,
            '\n'+ '-'*50
        )
        
        print(
            '\n'+ '-'*50,
            '\nRemove Registered Current IP in CuAskUpdate.selIp',
            '\n'+ '-'*50 +'\n'
        )

        host = REQUEST_PARSER_CONFIG['HOST']
        headers = REQUEST_PARSER_CONFIG['HEADERS']
        href = REQUEST_PARSER_CONFIG['HREF']
        login_data = REQUEST_PARSER_CONFIG['LOGIN_DATA']
        contents = REQUEST_PARSER_CONFIG['CONTENTS']

        parser = LSOIpController(host, headers)
        parser.logIn(href, login_data)
        value = parser.getCuAskItem(href)
        parser.putCuAskUpdate(value, contents, 'removeSelIp')
        parser.logOut()
        parser.close()

        return LawList

    def saveLawListToS3(self, data, s3, bucket_name, key_path):
        today = datetime.today().strftime('%Y%m%d')
        Key = os.path.join(key_path, 'LawNmList_{today}.json'.format(today=today))
        Body = bytes(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        bucket = s3.Bucket(bucket_name)
        bucket.put_object(
            ACL='private',
            ContentType='application/json',
            Key=Key,
            Body=Body
        )

    def saveLawNmListToJson(self, data, path):
        with io.open(path, 'w', encoding='utf8') as json_file:
            json.dump(data, json_file, ensure_ascii=False)