import kirc
import time

irc = kirc.Irc('Rusnet', 'irc.run.net', 6660,
               'kupp_of_santa', 'bot', 'kupp bot', 'utf-8')
irc.connect(100, 1000)
irc.join('#16bit')
times = [
    (1546300800 - (9*60*60), 'Якутск'),
    (1546300800 - (8*60*60), 'Иркутск'),
    (1546300800 - (7*60*60), 'Красноярск'),
    (1546300800 - (6*60*60), 'Омск'),
    (1546300800 - (5*60*60), 'Екатеринбург'),
    (1546300800 - (4*60*60), 'Самара'),
    (1546300800 - (3*60*60), 'Москва'),
    (1546300800 - (2*60*60), 'Калининград'),
    (1546300800 - (1*60*60), 'центральная европа'),
    (1546300800 - (0*60*60), 'Гринвичу')
    
]
for ny in times:
    ny_time, city = ny
    while time.time() < ny_time:
        pass
    irc.send_privmsg('#16bit', 'С новым годом %s!' % city)
irc.quit()