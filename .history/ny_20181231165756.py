import kirc
import time

irc = kirc.Irc('Rusnet', 'irc.run.net', 6660,
               'kupp_of_santa', 'bot', 'kupp bot', 'utf-8')
irc.connect(100, 1000)
irc.join('#16bit')
while time.time() < 1546286400:
    pass
irc.send_privmsg('#16bit', 'С новым годом Калининград!')
 #   elif time.time() >= 1546290000:
 #       irc.send_privmsg('#16bit', 'Happy new 1546290000!')
 #       time.sleep(1)
 #       irc.send_privmsg('#16bit', 'Спешу поздравить дорогих сочатовцев с новым годом. Счастья, здоровья, хороших гаджетов и тяночек! (с) uncle_kupp')
 #   elif time.time() >= 1546293600