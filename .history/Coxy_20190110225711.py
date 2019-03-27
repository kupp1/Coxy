import kirc
import sys
import bot
import time

irc = kirc.Irc('Rusnet', 'irc.run.net', 6660,
               'Coxy_t', 'bot', 'kupp bot', 'utf-8')
irc.connect(100, 100000)
irc.join('#16bits')
irc.join('#16bit')
c = bot.Bot(irc, '.')
irc.send('MODE Coxy_t +x')

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
        except kirc.IrcConnectionError:
            irc.reconnect(100, 100000)
            irc.join('#16bits')
            irc.join('#16bit')
            main_loop()
        except Exception:
            pass


main_loop()
