# -*- coding: utf-8 -*-

import re
import sys
import time
import datetime
import socket
import random
import delay

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = 'irc.run.net'
PORT = 6660
NICK = 'Coxy'
USERNAME = 'Coxy'
REALNAME = 'kupp bot'
CHANNEL = "#16bits"
PREFIX = '.'
CHANNELS = open('ch.txt')

CHANNELS_list = CHANNELS.readlines()

# def isint(n):
#     try:
#         int(n)
#         return True
#     except ValueError:
#         return False

def join(s, channels):
    for i in range(len(channels)):
        s.send(('JOIN ' + channels[i] + '\r\n').encode())

def connect():
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
    join(s, CHANNELS_list)
    connected = True

base = open('base.txt')
Coxy = base.readlines()

def input_msg(s):
    msg = str(input())
    if msg:
        s.send((str('PRIVMSG ' + CHANNEL + ' :' + msg + ' \r\n').encode()))

def sender_nick_find(data):
    n = 1
    nick = ''
    while data[n] != '!':
        nick += data[n]
        n += 1
    return nick

def sender_ch_find(data):
    n = 1
    ch = ''
    while data[n] != '#':
        n += 1
    while data[n] != ' ':
        ch += data[n]
        n += 1
    return ch

def msg_trim(s, Coxy, number, start, end, data):
    if sys.getsizeof(str('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number] + ' \r\n').encode()) <= 512:
        s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number] + ' \r\n').encode()))
    else:
        message_trim = ('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number] + ' \r\n')
        while sys.getsizeof(message_trim.encode()) > 512:
            end += 1
            message_trim = message_trim[start:end]
        s.send((str('PRIVMSG ' + sender_ch_find(data) + ' :' + Coxy[number][start:end] + ' \r\n').encode()))
        if sys.getsizeof(Coxy[number][end:len(Coxy)].encode()) > 512:
            msg_trim(Coxy, number, end, len(Coxy))

senders_nick_list = []
senders_nick_time = []
senders_boobs_nick_list = []
senders_boobs_nick_time = []
send_timer = datetime.timedelta(seconds=120)
last_citations_list = []
last_citations_time = []
citations_timer = datetime.timedelta(minutes=15)
version= 'Ну раз тебе так интересно, умник, то вот я https://github.com/kupp1/Coxy Названий, версий нет.'
help_str = 'Меня зовут Coxy! Я бот kupp. Пока, единственное что я делаю, это по команде !Coxy пишу различные цитаты доктора Кокса из сериала "Клиника", коих у меня ' + str(len(Coxy))
threshold = 5 * 60

def loop():
    try:
        global connected
        while connected == True:
            data = s.recv(4096).decode('utf-8', 'ignore')
            last_ping = time.time()
            if data.find('PING') != -1:
                s.send(str('PONG ' + data.split()[1] + '\r\n').encode())
            if (time.time() - last_ping) > threshold:
                connected = False
                break
            print(data)
            help = False
            if re.search(NICK + '.* hi', data):
                sender_nick = sender_nick_find(data)
                sender_ch = sender_ch_find(data)
                s.send((str('PRIVMSG ' + sender_ch + ' :' + sender_nick + ': Hi! Im ' + NICK + ' \r\n').encode()))
            if data.find(PREFIX + NICK + 'help') != -1:
                sender_ch = sender_ch_find(data)
                help = True
                s.send((str('PRIVMSG ' + sender_ch + ' :' + help_str + ' \r\n').encode()))
            if data.find(PREFIX + 'boobs') != -1:
                sender_nick = sender_nick_find(data)
                sender_ch = sender_ch_find(data)
                if delay.delay(senders_boobs_nick_list, senders_boobs_nick_time, send_timer, sender_nick + '_at_' + sender_ch_find(data)) == True:
                    s.send((str('PRIVMSG ' + sender_ch + ' :' + 'http://media.oboobs.ru/boobs/0' + str(random.randrange(7630)) +'.jpg' + ' \r\n').encode()))
                else:
                    s.send((str('NOTICE ' + sender_nick + ' :delay 15 minutes' + ' \r\n').encode()))
            if (data.find(PREFIX + NICK) != -1) and (help == False):
                sender_nick = sender_nick_find(data)
                sender_ch = sender_ch_find(data)
                if delay.delay(senders_nick_list, senders_nick_time, send_timer, sender_nick + '_at_' + sender_ch) == True:
                    number = random.randint(0, len(Coxy))
                    msg_trim(s, Coxy, number, 0, len(Coxy), data)
                else:
                    sender_nick = sender_nick_find(data)
                    s.send((str('NOTICE ' + sender_nick + ' :delay 120 seconds' + ' \r\n').encode()))
            if data.find(NICK + ' :\x01VERSION\x01') != -1:
                sender_nick = sender_nick_find(data)
                s.send(str('NOTICE ' + sender_nick + ' :\x01VERSION ' + version + ' \r\n').encode())
            if re.search('.* KILL' + NICK, data):
                join()
    except:
        connect()
        loop()
connect()
loop()