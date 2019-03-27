import kirc
import sys
import commands

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
                    kirc.pretty_print(msg.strip())
                    c.search(msg)
    except KeyboardInterrupt:
        irc.quit('Im part, but it doesnt mean that i crash')
    except kirc.IrcConnectionError:
        irc.reconnect(100, 1000)
