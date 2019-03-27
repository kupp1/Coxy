import kirc
import sys
import bot

irc = kirc.Irc('Rusnet', 'irc.run.net', 6660,
               'Coxy_t', 'bot', 'kupp bot', 'utf-8')
irc.connect(100, 100000)
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
        except kirc.IrcConnectionError:
            irc.reconnect(100, 100000)
            irc.join('#16bits')
            irc.join('#16bit')
            main_loop()
        else:
            kirc.pretty_print('WHAT THE FUCK IS THIS?! IT CANT HAPPEN!')

try:
    main_loop()
else:
    main_loop()
