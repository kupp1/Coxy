import kirc
import time
import re
import irc_format
import random
import peewee

ip_match = re.compile('((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\s*$)|(^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$))')
url_match = re.compile(r"""
                (?:
                  (?:
                    (https?|ftp):\/\/
                  )|www\.
                )
                (?:
                  \S+
                  (?:
                    :\S*
                  )?@
                )?
                (
                  (?:
                    [1-9]\d?|1\d\d|2[01]\d|22[0-3]
                  )
                  (?:
                    \.(?:
                        1?\d{1,2}|2[0-4]\d|25[0-5]
                      )
                  ){2}
                  (?:
                    \.(?:
                        [1-9]\d?|1\d\d|2[0-4]\d|25[0-4]
                      )
                  )
                  |(?:
                     (?:
                       [a-z\u00a1-\uffff0-9]-*
                     )*
                     [a-z\u00a1-\uffff0-9]+
                   )
                   (?:
                     \.(?:
                         [a-z\u00a1-\uffff0-9]-*
                       )*
                     [a-z\u00a1-\uffff0-9]+
                   )*
                   (?:
                     \.(?:
                         [a-z\u00a1-\uffff]{2,}
                       )
                   )\.?
                )
                (?:
                  :\d{2,5}
                )?
                (?:
                  [\/?#]\S*
                )?""", re.X)
irc_nick_match = re.compile(
    '^\A[a-zа-я_\-\[\]\\^{}|`][a-zа-я0-9_\-\[\]\\^{}|`]{2,15}$', re.IGNORECASE | re.UNICODE)
domain_match = re.compile(
    '^(?!:\/\/)([a-zA-Z0-9-_]+\.)*[a-zA-Z0-9][a-zA-Z0-9-_]+\.[a-zA-Z]{2,11}?$', re.IGNORECASE)

shrugs = [
    '┻━┻︵ \(°□°)/ ︵ ┻━┻',
    '¯\_(ツ)_/¯',
    '┻━┻︵¯\_(ツ)_/¯︵┻━┻'
]


def whois(irc: kirc.Irc, target: str):
    whois = {}
    irc.send('WHOIS %s' % target)
    while True:
        msgs = irc.wait_data()
        for msg in msgs.split('\r\n'):
            kirc.pretty_print(msg)
            command = kirc.Parse(msg).command
            if command == '318' or command == '401':
                break
            elif command == '311':
                words = msg.split()
                whois['nick'] = words[3]
                whois['username'] = words[4][1:]
                whois['ip'] = words[5]
                whois['realname'] = words[7][1:]
            elif command == '319':
                whois['channels'] = msg.split(':')[2][:-2].split()
            elif command == '312':
                whois['server'] = msg.split()[4]
            elif command == '223':
                whois['charset'] = msg.split()[6]
            elif command == '317':
                words = msg.split()
                try:
                    whois['seconds idle'] = float(words[4])
                    whois['signon time'] = float(words[5])
                except IndexError as error:
                    print(error)
        else:
            continue
        break
    return whois


class Stat(peewee.Model):
    rowid = peewee.PrimaryKeyField()
    nick = peewee.CharField()
    join_count = peewee.IntegerField(default=1)
    symbols_count = peewee.IntegerField(default=0)
    msg_count = peewee.IntegerField(default=0)
    words_count = peewee.IntegerField(default=0)

    class Meta:
        database = peewee.SqliteDatabase('/media/kupp/Files/stat.sqlite')
        db_table = 'stat'


