import yaml
import re
import sys
import time
import datetime
from kirc import kirc
import commands
from passlib.context import CryptContext
from getpass import getpass
from threading import Thread
import traceback

pwd_context = CryptContext(schemes=['pbkdf2_sha256', 'des_crypt'], deprecated='auto') #init cryptography for password checker
hash_file = open('hash') #open file with sha256 hash for pawwword
true_pass_hash = hash_file.readlines() #readhash

def check_password(password):
    if pwd_context.verify(password, true_pass_hash[0]) != True: #check password with hash
        return False
    else:
        return True

passes = 0 # auxiliary variable for pass checker

def get_pass_for_nickserv(attempts):
    global passes
    password = getpass(prompt='Enter password: ') # get password for nickserv
    if check_password(password) != True:
        if passes < attempts:
            print('Incorrect password! Try again!')
            passes += 1
            get_pass_for_nickserv(attempts - 1)
        else:
            sys.exit(str(passes+1) + ' incorrect password attempts!') # if attempts exhausted program interrupt
    else:
        return password

password = get_pass_for_nickserv(3)
print('Password accept')

start_time = datetime.datetime.now()
timeout = 7 * 60 # server autoping timeout

self_ping_timer = 2 * 60 #timer for sent ping to server
PONG_timeout = 60 #server timeout to reply on bot ping

nick = 'Coxy'
host = 'irc.run.net'
bot_hoster = 'kupp'
version= 'Coxy v2: https://github.com/kupp1/Coxy | kupp bot'
help_str = 'My name Coxy! Im ' + bot_hoster + ' bot'
quit_msg = 'Im part, but it doesnt mean that i crash'

file = open("servers.yaml", 'r')
servers = yaml.load(file)
file.close()

for server in servers:
    exec(server + ' = ' + 'kirc.irc(name="' + server + '", host="' + servers[server]['host'] + '", port=' + str(servers[server]['port']) +
         ', nick="' + servers[server]['nick'] + '", username="' + servers[server]['username'] +
         '", realname="' + servers[server]['realname'] + '", encoding="' + servers[server]['encoding'] +
         '", ssl_connect=' + str(servers[server]['ssl']) + ')')

channels = servers['RusNet']['channels']

#init commands, see main class in commands.py
uptime = commands.uptime_irc_command(start_time)
host_uptime = commands.host_uptime_irc_command()
boobs = commands.boobs_irc_command()
butts = commands.butts_irc_command()
Coxy = commands.Coxy_irc_command()
dance = commands.dance_irc_command()
top = commands.dance_top_irc_command()
help = commands.help_irc_command(help_str)
ipinfo = commands.ipinfo_irc_command()
test = commands.test_irc_command()

def bot_start():
    for server in servers:
        exec(server + '.connect(3, 60)')
        exec(server + '_channels = ' + str(servers[server]['channels']))
        exec(server + '.join(' + server + '_channels' + ')')

def bot_restart():
    for server in servers:
        exec(server + '.reload_sock()')
    bot_start()

def bot_quit():
    for server in servers:
        exec(server + '.quit(quit_msg)')

def loop(irc):
    self_ping_time = 0
    PONG_wait = False
    irc.send('nickserv identify ' + password) #auth nick on nickserv
    while True:
        msg = irc.get_irc_data() #decode irc bytes to string
        irc.pretty_print(msg)

        if msg.find('PING') != -1: #reply server ping
            try:
                irc.send('PONG ' + msg.split()[1])
                last_ping = time.time()
            except:
                pass
        if 'last_ping' in locals(): #check server pings timeout
            if (time.time() - last_ping) > timeout and (len(msg) == 0):
                # raise Exception('Disconnected!') #generate error if timeout
                traceback.print_exc()
                bot_restart()
                loop()
        # if PONG_wait: #bot waiting reply for selfping if PONG_wait == True
        #     if msg.find('PONG ' + host) == -1:
        #         if time.time() - self_ping_time > PONG_timeout:
        #             raise Exception('Disconnected!')
        #     else:
        #         PONG_wait = False
        # else:
        #     if time.time() - self_ping_time > self_ping_timer: #if PONG_wait == False and its time to sent ping bot sent ping to server
        #         irc.send('PING ' + host)
        #         PONG_wait = True
        #         self_ping_time = time.time()
        if re.search(nick + '.* hi', msg): #test command
            irc.send_privmsg(irc.sender_ch_find(msg), irc.sender_nick_find(msg) + ': Hi! Im ' + nick)
        if msg.find(nick + ' :\x01VERSION\x01') != -1: #CTCP VERSION reply
            irc.send_notice(irc.sender_nick_find(msg), '\x01VERSION ' + version)
        if re.search('.* KICK .*' + nick, msg): #autorejoin
            irc.pretty_print('Kick at ' + irc.sender_ch_find(msg))
            irc.join_once(irc.sender_ch_find(msg))

        # wait commands, see classes in commands.py
        uptime.req(msg, irc)
        host_uptime.req(msg, irc)
        boobs.req(msg, irc)
        butts.req(msg, irc)
        Coxy.req(msg, irc)
        dance.req(msg, irc)
        top.req(msg, irc)
        help.req(msg, irc)
        ipinfo.req(msg, irc)
        test.req(msg, irc)

bot_start()
for server in servers:
    exec(server + '_thread = Thread(target=loop, args=' + '(' + server + ',))')
    # exec(server + '_thread.daemon = True')
    exec(server + '_thread.start()')