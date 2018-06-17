#! /usr/bin/python3
# -*- coding: utf-8 -*-

import re
import sys
import time
import datetime
import random
sys.path.insert(0, './kirc')
import kirc #from ./kirc, lib with simple functions to irc, see https://github.com/kupp1/kirc
sys.path.insert(0, './libs')
import delay #lib for delay bot commands use
import parsers #some website parsers
import uptime #stupid lib for get linux machine uptime
import dance
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "des_crypt"], deprecated="auto")
hash_file = open('hash')
true_pass_hash = hash_file.readlines()

def check_password(password):
    if pwd_context.verify(password, true_pass_hash[0]) != True:
        return False
    else:
        return True


passes = 0
def get_pass_for_nickserv(attempts):
    global passes
    print('Enter password: ', end='')
    password = str(input()) # get password for nickserv
    if check_password(password) != True:
        if passes < attempts:
            print('Incorrect password! Try again!')
            passes += 1
            get_pass_for_nickserv(attempts - 1)
        else:
            sys.exit(str(passes+1) + ' incorrect password attempts!')
    else:
        return password


bot_managers = [
    'kupp'
]
manage_session_timeout = datetime.timedelta(minutes=20)

password = get_pass_for_nickserv(3)
print('Password accept')

host = 'irc.run.net'
port = 6660 #use utf-8
nick = 'Coxy_t'
username = 'Coxy'
realname = 'kupp bot'
quit_msg = 'Я вышел, но это не значит, что я обязательно крашнулся.'

bot_hoster = 'kupp' #nick

prefix = '.'
channels = [
    '#16bits',
    # '#16bit'
]

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
dance_list = []
dance_time = []
dance_timer = datetime.timedelta(days=1)
threshold = 15 * 60

version= 'Coxy v1: https://github.com/kupp1/Coxy | kupp bot'
help_str = 'My name Coxy! Im ' + bot_hoster + ' bot'

start_time = datetime.datetime.now()

arg = ''

def get_command(msg):
    global prefix
    global arg
    if msg.split()[0][0:len(prefix)] == prefix:
        try:
            arg = msg.split()[1]
        except IndexError:
            arg = ''
        return msg.split()[0][len(prefix):len(msg.split()[0])]
    else:
        return ''

