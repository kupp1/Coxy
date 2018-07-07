#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Coxy is a python3 opensourse irc bot
Author: kupp1 on github aka kupp on irc RusNet network
License: Apache-2.0
"""

import yaml
import re
import sys
import time
import datetime
from old import commands
from passlib.context import CryptContext
from getpass import getpass

pwd_context = CryptContext(schemes=['pbkdf2_sha256', 'des_crypt'], deprecated='auto')
# init cryptography for password checker
hash_file = open('hash')  # open file with sha256 hash for password
true_pass_hash = hash_file.readlines()  # read hash


def check_password(password):
    return pwd_context.verify(password, true_pass_hash[0])  # check password with hash

passes = 0  # auxiliary variable for pass checker

def get_pass_for_nickserv(attempts):  # get pass for nick auth
    while passes < attempts:
        if passes == attempts:
            sys.exit('incorrect password attempts!')
        password = getpass(prompt='Enter password: ')
        if check_password(password):
            return password
        else:
            print('Incorrect password! Try again!')

password = get_pass_for_nickserv(3)
print('Password accept')

start_time = datetime.datetime.now()  # bot start time for uptime command
timeout = 6 * 60  # server ping timeout in seconds

# not necessarily info
nick = 'Coxy'
host = 'irc.run.net'
bot_hoster = 'kupp'
version= 'Coxy v2: https://github.com/kupp1/Coxy | kupp bot'
help_str = 'My name Coxy! Im %s%s' % (bot_hoster, ' bot')
quit_msg = 'Im part, but it doesnt mean that i crash'

file = open("servers.yaml", 'r')  # open config file
servers = yaml.load(file)
file.close()

for server in servers:  # dynamic create insistence of irc class from kirc with options from servers.yaml
                        # name of insistance == server name from servers.yaml
    exec(server + ' = ' + 'kirc.Irc(name="' + server + '", host="' + servers[server]['host'] + '", port=' +
         str(servers[server]['port']) + ', nick="' + servers[server]['nick'] + '", username="' +
         servers[server]['username'] + '", realname="' + servers[server]['realname'] + '", encoding="' +
         servers[server]['encoding'] + '", ssl_connect=' + str(servers[server]['ssl']) + ', hide_ip=' +
         str(servers[server]['hide_ip']) + ', nick_auth=' + str(servers[server]['nick_auth']) + ', nick_auth_str="' +
         servers[server]['nick_auth_str'] + '", nick_pass="' + password + '")')

# init commands, see main class in commands.py
# not the best solution
uptime = commands.uptime_irc_command(start_time)
host_uptime = commands.host_uptime_irc_command()
boobs = commands.boobs_irc_command()
butts = commands.butts_irc_command()
Coxy = commands.Coxy_irc_command()
dance = commands.dance_irc_command()
top = commands.dance_top_irc_command()
help = commands.help_irc_command(help_str)
ipinfo = commands.ipinfo_irc_command()
whois = commands.whois_irc_command()
kitty = commands.kitty_irc_command()


def bot_start():  # dynamic start all thread (one thread - one server)
    for server in servers:
        exec('%s.connect(3, 60)' % server)  # connect to server (kirc.irc.connect)
        exec('%s_channels = %s' % (server, str(servers[server]['channels'])))  # get channels list from config
        exec('%s.join(%s%s%s' % (server, server, '_channels', ')'))  # join to all channels from list


def bot_restart():  # dynamic restart all thread (one thread - one server)
    for server in servers:
        exec('%s.reload_sock()' % server) # (kirc.irc.reload_sock)
    bot_start()


def server_reconnect(irc, channels):
    irc.reload_sock()
    irc.connect(3, 60)
    irc.join(channels)


def bot_quit():   # dynamic quit all thread (one thread - one server)
    for server in servers:
        exec('%s.quit(quit_msg)' % server) # (kirc.irc.quit)

def loop(irc):
    while True:
        msg = irc.get_irc_data()  # decode irc bytes to string
        irc.pretty_print(msg)  # print with timestamp

        if msg.find('PING') != -1:  # reply server ping
            try:
                irc.send('PONG ' + msg.split()[1])
                irc.pretty_print('Send PING to %s' % msg.split()[1])
                last_ping = time.time()
            except:
                pass

        if 'last_ping' in locals():  # check server pings timeout
            if (time.time() - last_ping) > timeout and (len(msg) == 0):
                exec('server_reconnect(irc, %s%s' % (irc.name, '_channels)'))
                loop(irc)

        if re.search(irc.nick + '.* hi', msg):  # test command (bor_nick * hi)
            irc.send_privmsg(irc.get_msg_ch(msg), '%s: Hi! Im %s' % (irc.get_sender_nick(msg), irc.nick))

        if msg.find('PRIVMSG %s%s' % (irc.nick, ' :\x01VERSION\x01')) != -1:  # CTCP VERSION reply
            irc.send_notice(irc.get_sender_nick(msg), '\x01VERSION %s' % version)
            irc.pretty_print('Send CTCP VERSION reply to %s' % irc.get_sender_nick(msg))
        if msg.find('PRIVMSG %s%s' % (irc.nick, ' :\x01TIME\x01')) != -1:  # CTCP TIME reply
            irc.send_notice(irc.get_sender_nick(msg), '\x01TIME %s' % time.strftime("%H:%M:%S"))
            irc.pretty_print('Send CTCP TIME reply to %s' % irc.get_sender_nick(msg))
        if msg.find('PRIVMSG %s%s' % (irc.nick, ' :\x01PING')) != -1:  # CTCP PING reply
            irc.send_notice(irc.get_sender_nick(msg), '\x01PING %s' % str(time.time()))
            irc.pretty_print('Send CTCP PING reply to %s' % irc.get_sender_nick(msg))

        if re.search('.* KICK .*' + irc.nick, msg):  # autorejoin after kick
            irc.pretty_print('Kick at %s' % irc.get_msg_ch(msg))
            irc.join_once(irc.get_msg_ch(msg))

        # wait commands, see classes in commands.py
        uptime(msg, irc)
        host_uptime(msg, irc)
        boobs(msg, irc)
        butts(msg, irc)
        Coxy(msg, irc)
        dance(msg, irc)
        top(msg, irc)
        help(msg, irc)
        ipinfo(msg, irc)
        whois(msg, irc)
        kitty(msg, irc)

bot_start()
for server in servers:  # dynamic create threads (one server - one thread)
    exec('%s_thread = Thread(target=loop, args=%s%s%s' % (server, '(', server, ',))'))  # init thread
    exec('%s_thread.start()' % server)  # start thread
