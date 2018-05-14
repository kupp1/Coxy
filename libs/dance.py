# lib bot chose dancer of the day, all strings on russian
import random

dances_base = open('./libs/dances_list.txt', 'r')
dances = dances_base.readlines()

dance_1 = [
    'Хей, народ! Сейчас я запускаю танцыыы! И не говорите, что не хотели! Я прихожожу, когда зовут!',
    'Опаньки… я уж и не думал, что в этом сборище кто-то хочет настоящик потанцулек',
    'Я так рад наконец, прибыв в ваше захослустье! Ну чо, бабки! Хватайте дедушек, будем сейчас ритм давать!',
    'Бебебе. Опять этот. Ну сколько можно, я вообще человек занятой… хотя ладно, погнали, чо уж там',
    'Ну! Кто тут такой миленький, а? Захотел танцевать? А не моловат еще? Да не моловат, во как двигается! Погнали!',
    'Динь! Динь! Вы меня звали? Знаю, что звали! Ну что?! Закатим тусуху с чем там у вас положено… ',
    'Првет! Я не готов, но я импровизирую! Так что будте готовы к чему угодно!',
    'Все свои члены собрали? Потому что я уже тут! Надо быть готовым! Давайте, покажем им, кто тут настоящий герой дня!',
    'Я же просил не отрывать меня когда ни попадя! Я делаю большое одолжение вам, устраивая праздник! В ноги клонитесь!',
    'Наконец вы позвали профи! Я не вижу софитов, я не вижу сцены! Где они? Ладно. Давайте танцевать тут…'
]

dance_2 = [
    'Сейчас я сделаю что-то нереально крутое!',
    'Беригите свои глазки, ибо сейчас будет ярко-ярко!',
    'Даже тут можно сделать что-то. Вы готовы, деревенщина? Давайте, доедайте пельмеши и на ноги!',
    'Я же сказал, чтоб меня ждали! Ишь! Какие невоспитанные! Ну ничего. Я прощаю вас. А теперь я тут задаю моду!',
    'Все готовы к этому действию! Отлично! Сейчас надо будет очень много двигаться! готовьте подзарядку!',
    'Я не думал что все будет с вами так плохо. Как получится, так и пойдем дальше, но чур не останавливаться!',
    'Воу! Не стоило, не стоило. Я всегда это знал. А теперь позвольте! Маэстро готов!',
    'Но как нибудь сможите. Найдите в себе силы. Это будет нелегко, но зато будет что вспомнить! Давай, детка!',
    'На часах… черт, не могу эти цифры разробрать. Короче! Самое время одеть свои наряды!',
    'Вы готовы дети?! Я вас не слыыышу! Вот так хорошо. Руки в боки и вперед плясать!'
]

top_end = [
    'Вот. Верхушечка.',
    'Вам еще учится и учится!',
    'Надо знать своих героев!',
    'Надо знать своих танцоров!',
    'Хочешь попасть? Дождись, когда Маэстро тут будет.',
    'Легенды…',
    'Легенды танца!',
    'Учитесь!'
]

top_start = [
    'Покажу вам верхушечку:',
    'Интересно? Вот вам первые 5:',
    'Легенды! Они тут:',
    'Вот! Красавцы:',
    'Огонь юзеры:',
    'Cейчас покажется головка!.. списка топ танцоров конечно',
    'Лучшие танцоры:',
    'Топ-5 танцоров:'
]

def get_dance_1():
    return dance_1[random.randint(0, len(dance_1)-1)]

def get_dance_2():
    return dance_2[random.randint(0, len(dance_2)-1)]

def get_dance_3(names, bot_nick):
    dancer = names[random.randint(0, len(names) - 1)]
    while dancer == bot_nick:
        dancer = names[random.randint(0, len(names) - 1)]
    dance = dances[random.randint(0, len(dances)-1)][:-1]
    dance_3 = [
        'А теперь на танцполе \x0313' + dancer + '\x03 И он пригтовил для нас \x0304' + dance + '\x03',
        'А зажжет особый человек! \x0312' + dancer + '\x03! Готовься танцевать \x0304' + dance + '\x03!',
        'Хочешь ты того, \x0303' + dancer + '\x03, или нет, но очередь твоя! Готовься танцевать \x0304' + dance + '\x03!',
        'Все наше внимание займет \x0313' + dancer + '\x03 с танцем \x0304' + dance + '\x03!',
        'Еее! Я знаю, \x0313' + dancer + '\x03, ты ждал случая! Танцуй \x0304' + dance + '\x03!',
        '\x0313' + dancer + '\x03! Dance, dance, dance, как было в книге Мураками! Танцуй нам \x0304' + dance + '\x03!'
    ]
    write_top_dancers(dancer)
    return dance_3[random.randint(0, len(dance_3)-1)]

def write_top_dancers(dancer):
    dances_top_base = open('./libs/dances_top.txt')
    dances_top = dances_top_base.readlines()
    for i in range(len(dances_top)):
        dances_top[i] = dances_top[i][:-1]
    new_member = True
    for i in range(len(dances_top)):
        if dances_top[i].split()[0] == dancer:
            new_member = False
            dances_top[i] = dancer + ' ' + str(int(dances_top[i].split()[1])+1)
    if new_member == True:
        dances_top.append(dancer + ' ' + '1')
    dances_top_base_w = open('./libs/dances_top.txt', 'w')
    dances_top.sort(key=lambda x: x.split()[1], reverse=True)
    print(dances_top)
    dances_top = map(lambda x: x + '\n', dances_top)
    dances_top_base_w.writelines(dances_top)

def get_top_dacers():
    dances_top_base = open('./libs/dances_top.txt')
    dances_top = dances_top_base.readlines()
    for i in range(len(dances_top)):
        dances_top[i] = dances_top[i][:-1]
    return dances_top[0:4]

def get_top_start():
    return top_start[random.randint(0, len(top_start) - 1)]

def get_top_end():
    return top_end[random.randint(0, len(top_end) - 1)]