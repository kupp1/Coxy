import kirc
import sys
import commands
import peewee

class Stat(peewee.Model):
    rowid = peewee.PrimaryKeyField()
    nick = peewee.CharField()
    join_count = peewee.IntegerField(default=1)
    symbols_count = peewee.IntegerField(default=0)
    msg_count = peewee.IntegerField(default=0)
    words_count = peewee.IntegerField(default=0)

    class Meta:
        database = peewee.SqliteDatabase('stat.sqlite')
        db_table = 'stat'

stat_ch = ['###kupp_tests']

def collect_stat(irc: kirc.Irc, msg_content: str):
    if irc.is_privmsg(msg) and (irc.get_msg_channel(msg) in stat_ch):
        try:
            row = Stat.get(Stat.nick == irc.get_nick(msg).lower())
        except peewee.DoesNotExist:
            Stat.create(nick=irc.get_nick(msg).lower(),
                        symbols_count=len(msg_content) - msg_content.count(' '),
                        msg_count=1,
                        words_count=len(msg_content.split()))
        else:
            row.symbols_count += len(msg_content) - msg_content.count(' ')
            row.msg_count += 1
            row.words_count += len(msg_content.split())
            row.save()
    elif irc.is_join(msg) and (irc.get_msg_channel(msg) in stat_ch):
        try:
            row = Stat.get(Stat.nick == irc.get_nick(msg).lower())
        except peewee.DoesNotExist:
            Stat.create(nick=irc.get_nick(msg).lower())
        else:
            row.join_count += 1
            row.save()

irc = kirc.Irc('Rusnet', 'irc.run.net', 6660,
               'Coxy_t', 'bot', 'kupp bot', 'utf-8')
irc.connect(100, 1000)
# irc.join('#16bits')
irc.join('###kupp_tests')
c = commands.CommandsCore(irc, '.')
while True:
    try:
        msgs = irc.wait_data()
        if msgs:
            for msg in msgs.split('\r\n'):
                if msg:
                    irc.maintenance(msg)
                    # collect_stat(irc, kirc.Parse(msg).content)
                    kirc.pretty_print(msg.strip())
                    c.search(msg)
    except KeyboardInterrupt:
        irc.quit('Im part, but it doesnt mean that i crash')
    except kirc.IrcConnectionError:
        irc.reconnect(100, 1000)
