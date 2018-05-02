# -*- coding: utf-8 -*-

import re
import sys
import time
import datetime
import socket
import random
import delay
import parser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "des_crypt"], deprecated="auto") # get password for nickserv
hash_file = open('hash')
true_pass_hash = hash_file.readlines()
password = str(input())
if pwd_context.verify(password, true_pass_hash[0]) != True:
    sys.exit('Incorrect password entered! Try again!') # if the password is incorrect program interrupted
del pwd_context
del hash_file
del true_pass_hash

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = 'irc.run.net'
PORT = 6660
NICK = 'Coxy'
USERNAME = 'Coxy'
REALNAME = 'kupp bot'

bot_hoster = 'kupp' #nick

PREFIX = '.'
CHANNELS = [
    '#16bits',
    '#16bit'
]

def join(s, channels): #join to channels, get list of channels
    for i in range(len(channels)):
        s.send(('JOIN ' + channels[i] + '\r\n').encode())
        print('JOIN to ' + channels[i])

def rejoin(s, channel): #func for auto rejoin, get one channel
    s.send(('JOIN ' + channel + '\r\n').encode())
    print('reJOIN to ' + channel)

def connect(): #connect to server
    print('soc created |', s)
    remote_ip = socket.gethostbyname(HOST)
    print('ip of irc server is:', remote_ip)
    s.connect((HOST, PORT))
    print('connected to: ', HOST, PORT)
    nick_cr = ('NICK ' + NICK + '\r\n').encode()
    s.send(nick_cr)
    usernam_cr = ('USER ' + USERNAME + ' ' + USERNAME + ' ' + USERNAME + ' ' + ':' + REALNAME + ' \r\n').encode()
    s.send(usernam_cr)

def sender_nick_find(data):
    nick = ''
    for i in range(len(data)):
        if (i > 0) and (data[i] != '!'):
            nick += data[i]
        elif data[i] == '!':
            break
    return nick

def sender_ch_find(data): #find sender channel
    ch = ''
    n1 = 0
    for n in range(len(data)):
        if data[n] == '#':
            n1 = n
    while data[n1] != ' ':
        ch += data[n1]
        n1 += 1
    return ch

def msg_cut(s, Coxy, number, start, end, data): # cut long messages
    if sys.getsizeof(str('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number][start:end] + ' \r\n').encode()) <= 514:
        s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number][start:end] + ' \r\n').encode()))
    else:
        message_trim = ('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number][start:end])
        while sys.getsizeof(message_trim.encode()) > 511:
            end -= 1
            message_trim = ('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number][start:end])
        s.send(str(message_trim + ' \r\n').encode())
        if sys.getsizeof(str('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number][end:len(Coxy[number])] + ' \r\n').encode()) > 514:
            msg_cut(s, Coxy, number, end, len(Coxy[number]), data)
        else:
            s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number][end:len(Coxy[number])] + ' \r\n').encode()))

def get_real_msg(data):
    n = 0
    for i in range(len(data)):
        if data[i] == ':':
            n += 1
        if data[i] == ':' and n == 2:
            return data[i+1:-3]

def sys_uptime(): #from https://thesmithfam.org/blog/2005/11/19/python-uptime-script/, return linux machine uptime
    try:
        f = open("/proc/uptime")
        contents = f.read().split()
        f.close()
    except:
        return "Cannot open uptime file: /proc/uptime"
    total_seconds = float(contents[0])
    MINUTE = 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24
    days = int(total_seconds / DAY)
    hours = int((total_seconds % DAY) / HOUR)
    minutes = int((total_seconds % HOUR) / MINUTE)
    seconds = int(total_seconds % MINUTE)
    string = ""
    if days > 0:
        string += str(days) + " " + (days == 1 and "day" or "days") + ", "
    if len(string) > 0 or hours > 0:
        string += str(hours) + " " + (hours == 1 and "hour" or "hours") + ", "
    if len(string) > 0 or minutes > 0:
        string += str(minutes) + " " + (minutes == 1 and "minute" or "minutes") + ", "
    string += str(seconds) + " " + (seconds == 1 and "second" or "seconds")
    return string

base = open('base.txt')
Coxy = base.readlines()

