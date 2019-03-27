import kirc
import time
import re


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
        required_args: минимальное количество аргументов к команде (целое число >= 0)
        pub_cooldown: задержка для использования команды на каналах для каждого пользователя (в секундах >=0)
        priv_cooldown: задержка на использование в привате для конкретного пользователя (в секундах >= 0)
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

    def __init__(self, irc: kirc.Irc, recipient: str, args: list, nick: str):
        self.irc = irc
        self.recipient = recipient
        self.args = args
        self.nick = nick

    def test(self):
        """Тестовая команда"""
        self.irc.send_privmsg(self.recipient, 'It Works!')

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


class CommandsCore():
    """
    Данный класс требует, в отличии от Commands (выше) создания экземпляра.
    Основная идея: в теле бота создается экземпляр данного класса. Далее в основной цикл вставляется лишь одна строчка:
    вызов основного метода данного класса (метод search).
    В этом классе обрабатываются сообщения поступившие из irc. В этих сообщения производится поиск вызова команд,
    которые описаны в классе Commands и анализируются специфические параметры команд (описаны в Commands).
    Данный класс не универсален, так как основан на некоторой специфике irc, т.е. на разделение на каналы и на приват.
    В случае если по всем параметрам необходимо вызвать команду то она вызывается. Определение вызова команды проходит в
    несколько этапов:
        1. Поиск запроса команды (метод call_search). За специфическое сочетание-запрос, который ищется только в начале
           строки принимается название метода этой команды из класса Commands + необходимый перед этим именем
           команды префикс (указывается как параметр при создании экземпляра класса CommandsCore).
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
            for parameter in parameters:
                try:  # пробуем запросить параметр команды
                    self.commands_info[command][parameter] = getattr(Commands, 'Commands.%s.%s' % (command, parameter))
                except AttributeError:  # если его нет, то присваиваем стандартное значение
                    self.commands_info[command][parameter] = default_parameters['default_%s' % parameter]
            try:
                self.commands_info[command]['regexp'] = eval(
                    'Commands.%s.regexp' % command)
            except AttributeError:
                self.commands_info[command]['regexp'] = re.compile('^%s' % command)

            """
            В коде выше используется eval. Это зло, но что-то подобное в данном случае для анализа статических переменных
            другого класса необходимо. Отмечу, что в __dict__ статические переменные не отображаются. Именно сатические
            переменные выбраны в Commands для ввода комманд только из-за стилистики кода.
            """

            self.commands_info[command]['pub_cooldown_string'] = self.delay2str(
                self.commands_info[command]['pub_cooldown'])
            self.commands_info[command]['priv_cooldown_string'] = self.delay2str(
                self.commands_info[command]['priv_cooldown'])
            """Создается строка, где текстом написан кулдаун."""

        self.cooldowns = {}  # кулдауны
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

    @staticmethod
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

    @staticmethod
    def cooldown(cooldowns: dict, timer: int, value: str):
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
        if self.cooldown(self.cooldowns, cooldown, '%s_%s_%s_%s' % (self.irc.name, command, self.recipient, self.nick)):
            return True
        else:
            self.irc.send_notice(self.nick, 'delay: %s' % string)
            return False

    def call_search(self, msg: str):
        content = kirc.Parse(msg).content
        command = None
        for command_i in self.commands:
            call = self.commands_info[command]['regexp'].search(content)
            if call:
                self.args = call.groups()
                command = command_i
                break
        return command

    def search(self, msg: str):
        self.is_private = self.irc.is_privmsg(msg, private=True)
        self.nick = self.irc.get_nick(msg)
        self.channel = self.irc.get_msg_channel(msg)
        command = self.call_search(msg)
        if command:
            if self.right_check(command):
                if self.cooldown_check(command):
                    eval(
                        'Commands(self.irc, self.recipient, self.args, self.nick).%s()\n' % command)
