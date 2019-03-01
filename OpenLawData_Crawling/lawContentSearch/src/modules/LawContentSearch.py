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
from modules.requests_parser import LSOIpController

socket.create_connection(('open.law.go.kr', 80), timeout=2)

class LawContentSearch():
    def __init__(self, headers, OC, target, Type):
        self.headers = headers
        self.OC = OC
        self.target = target
        self.Type = Type
        self.lawID = None
        self.uri = None

    def updateURIstring(self):
        params = {
            "OC": self.OC,
            "target": self.target,
            "Type": self.Type,
            "lawID": self.lawID
        }
        uri = 'http://www.law.go.kr/DRF/lawService.do?OC={OC}&target={target}&type={Type}&ID={lawID}'.format(**params)
        self.uri = uri
        return uri         
        
    def xmlToDict(self, uri, REQUEST_PARSER_CONFIG):
        req = requests.get(uri, headers=self.headers)
        OrderedDict = xmltodict.parse(req.text)
        strDict = json.dumps(OrderedDict, ensure_ascii=False)
        LawContent = json.loads(strDict)
        
        if LawContent.get('html', {}).get('body', {}).get('table', {}).get('caption', None) == '미등록 IP 접근 제한 레이아웃':
            print(
                '\n-> KeyError:', '법령',
                '\n-> Reason:', LawContent.get('html', {}).get('body', {}).get('table', {}).get('caption', None) +'\n',
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
            LawContent = json.loads(strDict)
        
        lawID = LawContent["법령"]["기본정보"]["법령ID"]
        print(f'lawID: {lawID} Successfully Convert xml To dict!')
        return LawContent
    
    def saveLawContentToS3(self, data, s3, bucket_name, key_path):
        lawID = data["법령"]["기본정보"]["법령ID"]
        today = datetime.today().strftime('%Y%m%d')
        Key = os.path.join(key_path, today, f'{key_path}_{lawID}_{today}.json')
        Body = bytes(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        bucket = s3.Bucket(bucket_name)
        bucket.put_object(
            ACL='private',
            ContentType='application/json',
            Key=Key,
            Body=Body
        )

    def getLawContent(self, lawIDs, s3, bucket_name, key_path, REQUEST_PARSER_CONFIG):
        t_start = time.time()
        print(
            '-'*50,
            '\nStart :', datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            '\n'+ '-'*50 +'\n'
        )

        for i, Id in enumerate(lawIDs):
            self.lawID = Id
            self.updateURIstring()
            print('{} th lawID {}: {}'.format(i+1, self.lawID, self.uri))
            lawContent = self.xmlToDict(self.uri, REQUEST_PARSER_CONFIG)
            self.saveLawContentToS3(lawContent, s3, bucket_name, key_path)
            time.sleep(randint(2,6))

        t_end = time.time()
        m, s = divmod(t_end-t_start, 60)
        h, m = divmod(m, 60)
        print(
            '\n'+ '-'*50,
            '\nEnd :', datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
            '\nDuration : %02d:%02d:%02d' % (h, m, s),
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
        