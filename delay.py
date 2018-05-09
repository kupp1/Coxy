import datetime

def delay(list, time, timer, value):
    new_member = True
    OK = True
    if len(list) != 0:
        for i, _ in enumerate(list):
            if list[i] == value:
                new_member = False
                if (datetime.datetime.now() - time[i]) >= timer:
                    del list[i]
                    del time[i]
                    OK = True
                else:
                    OK = False
    else:
        OK = True
    if new_member == True:
        list.append(value)
        time.append(datetime.datetime.now())
    return OK

def last_force_del(list, time):
    del list[len(list) - 1]
    del time[len(time) - 1]