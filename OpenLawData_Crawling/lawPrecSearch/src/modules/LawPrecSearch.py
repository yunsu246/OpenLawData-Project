#-- coding:utf-8 --
import os
import io
import re
import json
import time
import socket
import requests
import xmltodict
from datetime import datetime
from math import ceil
from random import randint
from xml.parsers.expat import ExpatError
from modules.requests_parser import LSOIpController

socket.create_connection(('open.law.go.kr', 80), timeout=2)

class LawPrecSearch():
    def __init__(self, headers, OC, target, Type, page, display, sort, PrecSearch, PrecService, totalPrecCnt, updatePrecCnt):
        self.headers = headers
        self.OC = OC
        self.target = target
        self.Type = Type
        self.page = page
        self.sort = sort
        self.display = display
        self.PrecSearch = PrecSearch
        self.PrecService = PrecService
        self.totalPrecCnt = totalPrecCnt
        self.updatePrecCnt = updatePrecCnt
        self.PrecSearchURI = None
        self.PrecServiceURI = None
        self.total_item_num = None
        self.total_page_num = None

    def updatePrecSearchURI(self):
        params = {
            "OC": self.OC,
            "target": self.target,
            "Type": self.Type,
            "page": self.page,
            "display": self.display,
            "sort": self.sort
        }
        PrecSearchURI = 'http://www.law.go.kr/DRF/lawSearch.do?OC={OC}&target={target}&type={Type}&page={page}&display={display}&sort={sort}'.format(**params)
        self.PrecSearchURI = PrecSearchURI
        return PrecSearchURI

    def updatePrecServiceURI(self, precID):
        params = {
            "OC": self.OC,
            "target": self.target,
            "Type": self.Type
        }
        PrecServiceURI = 'http://www.law.go.kr/DRF/lawService.do?OC={OC}&target={target}&type={Type}&ID={precID}'.format(**params, precID=precID)
        self.PrecServiceURI = PrecServiceURI
        return PrecServiceURI
        
    def xmlToDict(self, uri, searchType, REQUEST_PARSER_CONFIG):
        req = requests.get(uri, headers=self.headers)
        OrderedDict = xmltodict.parse(req.text)
        strDict = json.dumps(OrderedDict, ensure_ascii=False)
        LawResult = json.loads(strDict)

        if LawResult.get('html', {}).get('body', {}).get('table', {}).get('caption', None) == '미등록 IP 접근 제한 레이아웃':
            print(
                '\n-> KeyError:', searchType,
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
        if LawResult.get(searchType, None) != None:
            LawSearch = LawResult[searchType]
        elif LawResult.get('html', {}).get('head', {}).get('title', None) == '국가법령정보센터 | 오류페이지':
            LawSearch = {key: "None" for key in self.updatePrecCnt}
        elif LawResult.get('Law', None) != None:
            LawSearch = {key: "None" for key in self.updatePrecCnt}

        return LawSearch
    
    def getTotalItemPageNum(self, data):
        total_item_num = data["totalCnt"]
        total_page_num = ceil(int(total_item_num) / self.display)
        self.total_item_num = int(total_item_num)
        self.total_page_num = int(total_page_num)
        return total_page_num, total_item_num

    def savePrecListToS3(self, data, s3, bucket_name, key_path, page_num):
        today = datetime.today().strftime('%Y%m%d')
        Key = os.path.join(key_path, today,'precNmList_{page_num:03d}_{today}.json'.format(page_num=page_num, today=today))
        Body = bytes(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        bucket = s3.Bucket(bucket_name)
        bucket.put_object(
            ACL='private',
            ContentType='application/json',
            Key=Key,
            Body=Body
        )

    def getPrecList(self, s3, bucket_name, key_path, REQUEST_PARSER_CONFIG):
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
        
        totalPrecList = (self.page -1) * 100
        for page_num in range(self.page, total_page_num + 1):
            self.page = page_num
            self.updatePrecSearchURI()

            try:
                PrecList = self.xmlToDict(self.PrecSearchURI, self.PrecSearch, REQUEST_PARSER_CONFIG)[self.target]

                for j, Nm in enumerate(PrecList):
                    count = totalPrecList + j+1
                    precID = Nm["판례일련번호"]
                    self.updatePrecServiceURI(precID)
                    print('{} th {}: {}'.format(count, self.PrecService, self.PrecServiceURI))
                    Cnt = self.xmlToDict(self.PrecServiceURI, self.PrecService, REQUEST_PARSER_CONFIG)
                    for key in self.updatePrecCnt:
                        PrecList[j][key] = Cnt[key]
                    time.sleep(randint(2,3))
            
            except ExpatError as e:
                print('\n'+ '-> ExpatError:', e)
                req = requests.get(self.updatePrecSearchURI()) 
                p = re.compile(r'<판례일련번호>(.*?)</판례일련번호>')
                precIdList = p.findall(req.text)
                precIdDict = {i+1: Id for i, Id in enumerate(precIdList) if Id != '0'}
                PrecList = []

                for j, precID in precIdDict.items():
                    count = totalPrecList + j
                    self.updatePrecServiceURI(precID)
                    print('{} th {}: {}'.format(count, self.PrecService, self.PrecServiceURI))
                    Cnt = self.xmlToDict(self.PrecServiceURI, self.PrecService, REQUEST_PARSER_CONFIG)
                    date = Cnt["선고일자"]
                    Cnt["@id"] = j
                    Cnt["판례상세링크"] = '/DRF/lawService.do?OC={OC}&target={target}&ID={precID}&type=HTML&mobileYn='.format(OC=self.OC, target=self.target, precID=precID)
                    Cnt["판례일련번호"] = Cnt.pop("판례정보일련번호")
                    Cnt["선고일자"] = '{}.{}.{}'.format(date[:4], date[4:-2], date[-2:])
                    PrecList.append(Cnt)
                    time.sleep(randint(2,3))

            totalPrecList += len(PrecList)
            self.savePrecListToS3(PrecList, s3, bucket_name, key_path, page_num)
        
        t_end = time.time()
        m, s = divmod(t_end-t_start, 60)
        h, m = divmod(m, 60)
        print(
            '\n'+ '-'*50,
            '\nEnd :', datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            '\nDuration : %02d:%02d:%02d' % (h, m, s),
            '\nTotal {} Items :'.format(self.PrecService), totalPrecList,
            '\nVerification of Total Item Number :', totalPrecList == total_item_num,
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
