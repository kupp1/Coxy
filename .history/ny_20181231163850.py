import kirc
import time

irc = kirc.Irc('Rusnet', 'irc.run.net', 6660,
               'Santa_Claus', 'bot', 'kupp bot', 'utf-8')
irc.connect(100, 1000)
irc.join('#16bit')
while True:
    if time.time() >= 1546290000:
        irc.send_privmsg('#16bit', 'Happy new 1546290000!')
        time.sleep(1)
        irc.send_privmsg('#16bit', 'Спешу поздравить дорогих сочатовцев с новым годом. Счастья, здоровья, хороших гаджетов и тяночек! (с) uncle_kupp')
        irc.quit('Ушел разносить подарки')