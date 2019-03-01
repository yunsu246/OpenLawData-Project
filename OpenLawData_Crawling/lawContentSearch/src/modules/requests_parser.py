#-- coding:utf-8 --
import socket
import requests
from bs4 import BeautifulSoup as bs

requests.packages.urllib3.disable_warnings()
socket.create_connection(('open.law.go.kr', 80), timeout=2)

class LSOIpController():
    def __init__(self, host, headers, session=requests.Session(), ip=requests.get('https://api.ipify.org').text):
        self.host = host
        self.headers = headers
        self.session = session
        self.ip = ip
    
    def logIn(self, href, data):
        url = '{host}/{login}?ReURI={cuAskList}'.format(host=self.host, **href)
        print('[GET] {url}'.format(url=url))
        req = self.session.get(url, headers=self.headers, verify=False)
        html = req.text
        soup = bs(html, 'html.parser')
        hidden = soup.find('input', {'name': 'ReURI'})
        print('\tReURI:', hidden['value'])

        # SKIP: Unpacking dictionary FOR requests.post data
        # LOGIN_INFO = {**login_data, **{csrf: hidden['value']}}
        # print(LOGIN_INFO)
        
        url = '{host}/LSO/execLogin.do?usrId={usrId}&pw={pw}'.format(host=self.host, **data)
        print('[POST] {url}'.format(url=url.split('?')[0]))
        resp = self.session.post(url, headers=self.headers, verify=False) # SKIP: data=LOGIN_INFO
        print('\tLOGIN_STATUS:', resp.status_code)
        # print('\tLOGIN_RESULT:', resp.text)
        if resp.status_code != 200:
            raise Exception('LOGIN FAILED. CHECK usrId & pw AGAIN')
            
    def getCuAskItem(self, href):
        url = '{host}/{cuAskList}'.format(host=self.host, cuAskList=href['cuAskList'])
        print('[GET] {url}'.format(url=url))
        req = self.session.get(url, headers=self.headers, verify=False)
        html = req.text
        soup = bs(html, 'html.parser')
        cuAskItem = soup.find('input', {'name': 'chk'})['value']
        # print('\tn_chk_VALUE:', cuAskItem)
        return cuAskItem

    def selIpEditor(self, soup, operator):
        return {
            'appendSelIp': lambda: self.appendSelIp(soup),
            'removeSelIp': lambda: self.removeSelIp(soup)
        }.get(operator, lambda: None)()
    
    def appendSelIp(self, soup):
        current_ip = [self.ip]
        previous_ip = [child['value'] for child in soup.find('select', {'name':'selIp'}).children if child != ' ']
        ipList = list(filter(lambda x: x != '', set(previous_ip) | set(current_ip)))
        print('\tPREVIOUS_IP:', previous_ip)
        print('\tCURRENT_IP:', current_ip)
        print('\tipList:', ipList)
        return ipList
        
    def removeSelIp(self, soup):
        current_ip = [self.ip]
        previous_ip = [child['value'] for child in soup.find('select', {'name':'selIp'}).children if child != ' ']
        ipList = list(filter(lambda x: x != '', set(previous_ip) - set(current_ip)))
        print('\tPREVIOUS_IP:', previous_ip)
        print('\tCURRENT_IP:', current_ip)
        print('\tipList:', ipList)
        return ipList

    def putCuAskUpdate(self, value, contents, operator):
        url = '{host}/LSO/openApi/cuAskUpdate.do?n_chk={value}'.format(host=self.host, value=value)
        print('[GET] {url}'.format(url=url))
        req = self.session.get(url, headers=self.headers, verify=False)
        html = req.text
        soup = bs(html, 'html.parser')
        
        ipList = self.selIpEditor(soup, operator)
        
        srvType = {'List':[], 'Cnt':[]}
        for param in soup.findAll('input'):
            if param['name'] == 'chListType':
                srvType['List'].append(param)
            elif param['name'] == 'chCntType':
                srvType['Cnt'].append(param)
            else:
                pass

        LenList, LenCnt = len({Cnt['id'][:-1] for Cnt in srvType['Cnt']}), len({List['id'][:-1] for List in srvType['List']})
        srvListHtmlYn = ','.join(['3']*LenList)
        srvCntHtmlYn = ','.join(['3']*LenCnt)

        form = {
            "ipList": '/'.join(ipList),
            "maxIndex": soup.find('input', {'name':'maxIndex'})['value'],
            "srvNw": soup.find('input', {'name':'srvNw'})['value'],
            "srvListType": soup.find('input', {'name':'srvListType'})['value'],
            "srvCntType": soup.find('input', {'name':'srvCntType'})['value'],
            "srvType": soup.find('input', {'name':'srvType'})['value'],
            "srvListHtmlYn": srvListHtmlYn,
            "srvCntHtmlYn": srvCntHtmlYn,
            "coUseSrvSeq": soup.find('input', {'name':'coUseSrvSeq'})['value'],
            "usrSeq": soup.find('input', {'name':'usrSeq'})['value'],
            **contents
        }

        params = '&'.join(['{}={}'.format(key, value) for key, value in form.items()])

        url = '{host}/LSO/openApi/cuAskUpdateSubmit.do?{params}'.format(host=self.host, params=params)
        print('[PUT] {url}'.format(url=url.split('?')[0]))
        req = self.session.get(url, headers=self.headers, verify=False)
        print('\tUPDATE_STATUS:', req.status_code)      

    def logOut(self):
        url = '{host}/LSO/logout.do'.format(host=self.host)
        print('[POST] {url}'.format(url=url))
        req = self.session.get(url, headers=self.headers, verify=False)
        print('\tLOGOUT_STATUS:', req.status_code)        

    def close(self):
        self.session.cookies.clear()
        self.session.close()