import kirc
import sys
import bot
import time

nick = 'Coxy'

irc = kirc.Irc('Rusnet', 'irc.run.net', 9996,
               nick, 'bot', 'kupp bot', 'utf-8', ssl_enable=True)
irc.connect(100, 100000)
irc.send('MODE %s +x' % nick)
irc.join('#16bits')
irc.join('#16bit')
c = bot.Bot(irc, '.')


def main_loop():
    while True:
        try:
            msgs = irc.wait_data()
            if msgs:
                for msg in msgs.split('\r\n'):
                    if msg:
                        irc.maintenance(msg)
                        kirc.pretty_print(msg.strip())
                        c.do(msg)
        except KeyboardInterrupt:
            irc.quit('Im part, but it doesnt mean that i crash')
            sys.exit()
        except kirc.IrcConnectionError:
            irc.reconnect(100, 100000)
            irc.join('#16bits')
            irc.join('#16bit')
            main_loop()
        except Exception as error:
            print(error)


main_loop()