senders_nick_list = []
senders_nick_time = []
senders_boobs_nick_list = []
senders_boobs_nick_time = []
senders_butts_nick_list = []
senders_butts_nick_time = []
send_timer = datetime.timedelta(seconds=120)
last_citations_list = []
last_citations_time = []
citations_timer = datetime.timedelta(minutes=15)
version= 'Coxy: https://github.com/kupp1/Coxy'
help_str = 'Меня зовут Coxy! Я бот kupp. По команду .Coxy вывожу цитаты доктора Кокса из клиники. По комаде .boobs порадую сиськами, а по .butts попками'
threshold = 5 * 60

start_time = datetime.datetime.now()

def loop():
    try:
        global connected
        while connected == True:
            data = s.recv(4096).decode('utf-8', 'ignore')
            print(data)
            last_ping = time.time()
            if data.find('PING') != -1:
                s.send(str('PONG ' + data.split()[1] + '\r\n').encode())
                last_ping = time.time()
            if (time.time() - last_ping) > threshold:
                connected = False
                break
            msg = get_real_msg(data)
            if msg:
                if re.search(NICK + '.* hi', data):
                    s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + sender_nick_find(data) + ': Hi! Im ' + NICK + ' \r\n').encode()))
                if data.find(PREFIX + 'uptime') != -1:
                    time_diff = datetime.datetime.now() - start_time
                    seconds = int(time_diff.total_seconds())
                    minutes = 0
                    hours = 0
                    days = 0
                    if seconds > 60:
                        minutes = int(seconds // 60)
                        seconds = int(seconds % 60)
                    if minutes > 60:
                        hours = int(minutes // 60)
                        minutes = int(hours % 60)
                    if hours > 24:
                        days = int(hours// 24)
                        hours = int(hours % 24)
                    s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + sender_nick_find(data) + ': Чукча работает ' + str(days) + ' дней ' + str(hours) + ' часов ' + str(minutes) + ' минут ' + str(seconds) + ' секунд' + ' \r\n').encode()))
                if data.find(PREFIX + 'host_uptime') != -1:
                    s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + sys_uptime() + ' \r\n').encode()))
                if data.find(PREFIX + 'help') != -1:
                    s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + help_str + ' \r\n').encode()))
                if ( data.find(PREFIX + 'boobs') != -1 ) or ( data.find(PREFIX + 'сиськи') != -1 ):
                    if delay.delay(senders_boobs_nick_list, senders_boobs_nick_time, send_timer, sender_nick_find(data) + '_at_' + sender_ch_find(data)) == True:
                        s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + parser.parser('boobs') + ' \r\n').encode()))
                    else:
                        s.send((str('NOTICE ' + sender_nick_find(data) + ' :delay 120 seconds' + ' \r\n').encode()))
                if ( data.find(PREFIX + 'butts') != -1 ) or ( data.find(PREFIX + 'жопки') ) != -1:
                    if delay.delay(senders_butts_nick_list, senders_butts_nick_time, send_timer, sender_nick_find(data) + '_at_' + sender_ch_find(data)) == True:
                        s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + parser.parser('butts') + ' \r\n').encode()))
                    else:
                        s.send((str('NOTICE ' + sender_nick_find(data) + ' :delay 120 seconds' + ' \r\n').encode()))
                if data.find(PREFIX + NICK) != -1:
                    if delay.delay(senders_nick_list, senders_nick_time, send_timer, sender_nick_find(data) + '_at_' + sender_ch_find(data)) == True:
                        number = random.randint(0, len(Coxy))
                        msg_cut(s, Coxy, number, 0, len(Coxy[number]), data)
                    else:
                        s.send((str('NOTICE ' + sender_nick_find(data) + ' :delay 120 seconds' + ' \r\n').encode()))
                if data.find(NICK + ' :\x01VERSION\x01') != -1:
                    s.send(str('NOTICE ' + sender_nick_find(data) + ' :\x01VERSION ' + version + ' \r\n').encode())
                if re.search('.* KICK .*' + NICK, data):
                    print('kick at ' + sender_ch_find(data))
                    rejoin(s, sender_ch_find(data))
    except:
        time.sleep(60)
        connect()
        join(s, CHANNELS)
        loop()
connect()
while True:
    data = s.recv(4096).decode('utf-8', 'ignore')
    print(data)
    if data.find('001') != -1:
        s.send((str('nickserv identify ' + password + ' \r\n').encode()))
        connected = True
        print('Connection established')
        join(s, CHANNELS)
        loop()
        break
