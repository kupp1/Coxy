import json
import urllib.request

def boobs():
    try:
        url = 'http://api.oboobs.ru/noise/1/'
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode('utf-8')
        msg = 'http://media.oboobs.ru/%s' % json.loads(text)[0]['preview']
        return msg
    except:
        return -1

def butts():
    try:
        url = 'http://api.obutts.ru/noise/1/'
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode('utf-8')
        msg = 'http://media.obutts.ru/%s' % json.loads(text)[0]['preview']
        return msg
    except:
        return -1
