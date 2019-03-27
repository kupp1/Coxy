import re
import sys
import ssl
import time
import socket


def pretty_print(*args, end='\n'):
    """pretty print with timestamp"""
    print('[' + time.strftime("%H:%M:%S") + ']', *args, end=end)


RFC2812 = re.compile(r""" # Оригинальная регулярка взята с https://gist.github.com/datagrok/380449c30fd0c5cf2f30
             ^   # We'll match the whole line. Start.
                 # Optional prefix and the space that separates it
                 # from the next thing. Prefix can be a servername,
                 # or nick[[!user]@host]
             (?::(            # This whole set is optional but if it's
                              # here it begins with : and ends with space
               ([^@!\ ]*)     # nick
               (?:            # then, optionally user/host
                 (?:          # but user is optional if host is given
                   !~?([^@]*) # !user
                 )?           # (user was optional)
                 @([^\ ]*)    # @host
               )?             # (host was optional)
             )\ )?            # ":nick!user@host " ends
             ([^\ ]+)         # IRC command (required)
             # Optional args, max 15, space separated. Last arg is
             # the only one that may contain inner spaces. More than
             # 15 words means remainder of words are part of 15th arg.
             # Last arg may be indicated by a colon prefix instead.
             # Pull the leading and last args out separately; we have
             # to split the former on spaces.
             (
               (?:
                 \ [^:\ ][^\ ]* # space, no colon, non-space characters
               ){0,14}          # repeated up to 14 times
             )                  # captured in one reference
             (?:\ :?(.*))?      # the rest, does not capture colon.
             $ # EOL""", re.X)


class Parse:
    """
    Данный класс является оберткой над регуляркой, представленной выше.
    Позволяет более красивым образом запрашивать группу по «названию»:
        Parse(строчка).host например возвращает хост.
    """

    def __init__(self, data: str):
        self.__data = data

    def __parse(self, data: str):
        self.__parsed = RFC2812.search(data)
        return bool(self.__parsed)

    @property
    def parse(self):
        return RFC2812.search(self.__data).groups()

    @property
    def raw(self):
        return self.__data

    @property
    def ident(self):
        if self.__parse(self.__data):
            return self.__parsed.group(1)
        else:
            return ''

    @property
    def nick(self):
        if self.__parse(self.__data):
            return self.__parsed.group(2)
        else:
            return ''

    @property
    def username(self):
        if self.__parse(self.__data):
            return self.__parsed.group(3)
        else:
            return ''

    @property
    def host(self):
        if self.__parse(self.__data):
            return self.__parsed.group(4)
        else:
            return ''

    @property
    def command(self):
        if self.__parse(self.__data):
            return self.__parsed.group(5)
        else:
            return ''

    @property
    def params(self):
        if self.__parse(self.__data):
            return self.__parsed.group(6)[1:] or ''
        else:
            return ''

    @property
    def content(self):
        if self.__parse(self.__data):
            return self.__parsed.group(7) or ''
        else:
            return ''


class IrcConnectionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Irc():
    """
    Основнаой класс, в котором реализуется вся специфика IRC.
    Тестировалость только на Freenode и RusNet
    """

    def __init__(self, name: str, host: str, port: int, nick: str, username: str, realname: str, encoding: str,
                 ssl_enable=False, ping_timeout=60):
        self._name = name
        self._host = host
        self._port = port
        self._ssl_enable = ssl_enable
        self._nick = nick
        self._username = username
        self._realname = realname
        self._encoding = encoding
        self._ping_timeout = ping_timeout
        self.__sock_init()
        self.start_time = time.time()
        # регулярка дли пингов сервера
        self.ping_match = re.compile('^PING :.*')
        self.ctcp_match = re.compile(r'\x01(.*)\x01')

    @property
    def name(self):
        return self._name

    def __sock_init(self):
        if self._ssl_enable:
            self.__sock = ssl.wrap_socket(socket.socket())
        else:
            self.__sock = socket.socket()

    def __sock_close(self):
        self.__sock.shutdown(2)

    def __reload_sock(self):
        self.__sock_close()
        self.__sock_init()

    def connection_alive(self):
        self.send('PING :%s' % self._host)  # самостоятельно пингуем сервер
        # устанавливаем одну секунду как минимальное время пинга до сервера
        self.__sock.settimeout(1)
        try:
            msg = self.__sock.recv(4096).decode(
                self._encoding, 'ignore')  # ждем ответа
        except socket.timeout:
            # возвращаем иcходный таймаут
            self.__sock.settimeout(self._ping_timeout)
            return False  # вердикт: коннект оборвался
        else:  # если таймаута все-таки не произошло
            self.__sock.settimeout(self._ping_timeout)
            if msg.find('PONG :%s' % self._host):  # и мы получили понг
                return True  # вердикт: коннект стабилен
            else:
                return False

    def wait_data(self):
        """decode incoming bytes to text"""
        try:
            return self.__sock.recv(4096).decode(self._encoding, 'ignore')
        except socket.timeout:
            if not self.connection_alive():
                raise IrcConnectionError('disconnected')

    def send(self, data: str):
        self.__sock.send(('%s\r\n' % data).encode(self._encoding))

    def reconnect(self, reconnect_attempts: int, reconnect_timeout: int):
        self.__reload_sock()
        self.connect(reconnect_attempts, reconnect_timeout)

    def connect(self, connect_attempts: int, connect_timeout: int):
        pretty_print('soc created | %s' % str(self.__sock))
        attempt = 0
        connected = False
        while attempt <= connect_attempts and not connected:  # пока попытки не исчерпаны и коннекта нет
            attempt += 1
            try:
                try:  # пробуем запросить ip
                    remote_ip = socket.gethostbyname(self._host)
                except socket.gaierror:
                    raise IrcConnectionError(
                        'Name or service not known: %s' % self._host)
                pretty_print('ip of irc server is: %s' % str(remote_ip))
                try:  # пробуем подключится
                    self.__sock.connect((self._host, self._port))
                except socket.error:
                    raise IrcConnectionError('Connect timeout')
                # фактически коннект есть
                pretty_print('connected to %s:%s' %
                             (self._host, str(self._port)))
                # отправляем свои данные согласно rfc
                self.send('NICK %s' % self._nick)
                self.send('USER %s 0 * :%s' % (self._username, self._realname))
                connect_time = time.time()
                self.__sock.settimeout(self._ping_timeout)
                while True:  # ждем от сервера приветственного сообщения
                    if time.time() - connect_time > connect_timeout:
                        # если сообщение не пришло, то работать не можем
                        raise IrcConnectionError('Irc server timeout')
                    msgs = self.wait_data()
                    if msgs:
                        for msg in msgs.split('\r\n'):
                            if msg:
                                pretty_print(msg.strip())
                                if re.search('^00[1-9]$', Parse(msg).command):  # если пришло
                                    # то пожалуй все хорошо
                                    pretty_print('Connection established')
                                    connected = True
                    if connected:
                        break
            except IrcConnectionError:
                # замечаю, что внешний цикл повторяется только при выкидывании ошибки
                self.__reload_sock()
                continue

    def join(self, channels: list or str):
        if isinstance(channels, list):
            for ch in channels:
                self.send('JOIN %s' % ch)
                pretty_print('Join to %s' % ch)
        elif isinstance(channels, str):
            self.send('JOIN %s' % channels)
            pretty_print('Join to %s' % channels)

    def is_privmsg(self, msg: str, private=None):
        """
        Проверка является ли строка msg сообщением типа privmsg.
        Флаг private имеет три состояния:
            none: функция проверяет privmsg ли msg
            True: функция вернет True только если msg прислана боту в приват
            False: если не в приват
        """
        if private is None:
            return Parse(msg).command == 'PRIVMSG'
        elif private:
            return Parse(msg).command == 'PRIVMSG' and Parse(msg).params == self._nick
        else:
            return Parse(msg).command == 'PRIVMSG' and Parse(msg).params != self._nick

    def is_action(self, msg: str):
        return Parse(msg).command == 'PRIVMSG' and self.ctcp_match.search(Parse(msg).content)

    @staticmethod
    def is_notice(msg: str):
        return Parse(msg).command == 'NOTICE'

    @staticmethod
    def is_quit(msg: str):
        return Parse(msg).command == 'QUIT'

    @staticmethod
    def is_nick(msg: str):
        return Parse(msg).command == 'NICK'

    @staticmethod
    def is_join(msg: str):
        return Parse(msg).command == 'JOIN'

    @staticmethod
    def is_kick(msg: str):
        return Parse(msg).command == 'KICK'

    @staticmethod
    def is_part(msg: str):
        return Parse(msg).command == 'PART'

    @staticmethod
    def get_nick(msg: str):
        nick = Parse(msg).nick
        if nick:
            return nick
        else:
            return ''

    @staticmethod
    def get_msg_content(msg: str):
        content = Parse(msg).content
        content = re.sub(r'^\x01[^ ]+( |$)', '', content)
        return content.replace('\x01', '').replace('\r\n', '')

    def get_msg_channel(self, msg: str):
        if self.is_join(msg):
            channel = self.get_msg_content(msg)
        else:
            channel = Parse(msg).params
        try:
            if channel[0] == '#' or channel[0] == '&':
                return channel
            else:
                return ''
        except IndexError:
            return ''

    def _cut(self, command: str, recipient: str, text: str, start: int, end: int):
        """Разделяет блинное сообщение на части, т.к. в irc privmsg не может веcить больше 512 байт (514: два на \r\n)"""
        if sys.getsizeof(('%s %s :%s\r\n' % (command, recipient, text[start:end])).encode()) <= 514:
            self.send('%s %s :%s' % (command, recipient, text[start:end]))
            pretty_print('Send %s to %s :%s' %
                         (command.lower(), recipient, text[start:end].strip()))
        else:
            msg = ('%s %s :%s' % (command, recipient, text[start:end]))
            while sys.getsizeof(msg.encode()) > 511:
                end -= 1
                msg = '%s %s :%s' % (command, recipient, text[start:end])
            self.send(msg)
            pretty_print('Send %s to %s :%s' %
                         (command.lower(), recipient, text[start:end].strip()))
            if sys.getsizeof(('%s %s :%s\r\n' % (command, recipient, text[end:len(text)])).encode()) > 514:
                self._cut(command, recipient, text, end, len(text))
            else:
                self.send('%s %s :%s' % (command, recipient, text[end:len(text)]))
                pretty_print('Send privmsg to %s :%s' %
                             (recipient, text[end:len(text)].strip()))

    def send_privmsg(self, recipient: str, text: str):
        self._cut('PRIVMSG', recipient, text, 0, len(text))

    def send_notice(self, recipient: str, text: str):
        self._cut('NOTICE', recipient, text, 0, len(text))

    def send_action(self, recipient: str, text: str):
        self.send('PRIVMSG %s :\x01ACTION %s\x01' % (recipient, text))
        pretty_print('Send action to %s :%s' % (recipient, text))

    def maintenance(self, msg: str):
        if self.ping_match.search(msg):
            self.send('PONG %s' % msg.split(':')[1])
        content = Parse(msg).content
        ctcp_match = self.ctcp_match.search(content)
        if ctcp_match:
            print('CTCP')
            ctcp_string = ctcp_match.groups()[0]
            if self.is_privmsg(msg, private=True):
                if ctcp_string == 'VERSION':
                    self.send_notice(Parse(msg).nick, '\x01VERSION kirc https://github.com/kupp1/Coxy\x01')
                elif ctcp_string == 'TIME':
                    self.send_notice(Parse(msg).nick, '\x01TIME %s\x01' % time.strftime("%H:%M:%S"))

    def quit(self, quit_msg='Bye!'):
        self.send('QUIT :%s' % quit_msg)
        self.__sock_close()
