import datetime
import time
import subprocess
import random
import urllib.request
import json
from libs import parsers
from libs import dance
import socket

class irc_command():
    def __init__(self, prefix: str, command: str, pub_use=True, priv_use=True, required_args=0, pub_delay=datetime.timedelta(seconds=120), priv_delay=datetime.timedelta(seconds=0), command_mirror=''):
        self.prefix = prefix
        self.command = command
        self.pub_use = pub_use
        self.priv_use = priv_use
        self.required_args = required_args
        self.pub_delay = pub_delay
        self.priv_delay = priv_delay
        self.command_mirror = command_mirror

        self.priv_list =[]
        self.priv_time = []
        self.pub_list = []
        self.pub_time = []

    def get_word_list(self, msg: str):
        return msg.split()

    def _command_find(self, msg: list): # check commands call
        if msg[0:len(self.prefix) + len(self.command)] == self.prefix + self.command:
            #find [prefix][command]  at the beginning of the message
            return True
        else:
            if self.command_mirror:
                if msg[0:len(self.prefix) + len(self.command_mirror)] == self.prefix + self.command_mirror:
                    #if cant find [prefix][command] check [prefix][command_mirror]
                    return True
                else:
                    return False

    def _isPrivate(self, msg: str, self_nick: str): #check if msg is private
        if msg.find('PRIVMSG ' + self_nick) != -1:
            return True
        else:
            return False

    def _delay(self, list, time, timer, value): #command use delay
        if str(timer) != '0:00:00':
            new_member = True
            allow = True
            if len(list) != 0:
                for i, _ in enumerate(list):
                    if list[i] == value:
                        new_member = False
                        if (datetime.datetime.now() - time[i]) >= timer:
                            del list[i]
                            del time[i]
                            allow = True
                        else:
                            allow = False
            else:
                allow = True
            if new_member == True:
                list.append(value)
                time.append(datetime.datetime.now())
            return allow
        else:
            return True

    def _last_delay_del(self, list, time): #del last delay
        del list[len(list) - 1]
        del time[len(time) - 1]

    def delay2str(self, delay): #convet datetime.timedelta to string, for dalay notice
        seconds = int(delay.total_seconds())
        minutes = 0
        hours = 0
        days = 0
        if seconds > 60:
            minutes = int(seconds // 60)
            # seconds = int(seconds % 60)
        if minutes > 60:
            hours = int(minutes // 60)
            minutes = int(minutes % 60)
        if hours > 24:
            days = int(hours // 24)
            hours = int(hours % 24)
        if days == 0:
            if hours == 0:
                if minutes == 0:
                    return '0'
                else:
                    return str(minutes) + ' minutes'
            else:
                if minutes == 0:
                    return str(hours) + ' hours'
                else:
                    return str(hours) + ' hours, ' + str(minutes) + ' minutes'
        else:
            if hours == 0:
                if minutes == 0:
                    return str(days) + ' days'
                else:
                    return str(days) + ' days, ' + str(minutes) + ' minutes'
            else:
                if minutes == 0:
                    return str(days) + ' days, ' + str(hours) + ' hours'
                else:
                    return str(days) + ' days, ' + str(hours) + ' hours, ' + str(minutes) + ' minutes'

    def _call_check(self, msg: str, self_nick: str, irc): #check right to use on public or on private and delays
        if self.priv_use:
            if self._isPrivate(msg, self_nick):
                self.target = irc.sender_nick_find(msg)
                if self._delay(self.priv_list, self.priv_time, self.priv_delay, irc.name + '_' + self.target):
                    return True
                else:
                    irc.send_notice(self.target, 'delay: ' + self.delay2str(self.priv_delay))
                    return False
        else:
            if self._isPrivate(msg, self_nick):
                return False
        if self.pub_use:
            if not(self._isPrivate(msg, self_nick)):
                self.target = irc.sender_ch_find(msg)
                nick = irc.sender_nick_find(msg)
                if self._delay(self.pub_list, self.pub_time, self.pub_delay, irc.name + '_' + self.target + '_' + irc.sender_nick_find(msg)):
                    return True
                else:
                    irc.send_notice(nick, 'delay: ' + self.delay2str(self.pub_delay))
                    return False
        else:
            if not(self._isPrivate(msg, self_nick)):
                return False

    def _arg_check(self, word_list: list): #check required args
        self.args = word_list[1:]
        if len(self.args) >= self.required_args:
            return True
        else:
            return False

    def reply(self, msg: str, self_nick: str, irc): #check all
        self.msg_content = irc.get_real_privmsg(msg)
        if self._command_find(self.msg_content):
            msg_content = irc.get_real_privmsg(msg)
            word_list = self.get_word_list(msg_content)
            if self._call_check(msg, self_nick, irc):
                if self._arg_check(word_list):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

class uptime_irc_command(irc_command):
    def __init__(self, bot_start_time):
        super().__init__(prefix='.', command='uptime')
        self.bot_start_time = bot_start_time

    def get_bot_uptime(self, bot_start_time):
        time_diff = datetime.datetime.now() - bot_start_time
        seconds = int(time_diff.total_seconds())
        minutes = 0
        hours = 0
        days = 0
        if seconds > 60:
            minutes = int(seconds // 60)
            # seconds = int(seconds % 60)
        if minutes > 60:
            hours = int(minutes // 60)
            minutes = int(minutes % 60)
        if hours > 24:
            days = int(hours // 24)
            hours = int(hours % 24)
        return 'Bot uptime: ' + str(days) + ' days, ' + str(hours) + ' hours, ' + str(minutes) + ' minutes'

    def req(self, msg: str, irc): #main function
        if self.reply(msg, irc.nick, irc):
            irc.send_privmsg(self.target, self.get_bot_uptime(self.bot_start_time))

class host_uptime_irc_command(irc_command):
    def __init__(self):
        super().__init__(prefix='.', command='host_uptime')

    def get_host_machine_uptime(self):
        return 'host machine ' + subprocess.check_output(['uptime', '-p']).decode()

    def req(self, msg: str, irc):
        if self.reply(msg, irc.nick, irc):
            irc.send_privmsg(self.target, self.get_host_machine_uptime())

class boobs_irc_command(irc_command):
    def __init__(self):
        super().__init__(prefix='.', command='boobs', command_mirror='сиськи')

    def req(self, msg: str, irc):
        if self.reply(msg, irc.nick, irc):
            irc.send_privmsg(self.target, parsers.boobs())

class butts_irc_command(irc_command):
    def __init__(self):
        super().__init__(prefix='.', command='butts', command_mirror='жопки')

    def req(self, msg: str, irc):
        if self.reply(msg, irc.nick, irc):
            irc.send_privmsg(self.target, parsers.butts())

class Coxy_irc_command(irc_command):
    def __init__(self):
        super().__init__(prefix='.', command='Coxy')
        base = open('./libs/base.txt')
        self.Coxy = base.readlines()
        self.random_list = []
        self.random_time = []
        self.random_delay = datetime.timedelta(minutes=15)

    def req(self, msg: str, irc):
        if self.reply(msg, irc.nick, irc):
            if (len(self.args)) != 0:
                try:
                    irc.send_privmsg(self.target, self.Coxy[int(self.args[0])])
                except:
                    irc.send_notice(irc.sender_nick_find(msg), 'Cant find ' + str(self.args[0]))
            else:
                while True:
                    index = random.randint(0, len(self.Coxy) - 1)
                    if self._delay(self.random_list, self.random_time, self.random_delay, index):
                        break
                    else:
                        continue
                irc.send_privmsg(self.target, self.Coxy[index])

class dance_irc_command(irc_command):
    def __init__(self):
        super().__init__(prefix='.', command='dance', priv_use=False, pub_delay=datetime.timedelta(days=1))

    def req(self, msg: str, irc):
        if self.reply(msg, irc.nick, irc):
            irc.send_privmsg(self.target, dance.get_dance_1())
            time.sleep(3)
            irc.send_privmsg(self.target, dance.get_dance_2())
            time.sleep(3)
            irc.send_privmsg(self.target, dance.get_dance_3(irc.get_names(self.target), irc.nick))

class dance_top_irc_command(irc_command):
    def __init__(self):
        super().__init__(prefix='.', command='top', pub_use=False, priv_delay=datetime.timedelta(minutes=5))

    def req(self, msg: str, irc):
        if self.reply(msg, irc.nick, irc):
            top = dance.get_top_dacers()
            irc.send_privmsg(self.target, dance.get_top_start())
            for i in range(len(top)):
                irc.send_privmsg(self.target, '\x0302' + top[i].split()[0] + '\x03 : \x0304 ' + top[i].split()[1] + '\x03')
            irc.send_privmsg(self.target, dance.get_top_end())

class help_irc_command(irc_command):
    def __init__(self, help_str):
        super().__init__(prefix='.', command='help')
        self.help_str = help_str
    def req(self, msg: str, irc):
        if self.reply(msg, irc.nick, irc):
            irc.send_privmsg(self.target, self.help_str)


class ipinfo_irc_command(irc_command):
    def __init__(self):
        super().__init__(prefix='.', command='ipinfo', pub_use=False, priv_delay=datetime.timedelta(minutes=2), required_args=1)

    def get_info(self, adress):
        try:
            api = "http://freegeoip.net/json/" + adress
            result = urllib.request.urlopen(api).read()
            result = str(result)
            result = result[2:len(result) - 3]
            result = json.loads(result)

            info = []
            info.append("IP: " + result["ip"])
            info.append("Country Name: " + result["country_name"])
            info.append("Country Code: " + result["country_code"])
            info.append("Region Name: " + result["region_name"])
            info.append("Region Code: " + result["region_code"])
            info.append("City: " + result["city"])
            info.append("Zip Code: " + result["zip_code"])
            info.append("Latitude: " + str(result["latitude"]))
            info.append("Longitude: " + str(result["longitude"]))
            info.append("Location link: " + "http://www.openstreetmap.org/#map=11/" + str(result["latitude"]) + "/" + str(
                result["longitude"]))

            return info
        except:
            return -1

    def req(self, msg: str, irc):
        if self.reply(msg, irc.nick, irc):
            info = self.get_info(self.args[0])
            if isinstance(info, list):
                for i in info:
                    irc.send_privmsg(self.target, i)
            else:
                try:
                    if self.args[0].find('https://') != -1:
                        self.args[0] = self.args[0][8:]
                    if self.args[0].find('http://') != -1:
                        self.args[0] = self.args[0][7:]
                    cut = self.args[0].find('/')
                    if cut != -1:
                        self.args[0] = self.args[0][:cut]
                    info = self.get_info(socket.gethostbyname(self.args[0]))
                    if isinstance(info, list):
                        for i in info:
                            irc.send_privmsg(self.target, i)
                    else:
                        irc.send_privmsg(self.target, 'error')
                except:
                    try:
                        nick_ip = irc.whois(irc.sender_nick_find(msg))['ip']
                        if nick_ip:
                            info = self.get_info(nick_ip)
                            for i in info:
                                irc.send_privmsg(self.target, i)
                        else:
                            irc.send_privmsg(self.target, 'error')
                    except:
                        irc.send_privmsg(self.target, 'error')

class test_irc_command(irc_command):
    def __init__(self):
        super().__init__(prefix='.', command='test', pub_use=False, priv_delay=datetime.timedelta(minutes=2), required_args=1)

    def req(self, msg: str, irc):
        if self.reply(msg, irc.nick, irc):
            irc.send_privmsg(self.target, str(irc.whois(self.args[0])))
