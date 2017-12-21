# coding = utf-8

import requests
import json
from bs4 import BeautifulSoup
import re
from copy import copy

headers = {
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language' : 'zh-CN,zh;q=0.8'
}

config = {
    'remarks' : '',
    'id' : '',
    'server' : 'server host',
    'server_port' : 8388,
    'server_udp_port' : 0,
    'password' : '0',
    'method' : 'aes-256-cfb',
    'protocol' : 'origin',
    'protocolparam' : '',
    'obfs' : 'plain',
    'obfsparam' : '',
    'remarks_base64' : '',
    'group' : '',
    'enable' : True,
    'udp_over_tcp' : False
}

def write_config(path, configs):
    try:
        with open(path, 'r+') as file:
            data = json.load(file)
            for i in range(len(data['configs'])):
                for j in range(len(configs)):
                    if data['configs'][i]['id'] == configs[j]['id']:
                        data['configs'][i] = configs[j]
        with open(path, 'w+') as file:
            json.dump(data, file, indent=4, sort_keys=True)
        print('Succeed')
    except Exception as e:
        print('Exception occured when writing config: ' + str(e))

def login(url, username, password):
    payload = {
        'log' : username,
        'pwd' : password,
        'testcookie' : '1'
    }
    session = requests.session()

    try:
        with session.get(url, headers=headers) as res:
            res = session.post(url, headers=headers, data=payload)
            assert res.status_code == 200
    except Exception as e:
        session = None
        print('Exception occured when login: ' + str(e))

    return session

def crawl(url, session):
    try:
        with session.get(url, headers=headers) as res:
            content = res.content.decode('utf-8')
    except Exception as e:
        content = None
        print('Exception occured when crawling: ' + str(e))

    return content

def parse(content):
    li = []
    soup = BeautifulSoup(content, 'lxml')
    for child in soup.find_all('iframe'):
        slices = re.split(r'[:：\s]\s*', child.parent.text)
        c = copy(config)
        c['server'] = slices[4]
        c['password'] = slices[25]
        c['method'] = slices[27]
        c['protocol'] = slices[29]
        c['obfs'] = slices[31]
        li.append(c)
    return li

if __name__ == '__main__':
    home_url = r''
    login_page = r''
    target_page = r''
    port1_file = r''
    port2_file = r''
    port1_id = r'B4DA090AD5DABFDCBA8D4AD6AA61BA09'
    port2_id = r'C2984E20E738EB88DC9059DF3242C71B'
    ssr_config_path = r'D:\Program Files (x86)\ShadowsocksR\gui-config.json'
    #ssr_config_path = r'gui-config.json'
    
    s = login(home_url+login_page, '', '')
    if s != None:
        configs = parse(crawl(home_url+target_page, s))
        configs[0]['id'] = port1_id
        configs[1]['id'] = port2_id
        configs[0]['server_port'] = int(crawl(home_url+port1_file, s))
        configs[1]['server_port'] = int(crawl(home_url+port2_file, s))
        
        write_config(ssr_config_path, configs)
