import re
import sys
import time
import datetime
from kirc import kirc
import commands
from passlib.context import CryptContext
from getpass import getpass

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
channels = [
    '#16bits',
    # '#16bit'
]

self_ping_timer = 2 * 60 #timer for sent ping to server
PONG_timeout = 5 #server timeout to reply on bot ping

nick = 'Coxy'
host = 'irc.run.net'
bot_hoster = 'kupp'
version= 'Coxy v2: https://github.com/kupp1/Coxy | kupp bot'
help_str = 'My name Coxy! Im ' + bot_hoster + ' bot'
quit_msg = 'Im part, but it doesnt mean that i crush'

RusNet = kirc.irc(host='irc.run.net', port=9996, nick='Coxy_t', username='Coxy', realname='kupp bot', encoding='utf-8', ssl_connect=True)

#init commands, see main class in commands.py
uptime = commands.uptime_irc_command(start_time)
host_uptime = commands.host_uptime_irc_command()
boobs = commands.boobs_irc_command()
butts = commands.butts_irc_command()
Coxy = commands.Coxy_irc_command()
dance = commands.dance_irc_command()
top = commands.dance_top_irc_command()
help = commands.help_irc_command(help_str)

def bot_start():
    RusNet.connect(3, 60)
    RusNet.join(channels)

def bot_restart():
    RusNet.reload_sock()
    bot_start()

def loop():
    self_ping_time = 0
    PONG_wait = False
    RusNet.send('nickserv identify ' + password) #auth nick on nickserv
    while True:
        try:
            msg = RusNet.get_irc_data() #decode irc bytes to string

            if msg.find('PING') != -1: #reply server ping
                try:
                    RusNet.send('PONG ' + msg.split()[1])
                    last_ping = time.time()
                except:
                    pass
            if 'last_ping' in locals(): #check server pings timeout
                if (time.time() - last_ping) > timeout and (len(msg) == 0):
                    raise Exception('Disconnected!') #generate error if timeout
            if PONG_wait: #bot waiting reply for selfping if PONG_wait == True
                if msg.find('PONG ' + host) == -1:
                    if time.time() - self_ping_time > PONG_timeout:
                        raise Exception('Disconnected!')
                else:
                    PONG_wait = False
            else:
                if time.time() - self_ping_time > self_ping_timer: #if PONG_wait == False and its time to sent ping bot sent ping to server
                    RusNet.send('PING ' + host)
                    PONG_wait = True
                    self_ping_time = time.time()
            if re.search(nick + '.* hi', msg): #test command
                RusNet.send_privmsg(RusNet.sender_ch_find(msg), RusNet.sender_nick_find(msg) + ': Hi! Im ' + nick)
            if msg.find(nick + ' :\x01VERSION\x01') != -1: #CTCP VERSION reply
                RusNet.send_notice(RusNet.sender_nick_find(msg), '\x01VERSION ' + version)
            if re.search('.* KICK .*' + nick, msg): #autorejoin
                RusNet.pretty_print('Kick at ' + RusNet.sender_ch_find(msg))
                RusNet.join_once(RusNet.sender_ch_find(msg))

            # wait commands, see classes in commands.py
            uptime.req(msg, RusNet)
            host_uptime.req(msg, RusNet)
            boobs.req(msg, RusNet)
            butts.req(msg, RusNet)
            Coxy.req(msg, RusNet)
            dance.req(msg, RusNet)
            top.req(msg, RusNet)
            help.req(msg, RusNet)
        except KeyboardInterrupt: #for pretty exit
            RusNet.quit(quit_msg)
            sys.exit('Interrupt by user')
        except: #for disconnect case
            bot_restart()
            loop()

bot_start()
loop()
