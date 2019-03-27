import kirc
import sys
import bot
import time

irc = kirc.Irc('Rusnet', 'irc.run.net', 6660,
               'Coxy_t', 'bot', 'kupp bot', 'utf-8')
irc.connect(100, 100000)
irc.join('#16bits')
# irc.join('#16bit')
c = bot.Bot(irc, '.')

def try_repeat(func):
    def wrapper(*args, **kwargs):
        count = 10

        while count:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print('Error:', e)
                count -= 1

    return wrapper

def main_loop():
    while True:
        msgs = irc.wait_data()
        if msgs:
            for msg in msgs.split('\r\n'):
                if msg:
                    irc.maintenance(msg)
                    kirc.pretty_print(msg.strip())
                    c.do(msg)

def reconnect():
    irc.reconnect(100, 100000)

def start():
    try:
        main_loop()
    except KeyboardInterrupt:
        irc.quit('Im part, but it doesnt mean that i crash')
    except kirc.IrcConnectionError:
        try:
            reconnect()
        except OSError:
            time.sleep(10)
            reconnect()
        irc.join('#16bits')
        # irc.join('#16bit')
        main_loop()
    except Exception:
        pass
    else:
        kirc.pretty_print('WHAT THE FUCK IS THIS?! IT CANT HAPPEN!')
