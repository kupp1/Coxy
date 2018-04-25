#parser get url to girl from obutts.ru or oboobs.ru api

import json
import urllib.request

butts = 'http://api.obutts.ru/noise/1/'
boobs = 'http://api.oboobs.ru/noise/1/'

def parser(mode):
    if mode != 'boobs' and mode != 'butts':
        return -1
    url = 'http://api.o' + mode + '.ru/noise/1/'
    response = urllib.request.urlopen(url)
    data = response.read()      # a `bytes` object
    text = data.decode('utf-8')
    msg = 'http://media.o' + mode + '.ru/%s' % json.loads(text)[0]['preview']
    return msg