def get_bot_uptime():
    global start_time
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
        days = int(hours // 24)
        hours = int(hours % 24)
    return 'Bot uptime: ' + str(days) + ' days, ' + str(hours) + ' hours, ' + str(minutes) + ' minutes'

def start_dance(ch):
    kirc.send_privmsg(ch, dance.get_dance_1())
    time.sleep(3)
    kirc.send_privmsg(ch, dance.get_dance_2())
    time.sleep(3)
    kirc.send_privmsg(ch, dance.get_dance_3(kirc.get_names(ch), nick))

def send_dance_top(recipient):
    top = dance.get_top_dacers()
    kirc.send_privmsg(recipient, dance.get_top_start())
    for i in range(len(top)):
        kirc.send_privmsg(recipient, '\x0302' + top[i].split()[0] + '\x03 : \x0304 ' + top[i].split()[1] + '\x03')
    kirc.send_privmsg(recipient, dance.get_top_end())

def privmsg_priv_check(msg):
    if msg.find('PRIVMSG ' + nick) != -1:
        return True
    else:
        return False

def bot_start():
    global connected
    if kirc.connect(host, port, nick, username, realname, 60, 3) == True:
        connected = True
        kirc.join(channels)
        loop()

connected = False
def loop():
    try:
        kirc.send('nickserv identify ' + password)
        global connected
        while connected == True:
            data = kirc.get_irc_data()
            print('[' + time.strftime("%H:%M:%S")+ '] ' + data)

            if data.find('PING') != -1:
                kirc.send('PONG ' + data.split()[1])
                last_ping = time.time()
            if ('last_ping' in locals()) and (len(data) == 0):
                if (time.time() - last_ping) > threshold:
                    connected = False
                    raise ValueError('Disconnected!')
            if re.search(nick + '.* hi', data):
                kirc.send_privmsg(kirc.sender_ch_find(data), kirc.sender_nick_find(data) + ': Hi! Im ' + nick)
            if data.find(nick + ' :\x01VERSION\x01') != -1:
                kirc.send_notice(kirc.sender_nick_find(data), '\x01VERSION ' + version)
            if re.search('.* KICK .*' + nick, data):
                print('kick at ' + kirc.sender_ch_find(data))
                kirc.join_once(kirc.sender_ch_find(data))

            msg = kirc.get_real_privmsg(data)
            command = ''
            if msg:
                command = get_command(msg)
                priv = privmsg_priv_check(data)
            if command:
                if privmsg_priv_check(data) == False:
                    recipient = kirc.sender_ch_find(data)
                else:
                    recipient = kirc.sender_nick_find(data)
                if command == 'uptime':
                    kirc.send_privmsg(recipient, get_bot_uptime())
                if command == 'host_uptime':
                    kirc.send_privmsg(recipient, uptime.get_host_machine_uptime())
                if command == 'help':
                    kirc.send_notice(kirc.sender_nick_find(data), help_str)
                if (command == 'boobs') or (command == 'сиськи'):
                    if delay.delay(senders_boobs_nick_list, senders_boobs_nick_time, send_timer, kirc.sender_nick_find(data)) == True:
                        kirc.send_privmsg(recipient, parsers.boobs())
                    else:
                        kirc.send_notice(kirc.sender_nick_find(data), 'delay 120 seconds')
                if (command == 'butts') or (command == 'жопки'):
                    if delay.delay(senders_butts_nick_list, senders_butts_nick_time, send_timer, kirc.sender_nick_find(data)) == True:
                        kirc.send_privmsg(recipient, parsers.butts())
                    else:
                        kirc.send_notice(kirc.sender_nick_find(data), 'delay 120 seconds')
                if command == nick:
                    if delay.delay(senders_nick_list, senders_nick_time, send_timer, kirc.sender_nick_find(data)) == True:
                        index = random.randint(0, len(Coxy))
                        if arg:
                            try:
                                kirc.send_privmsg(recipient, Coxy[int(arg)])
                            except:
                                delay.last_force_del(senders_nick_list, senders_nick_time)
                                kirc.send_notice(kirc.sender_nick_find(data), 'Enter only citation number after command motherfucker!')

                        else:
                            while delay.delay(last_citations_list, last_citations_time, citations_timer, str(index)) != True:
                                index = random.randint(0, len(Coxy))
                            kirc.send_privmsg(recipient, Coxy[index])
                    else:
                        kirc.send_notice(kirc.sender_nick_find(data), 'delay 120 seconds')
                if (command == 'dance') and (priv == False):
                    if arg:
                        if arg == 'top':
                            kirc.send_notice(kirc.sender_nick_find(data), 'I send statistics as private message')
                            send_dance_top(kirc.sender_nick_find(data))
                    else:
                        if delay.delay(dance_list, dance_time, dance_timer, kirc.sender_ch_find(data)) == True:
                            start_dance(kirc.sender_ch_find(data))
                        else:
                            kirc.send_privmsg(kirc.sender_ch_find(data), 'Маэстро приходит один раз в день!')
                elif (command == 'dance') and (priv == True):
                    if arg == 'top':
                        kirc.send_notice(kirc.sender_nick_find(data), 'I send statistics as private message')
                        send_dance_top(recipient)
                    else:
                        kirc.send_privmsg(kirc.sender_nick_find(data), 'Эта команда только для каналов')
    except KeyboardInterrupt:
        print('\n')
        kirc.quit(quit_msg)
        sys.exit('Interrupt by user')
    except:
        kirc.reload_sock()
        bot_start()

bot_start()