def collect_stat(irc: kirc.Irc, msg: str):
    msg_content = kirc.Parse(msg).content.replace(
        'ACTION \x01', '').replace('\x01', '')
    if irc.is_privmsg(msg, private=False):
        try:
            row = Stat.get(Stat.nick == irc.get_nick(msg).lower())
        except peewee.DoesNotExist:
            Stat.create(nick=irc.get_nick(msg).lower(),
                        symbols_count=len(msg_content) -
                        msg_content.count(' '),
                        msg_count=1,
                        words_count=len(msg_content.split()))
        else:
            row.symbols_count += len(msg_content) - msg_content.count(' ')
            row.msg_count += 1
            row.words_count += len(msg_content.split())
            row.save()
    elif irc.is_join(msg):
        try:
            row = Stat.get(Stat.nick == irc.get_nick(msg).lower())
        except peewee.DoesNotExist:
            Stat.create(nick=irc.get_nick(msg).lower())
        else:
            row.join_count += 1
            row.save()


def delay2str(delay):
    """convert seconds to pretty string with hours, days and seconds, for delay notice"""
    seconds = int(delay)
    minutes = 0
    hours = 0
    days = 0
    if seconds > 60:
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
    if minutes > 60:
        hours = int(minutes // 60)
        minutes = int(minutes % 60)
    if hours > 24:
        days = int(hours // 24)
        hours = int(hours % 24)
    if days == 0:
        if hours == 0:
            if minutes == 0:
                if seconds == 0:
                    return '0'
                else:
                    return '%s seconds' % str(seconds)
            else:
                if seconds == 0:
                    return '%s minutes' % str(minutes)
                else:
                    return '%s minutes, %s seconds' % (str(minutes), str(seconds))
        else:
            if minutes == 0:
                return '%s hours' % str(hours)
            else:
                return '%s hours, %s minutes' % (str(hours), str(minutes))
    else:
        if hours == 0:
            if minutes == 0:
                return '%s days' % str(days)
            else:
                return '%s days, %s minutes' % (str(days), str(minutes))
        else:
            if minutes == 0:
                return '%s days, %s hours' % (str(days), str(hours))
            else:
                return '%s days, %s hours, %s minutes' % (str(days), str(hours), str(minutes))


def cooldown_answer(cooldowns: dict, timer: int, value: str):
    if timer != 0:  # если кулдаун 0, то и проверять нечего
        if value in cooldowns:  # если запись найдена
            # если срок кулдауна истек
            if time.time() - cooldowns[value] >= timer:
                cooldowns[value] = time.time()  # то обновляем его
                return True  # даем добро
            else:  # если срок не истек
                return False  # запрещаем
        else:  # если запись не найдена
            cooldowns[value] = time.time()  # создаем ее
            return True
    else:
        return True


latest_ver = None
latest_time = None
latest_ping = None

with open('dr_cox_quotes.txt', 'r') as text_file:
    cox_quotes = text_file.readlines()
quote_cooldown = 15 * 60
quote_cooldowns = {}

with open('ipstack_token.txt', 'r') as text_file:
    ipstack_token = text_file.readline()

kitty_ = [
    'присела ему на ручки и стала мурлыкать ^~ᴥ~^ «Мууур-рр»',
    'с визгом в него вцепилась',
    'приземлилась рядом и решила его игнорировать',
]

cutlet_ = [
    'попал в лицо',
    'попал в глаз',
    'попал в руку',
    'промахнулся…',
    'не попал…',
    'попал в ногу',
    'попал в живот',
    'попал в спину',
    'попал в голубя, летевшего мимо',
    'попал в пах',
    'попал в пятую точку',
    'попал в ухо',
    '...\x0304Headshot!\x03'
]

udp_ = [
    'и тот не дошел',
    'и тот дошел'
]


class Commands():
    """
    Класс, в котором представлены все команды.
    Все команды вызываются только из экземпляра класса CommandCore (класс внизу).
    Класс Commands соображен так, чтобы не иметь экземпляров и предоставлять каждой команде одинаковый интерфейс.
    Формат класса таков, что каждый отдельный метод - отдельная команда. Каждый метод способен работать со
    следующими входными данными:
        irc - ссылка на основной класс, из которого производится работа с irc (описан в kirc.py),
        recipient - куда следует отправить команду, может быть ником или каналом,
        args - аргументы пользователя к команде,
        nick - ник вызвавшего команду.
    Каждая команда имеет параметры:
        pub_use: использование на каналах (True или False)
        priv_use: использование в привате с ботом (True или False)
        pub_cooldown: задержка для использования команды на каналах для каждого пользователя (в секундах >=0)
        priv_cooldown: задержка на использование в привате для конкретного пользователя (в секундах >= 0)
    Особое внимание следует уделить параметру regexp - индивидуальная регулярка для каждой команды. По умолчанию
    команде даётся регулярка «^[префикс][названия метода команды]», если указать параметр regexp то регулярк
    сгенерируется в виде «^[prefix][всё из параметра regexp]».
    Пользовательские аргументы к команде разделяются в соответствии с группами в регулярке. В качестве аргументов
    подаются все группы.
    Все параметры команд для команд статичны и не могут быть изменены в ходе исполнения.
    Все параметры задаются после функций в виде статических переменных, например:
        def test(self)
            . . . тело команды . . .
        test.pub_use = False
        test.priv_cooldown = 90
    Команда может не иметь параметров в этом классе, тогда класс CommandsCore при анализе выдаст команде
    стандартное значение параметра (стандартные значения описаны в CommandsCore).
    Все параметры анализируются классом CommandCore.
    Все нюансы входных данных команд, их параметров и случаи вызова описаны в классе CommandsCore.
    """

    def __init__(self, irc: kirc.Irc, recipient: str, args: list, nick: str, commands_info: list):
        self.irc = irc
        self.recipient = recipient
        self.args = args
        self.nick = nick
        self.commands_info = commands_info

    def help_command(self):
        if self.args[0]:
            try:
                self.commands_info[self.args[0]]
            except KeyError:
                self.irc.send_notice(
                    self.nick, 'No such command %s' % self.args[0])
            else:
                command = self.args[0]
                command_method = getattr(self, command)
                self.irc.send_notice(self.nick, 'description: %s' %
                                     getattr(command_method, '__doc__'))
                for parameter in self.commands_info[command]:
                    self.irc.send_notice(self.nick, '%s: %s' % (
                        parameter, self.commands_info[command][parameter]))
        else:
            self.irc.send_notice(self.nick, 'I have several commands: %s' % ', '.join(
                list(self.commands_info.keys())))
            self.irc.send_notice(
                self.nick, 'Send [help command] [command] for more information')
    help_command.regexp = 'help(?:\s+(.+))?'
    help_command.pub_cooldown = 5

    def test(self):
        """Тестовая команда"""
        self.irc.send_privmsg(self.recipient, 'It Works!')

    def echo(self):
        string = self.args[0]
        if string:
            self.irc.send_privmsg(self.recipient, self.args[0].strip())
    echo.regexp = 'echo(?:\s+(.+))'
    echo.priv_use = False
    echo.pub_cooldown = 300

    def uptime(self):
        """Аптайм бота"""
        seconds = int(time.time() - self.irc.start_time)
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
        self.irc.send_privmsg(
            self.recipient, 'Bot uptime: %d days, %d hours, %d minutes' % (days, hours, minutes))

    def version(self):
        global latest_ver
        target = self.args[0] or self.nick
        self.irc.send_privmsg(target, '\x01VERSION\x01')
        latest_ver = (self.recipient, time.time(), target)
    version.regexp = '(?:(?:чоза\S*)|(?:ver(?:sion)?))(?: +(\S+))?'

    def time(self):
        global latest_time
        target = self.args[0] or self.nick
        self.irc.send_privmsg(target, '\x01TIME\x01')
        latest_time = (self.recipient, time.time(), target)
    time.regexp = '(?:time|время)(?:\s+(\S+)?)?'

    def ping(self):
        global latest_ping
        target = self.args[0] or self.nick
        self.irc.send_privmsg(target, '\x01PING %f\x01' % time.time())
        latest_ping = (self.recipient, time.time(), target)
    ping.regexp = '(?:ping|пинг)(?:\s+(\S+)?)?'

    def Coxy(self):
        global cox_quotes
        global quote_cooldown
        global quote_cooldowns
        if self.args[0]:
            try:
                self.irc.send_privmsg(
                    self.recipient, cox_quotes[int(self.args[0])])
            except IndexError:
                self.irc.send_privmsg(
                    self.recipient, 'Cant find %s' % self.args[0])
        else:
            for _ in range(100):
                i = random.randint(0, len(cox_quotes) - 1)
                if cooldown_answer(quote_cooldowns, quote_cooldown, i):
                    break
            else:
                return
            self.irc.send_privmsg(self.recipient, cox_quotes[i])
    Coxy.regexp = 'Coxy(?:\s+(-?\d+)?)?'

    def whois(self):
        target = self.args[0] or self.nick
        self.irc.send_privmsg(self.recipient, str(whois(self.irc, target)))
    whois.regexp = 'whois(?:\s+(\S+)?)?'

    def ip(self):
        """geoip"""
        global ipstack_token
        global ip_match
        global url_match
        global domain_match
        global irc_nick_match
        import urllib.request
        import urllib.error
        import json
        import socket
        target = self.args[0] or self.nick
        if irc_nick_match.search(target):
            try:
                address = whois(self.irc, target)['ip']
                print('address is ' + address)
            except KeyError:
                return
        else:
            address = target
        is_url = url_match.search(address)
        if is_url:
            ip = socket.getaddrinfo(is_url.group(2), 80)[2][4][0]
        elif domain_match.search(address):
            ip = socket.getaddrinfo(address, 80)[2][4][0]
        elif ip_match.search(address):
            ip = address
        else:
            return
        api = 'http://api.ipstack.com/%s?access_key=%s&format=1' % (
            ip, ipstack_token)
        info = urllib.request.urlopen(api).read()
        info = info.decode()
        info = json.loads(info)
        self.irc.send_privmsg(self.recipient, str(info))
    ip.regexp = 'ip(?:\s+(\S+)?)?'
    ip.pub_use = False

    def kitty(self):
        """Бросание котиками"""
        global kitty_
        target = self.args[0] or self.nick
        self.irc.send_action(self.recipient, 'кинул кошечку в %s, та %s' % (
            target, random.choice(kitty_)))
    kitty.regexp = '(?:kitty|киска)(?:\s+(\S+)?)?'
    kitty.priv_use = False

    def slap(self):
        """Classic slap"""
        target = self.args[0] or self.nick
        thing = self.args[1] or 'large trout'
        self.irc.send_action(
            self.recipient, 'slaps %s around a bit with a %s' % (target, thing))
    slap.regexp = 'slap(?:\s+(\S+)?(?:\s+)?(.+)?)?'
    slap.priv_use = False

    def poke(self):
        """Classic poke"""
        target = self.args[0] or self.nick
        self.irc.send_action(self.recipient, 'pokes %s' % target)
    poke.regexp = 'poke(?:\s+(.+)?)?'
    poke.priv_use = False

    def badum_ts(self):
        self.irc.send_privmsg(self.recipient, 'https://goo.gl/D7SQSc')

    def shrug(self):
        global shrugs
        self.irc.send_privmsg(self.recipient, random.choice(shrugs))

    def cutlet(self):
        global cutlet_
        target = self.args[0] or self.nick
        self.irc.send_action(self.recipient, 'Кинул котлетой в %s и %s' % (
            target, random.choice(cutlet_)))
    cutlet.regexp = '(?:котле\S+|cutle\S+)(?:\s+(.+)?)?'
    cutlet.priv_use = False

    def hi(self):
        global cutlet_
        target = self.args[0] or self.nick
        self.irc.send_action(self.recipient, 'Кинул приветом в %s и %s' % (
            target, random.choice(cutlet_)))
    hi.regexp = '(?:привет|hi)(?:\s+(.+)?)?'
    hi.priv_use = False

    def love(self):
        global cutlet_
        target = self.args[0] or self.nick
        self.irc.send_action(self.recipient, 'Кинул приветом в %s и %s' % (
            target, random.choice(cutlet_)))
    hi.regexp = '(?:привет|hi)(?:\s+(.+)?)?'
    hi.priv_use = False


    def tg(self):
        self.irc.send_privmsg(self.recipient, 'https://t.me/sixteen_bits')

    def steam(self):
        self.irc.send_privmsg(
            self.recipient, 'https://steamcommunity.com/groups/BochaClub')

    def udp(self):
        global udp_
        target = self.args[0] or self.nick
        self.irc.send_action(self.recipient, 'Кинул udp-пакетом в %s… %s' %
                             (self.args[0], random.choice(udp_)))
    udp.regexp = 'udp(?:\s+(.+)?)?'

    def stat(self):
        target = self.args[0] or self.nick
        try:
            row = Stat.get(Stat.nick == target.lower())
        except peewee.DoesNotExist:
            irc.send_privmsg(self.recipient, 'No such user')
        else:
            try:
                wpm = row.words_count / row.msg_count
            except ZeroDivisionError:
                wpm = 0
            self.irc.send_privmsg(
                self.recipient, '\x02%s\x02 send %d words, %d messages, %d symbols (\x02%.2f\x02 wpm) and join %d times' %
                (target, row.words_count, row.msg_count,
                 row.symbols_count, wpm, row.join_count)
            )
    stat.regexp = '(?:stat|писямерка)(?:\s+(\S+)?)?'

    def top_msg(self):
        top = Stat.select().order_by(Stat.msg_count.desc()).limit(5)
        self.irc.send_privmsg(self.recipient, 'Top 5 flooders by message count: \x0304%s\x03: %d, %s: %d, %s: %d, %s: %d, %s: %d' % (
            top[0].nick, top[0].msg_count,
            top[1].nick, top[1].msg_count,
            top[2].nick, top[2].msg_count,
            top[3].nick, top[3].msg_count,
            top[4].nick, top[4].msg_count,
        ))
    top_msg.regexp = '(?:top5msg|самая_длинная_писька)(\s+)?'

    def top_words(self):
        top = Stat.select().order_by(Stat.words_count.desc()).limit(5)
        self.irc.send_privmsg(self.recipient, 'Top 5 flooders by words count: \x0304%s\x03: %d, %s: %d, %s: %d, %s: %d, %s: %d' % (
            top[0].nick, top[0].words_count,
            top[1].nick, top[1].words_count,
            top[2].nick, top[2].words_count,
            top[3].nick, top[3].words_count,
            top[4].nick, top[4].words_count,
        ))
    top_words.regexp = '(?:top5words|самая_толстая_писька)(\s+)?'

    def top_sym(self):
        top = Stat.select().order_by(Stat.symbols_count.desc()).limit(5)
        self.irc.send_privmsg(self.recipient, 'Top 5 flooders by symbols count: \x0304%s\x03: %d, %s: %d, %s: %d, %s: %d, %s: %d' % (
            top[0].nick, top[0].symbols_count,
            top[1].nick, top[1].symbols_count,
            top[2].nick, top[2].symbols_count,
            top[3].nick, top[3].symbols_count,
            top[4].nick, top[4].symbols_count,
        ))
    top_sym.regexp = '(?:top5sym|самая_смачная_писька)(\s+)?'

    def top_join(self):
        top = Stat.select().order_by(Stat.join_count.desc()).limit(5)
        self.irc.send_privmsg(self.recipient, 'Top 5 flooders by join count: \x0304%s\x03: %d, %s: %d, %s: %d, %s: %d, %s: %d' % (
            top[0].nick, top[0].join_count,
            top[1].nick, top[1].join_count,
            top[2].nick, top[2].join_count,
            top[3].nick, top[3].join_count,
            top[4].nick, top[4].join_count,
        ))
    top_join.regexp = '(?:top5join|самая_популярная_писька)(\s+)?'


class Bot():
    """
    Данный класс требует, в отличии от Commands (выше) создания экземпляра.
    Основная идея: в теле бота создается экземпляр данного класса. Далее в основной цикл вставляется лишь одна строчка:
    вызов основного метода данного класса (метод search).
    В этом классе обрабатываются сообщения поступившие из irc. В этих сообщения производится поиск вызова команд,
    которые описаны в классе Commands и анализируются специфические параметры команд (описаны в Commands).
    Данный класс не универсален, так как основан на некоторой специфике irc, т.е. на разделение на каналы и на приват.
    В случае если по всем параметрам необходимо вызвать команду то она вызывается. Определение вызова команды проходит в
    несколько этапов:
        1. Поиск запроса команды (метод call_search) по индивидуальной регулярке.
        2. Проверка прав (параметры priv_use и pub_use, метод rights_check). Команда может быть запрещена к использованию
           либо на каналах либо в привате с ботом. Это и обрабатывается на данном этапе
        3. Проверка может ли данный пользователь вызвать команду (метод cooldown_check). Каждая команда имеет кулдаун
           (он же делей) или не имеет, если он равен 0. Кулдаун считается для каждого пользователя на каждом канале и в
           привате по отдельности. Кулдаун для отдельных каналов или пользователей не предусмотрен.
        4. Проверка введено ли пользователем необходимое количество аргументов (метод args_check) для данной команды.
           Правильность аргументов на данном этапе не проверяется, этим занимаются сами методы команд, описанные в
           классе Commands.
    Все проверяется сверху вниз. Если что-то не соответствует, то проверка прерывается и метод команды не вызывается.
    Все нюансы этапов описаны в методах ниже.
    """

    def __init__(self, irc: kirc.Irc, prefix: str):
        # специфическая регулярка для отбора всех методов команд из класса Commands
        r = re.compile('__.*__')
        self.irc = irc
        self.commands = [method for method in dir(
            Commands) if not r.search(method)]
        """
        В строчке выше быстрым созданием списка отбираются все методы из класса Commands, которые не соответствуют
        регулярке __.*__ (в таком формате называются все зарезервированные-встроенные методы классов, смотрите
        специфику python3).
        В список commands отбираются только имена методов. Далее они используются как имена команд.
        """
        self.prefix = re.escape(prefix)

        """
        Ниже заданы стандартные значения параметров для команд.
        Значения параметров описаны в Commands.
        """
        default_parameters = {
            'default_pub_use': True,
            'default_priv_use': True,
            'default_pub_cooldown': 120,
            'default_priv_cooldown': 0
        }
        self.commands_info = {}  # создаем пустой словарь для параметров
        parameters = [
            'pub_use',
            'priv_use',
            'pub_cooldown',
            'priv_cooldown'
        ]
        for command in self.commands:
            self.commands_info[command] = {}
            command_method = getattr(Commands, command)
            for parameter in parameters:
                try:  # пробуем запросить параметр команды
                    self.commands_info[command][parameter] = getattr(
                        command_method, parameter)
                except AttributeError:  # если его нет, то присваиваем стандартное значение
                    self.commands_info[command][parameter] = default_parameters['default_%s' % parameter]
            try:
                self.commands_info[command]['regexp'] = re.compile(
                    '^%s%s(?:\s+)?$' % (self.prefix, getattr(command_method, 'regexp')))
            except AttributeError:
                self.commands_info[command]['regexp'] = re.compile(
                    '^%s%s(?:\s+)?$' % (self.prefix, command))

            self.commands_info[command]['pub_cooldown_string'] = delay2str(
                self.commands_info[command]['pub_cooldown'])
            self.commands_info[command]['priv_cooldown_string'] = delay2str(
                self.commands_info[command]['priv_cooldown'])
            """Создается строка, где текстом написан кулдаун."""

        self.cooldowns = {}  # кулдауны
        self.ctcp_ans_match = re.compile(r'\x01([A-Z^ ]+)(?: +)(.+)\x01')
        """Все кулдауны записываются обрабатываются специфически, описание в методах cooldown и cooldown_check"""

    def right_check(self, command: str):
        if self.is_private:
            if self.commands_info[command]['priv_use']:
                return True
            else:
                self.irc.send_privmsg(
                    self.nick, '%s only for public' % command)
                return False
        else:
            if self.commands_info[command]['pub_use']:
                return True
            else:
                self.irc.send_privmsg(
                    self.nick, '%s only for private' % command)
                return False

    def cooldown_check(self, command: str):
        """
        Проверка кулдауна.
        Кулдаун записывается следующим образом:
            1. В качестве ключа выступает специфическая запись, которая характеризует к чему она относится.
               Записи для каналов выглядят следующим образом Имя-сети_Имя-команды_Канал_Ник. Таким образом кулдаун
               записывается для каждого пользователя на каждом канале в отдельности. Запись для привата же выглядит
               немного иначе Имя-сети_Имя-команды_Ник_Ник. Это происходит из-за того, что recipient совпадает c nick и поэтому
               запись дублируется. Пусть хранятся лишний символ ключах, а код остается понятнее.
            2. В качестве значения выступает время последнего успешного использования пользователем команды. Т.е. если
               пользователь пытается использовать команду, чей кулдаун еще не прошел, то запись в кулдауне не
               обновляется. Подробнее смотрите в методе cooldown
        """
        if self.is_private:
            self.recipient = self.nick
            string = self.commands_info[command]['priv_cooldown_string']
            cooldown = self.commands_info[command]['priv_cooldown']
        else:
            self.recipient = self.channel
            string = self.commands_info[command]['pub_cooldown_string']
            cooldown = self.commands_info[command]['pub_cooldown']
        if cooldown_answer(self.cooldowns, cooldown, '%s_%s_%s_%s' % (self.irc.name, command, self.recipient, self.nick)):
            return True
        else:
            self.irc.send_notice(self.nick, 'delay: %s' % string)
            return False

    def call_search(self, msg: str):
        command = None
        for command_i in self.commands:
            call = self.commands_info[command_i]['regexp'].search(self.content)
            if call:
                self.args = call.groups()
                command = command_i
                break
        return command

    def do(self, msg: str):
        global latest_ver
        global latest_time
        global latest_ping
        self.is_private = self.irc.is_privmsg(msg, private=True)
        self.nick = self.irc.get_nick(msg)
        self.channel = self.irc.get_msg_channel(msg)
        collect_stat(self.irc, msg)
        self.content = kirc.Parse(msg).content
        ctcp_ans = self.ctcp_ans_match.search(self.content)
        if ctcp_ans and kirc.Parse(msg).command == 'NOTICE':
            grps = ctcp_ans.groups()
            ctcp = grps[0]
            text = grps[1].strip()
            if ctcp == 'VERSION':
                if latest_ver and time.time() - latest_ver[1] < 300 and self.nick == latest_ver[2]:
                    self.irc.send_privmsg(latest_ver[0], '%s VERSION: %s' % (
                        irc_format.IrcTextFormat(latest_ver[2]).bold, text))
                    latest_ver = None
            elif ctcp == 'TIME':
                if latest_time and time.time() - latest_time[1] < 300 and self.nick == latest_time[2]:
                    self.irc.send_privmsg(latest_time[0], '%s TIME: %s' % (
                        irc_format.IrcTextFormat(latest_time[2]).bold, text))
                    latest_time = None
            elif ctcp == 'PING':
                if latest_ping and time.time() - latest_ping[1] < 300 and self.nick == latest_ping[2]:
                    self.irc.send_privmsg(latest_ping[0], '%s PING: %.3f' % (
                        irc_format.IrcTextFormat(latest_ping[2]).bold, time.time() - latest_ping[1]))
                    latest_ping = None
        command = self.call_search(msg)
        if command:
            if self.right_check(command):
                if self.cooldown_check(command):
                    getattr(Commands(self.irc, self.recipient, self.args,
                                     self.nick, self.commands_info), command)()
