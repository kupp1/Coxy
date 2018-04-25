# -*- coding: utf-8 -*-

import re
import sys
import time
import datetime
import socket
import random
import delay
import parser

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = 'irc.run.net'
PORT = 6660
NICK = 'Coxy'
USERNAME = 'Coxy'
REALNAME = 'kupp bot'

PREFIX = '.'
CHANNELS = [
    '#16bits',
    '#16bit'
]



def sys_uptime(): #from https://thesmithfam.org/blog/2005/11/19/python-uptime-script/, get linux machine uptime
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

# def isint(n):
#     try:
#         int(n)
#         return True
#     except ValueError:
#         return False

def join(s, channels): #join to channels
    for i in range(len(channels)):
        s.send(('JOIN ' + channels[i] + '\r\n').encode())

def connect(): #connect to server
    global connected
    global CHANNELS_list
    print('soc created |', s)
    remote_ip = socket.gethostbyname(HOST)
    print('ip of irc server is:', remote_ip)

    s.connect((HOST, PORT))

    print('connected to: ', HOST, PORT)

    nick_cr = ('NICK ' + NICK + '\r\n').encode()
    s.send(nick_cr)
    usernam_cr = ('USER ' + USERNAME + ' ' + USERNAME + ' ' + USERNAME + ' ' + ':' + REALNAME + ' \r\n').encode()
    s.send(usernam_cr)
    connected = True

base = open('base.txt')
Coxy = base.readlines()

def sender_nick_find(data):
    n = 1
    nick = ''
    while data[n] != '!':
        nick += data[n]
        n += 1
    return nick

def sender_ch_find(data): #find sender channel
    n = 1
    ch = ''
    while data[n] != '#':
        n += 1
    while data[n] != ' ':
        ch += data[n]
        n += 1
    return ch

def msg_cut(s, Coxy, number, start, end, data): # cut long messages
    if sys.getsizeof(str('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number] + ' \r\n').encode()) <= 512:
        s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number] + ' \r\n').encode()))
    else:
        message_trim = ('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number] + ' \r\n')
        while sys.getsizeof(message_trim.encode()) > 512:
            end -= 1
            message_trim = message_trim[start:end]
        s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number][start:end] + ' \r\n').encode()))
        if sys.getsizeof(Coxy[number][end:len(Coxy)].encode()) > 512:
            msg_cut(Coxy, number, end, len(Coxy))

def get_real_msg(data):
    n = 0
    for i in range(len(data)):
        if data[i] == ':':
            n += 1
        if data[i] == ':' and n == 2:
            return data[i+1:]

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
help_str = 'Меня зовут Coxy! Я бот kupp. По команду .Coxy вывожу цитаты доктора кокса. По комаде .boobs порадую сиськами, а по .butts попками'
threshold = 5 * 60

start_time = datetime.datetime.now()

def loop():
    try:
        global connected
        while connected == True:
            data = s.recv(4096).decode('utf-8', 'ignore')
            print(data)
            last_ping = time.time()
            msg = get_real_msg(data)
            if data.find('PING') != -1:
                s.send(str('PONG ' + data.split()[1] + '\r\n').encode())
                last_ping = time.time()
            if (time.time() - last_ping) > threshold:
                connected = False
                break
            if msg:
                help = False
                uptime = False
                sys_uptime_b = False
                if re.search(NICK + '.* hi', msg):
                    s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + sender_nick_find(data) + ': Hi! Im ' + NICK + ' \r\n').encode()))
                if msg.find(PREFIX + NICK + ' uptime') != -1:
                    uptime = True
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
                if msg.find(PREFIX + NICK + ' sys_uptime') != -1:
                    sys_uptime_b = True
                    s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + sys_uptime() + ' \r\n').encode()))
                if data.find(PREFIX + NICK + ' help') != -1:
                    help = True
                    s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + help_str + ' \r\n').encode()))
                if data.find(PREFIX + 'boobs') != -1:
                    if delay.delay(senders_boobs_nick_list, senders_boobs_nick_time, send_timer, sender_nick_find(data) + '_at_' + sender_ch_find(data)) == True:
                        s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + parser.parser('boobs') + ' \r\n').encode()))
                    else:
                        s.send((str('NOTICE ' + sender_nick_find(data) + ' :delay 120 seconds' + ' \r\n').encode()))
                if data.find(PREFIX + 'butts') != -1:
                    if delay.delay(senders_butts_nick_list, senders_butts_nick_time, send_timer, sender_nick_find(data) + '_at_' + sender_ch_find(data)) == True:
                        s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + parser.parser('butts') + ' \r\n').encode()))
                    else:
                        s.send((str('NOTICE ' + sender_nick_find(data) + ' :delay 120 seconds' + ' \r\n').encode()))
                if (data.find(PREFIX + NICK) != -1) and (help == False) and (uptime == False) and (sys_uptime_b == False):
                    if delay.delay(senders_nick_list, senders_nick_time, send_timer, sender_nick_find(data) + '_at_' + sender_ch_find(data)) == True:
                        number = random.randint(0, len(Coxy))
                        msg_cut(s, Coxy, number, 0, len(Coxy), data)
                    else:
                        s.send((str('NOTICE ' + sender_nick_find(data) + ' :delay 120 seconds' + ' \r\n').encode()))
                if data.find(NICK + ' :\x01VERSION\x01') != -1:
                    s.send(str('NOTICE ' + sender_nick_find(data) + ' :\x01VERSION ' + version + ' \r\n').encode())
                if re.search('.* KILL' + NICK, data):
                    join(s, sender_ch_find(data))
    except:
        connect()
        join(s, CHANNELS)
        loop()
connect()
join(s, CHANNELS)
loop()