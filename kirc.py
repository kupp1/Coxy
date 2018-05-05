import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def join(sock, channels): #join to channels, get list of channels
    for i in range(len(channels)):
        sock.send(('JOIN ' + channels[i] + '\r\n').encode())
        print('join to ' + channels[i])

def rejoin(sock, channel): #auto rejoin, get one channel
    sock.send(('JOIN ' + channel + '\r\n').encode())
    print('rejoin to ' + channel)

def connect(sock, host, port, nick, username, realname): #connect to server
    print('soc created |', sock)
    remote_ip = socket.gethostbyname(host)
    print('ip of irc server is:', remote_ip)
    sock.connect((host, port))
    print('connected to: ', host, port)
    nick_cr = ('NICK ' + nick + '\r\n').encode()
    sock.send(nick_cr)
    usernam_cr = ('USER ' + username + ' ' + username + ' ' + username + ' ' + ':' + realname + ' \r\n').encode()
    sock.send(usernam_cr)

def sender_nick_find(data): #find nick in irc data
    nick = ''
    for i in range(len(data)):
        if (i > 0) and (data[i] != '!'):
            nick += data[i]
        elif data[i] == '!':
            break
    return nick

def sender_ch_find(data): #find sender channel
    ch = ''
    n1 = 0
    for n in range(len(data)):
        if data[n] == '#':
            n1 = n
    while data[n1] != ' ':
        ch += data[n1]
        n1 += 1
    return ch

def privmsg_cut(sock, recipient, text, start, end): # cut long messages
    if sys.getsizeof(str('PRIVMSG ' + recipient + ' :' + text[start:end] + ' \r\n').encode()) <= 514:
        sock.send((str('PRIVMSG ' + recipient) + ' :' + text[start:end] + ' \r\n').encode())
    else:
        msg = ('PRIVMSG ' + recipient + ' :' + text[start:end])
        while sys.getsizeof(msg.encode()) > 511:
            end -= 1
            msg = ('PRIVMSG ' + recipient + ' :' + text[start:end])
        sock.send(str(msg + ' \r\n').encode())
        if sys.getsizeof(str('PRIVMSG ' + recipient + ' :' + text[end:len(text)] + ' \r\n').encode()) > 514:
            privmsg_cut(sock, recipient, text, end, len(text))
        else:
            sock.send((str('PRIVMSG ' + recipient) + ' :' + text[end:len(text)] + ' \r\n').encode())

def get_real_privmsg(data): #get real msg from irc data
    n = 0
    if data.find('PRIVMSG') != -1:
        for i in range(len(data)):
            if data[i] == ':':
                n += 1
            if data[i] == ':' and n == 2:
                return data[i+1:-3]
    else:
        return ''
def send_privmsg(sock, recipient, text):
    privmsg_cut(sock, recipient, text, 0, len(text))

def send_notice(sock, recipient, text):
    sock.send((str('NOTICE ' + recipient + ' :' + text + ' \r\n').encode()))