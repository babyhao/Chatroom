from socket import *
import os
import sys


# 登录聊天室
def do_login(s, user, name, addr):
    # user 中存在的用户或管理员不能重复登录
    if (name in user) or name == '管理员':
        s.sendto('该用户已存在！'.encode(), addr)
        return
    s.sendto(b'OK', addr)
    # 告知其他人有人进入聊天室
    for i in user:
        msg = '\n欢迎%s进入聊天室' % name
        s.sendto(msg.encode(), user[i])
    # 更新 user
    user[name] = addr


# 转发聊天消息
def do_chat(s, user, name, msg):
    msg = '\n%s说：%s' % (name, msg)
    for i in user:
        if i != name:
            s.sendto(msg.encode(), user[i])


# 登出聊天室
def do_exit(s, user, name, addr):
    msg = '\n' + name + '退出了聊天室'
    for i in user:
        if i == name:
            s.sendto(b'EXIT', addr)
        else:
            s.sendto(msg.encode(), user[i])
    del user[name]


# 管理员喊话
def do_child(s, addr):
    while True:
        msg = 'C %s %s' % ('管理员', input('admin>>'))
        s.sendto(msg.encode(), addr)


# 分发处理不同的请求类型
def do_parent(s, addr):
    user = {'管理员': addr}

    while True:
        msg, addr = s.recvfrom(1024)
        msglist = msg.decode().split(' ')
        if msglist[0] == 'L':
            do_login(s, user, msglist[1], addr)
        elif msglist[0] == 'C':
            do_chat(s, user, msglist[1], msglist[2])
        elif msglist[0] == 'Q':
            do_exit(s, user, msglist[1], addr)
        else:
            print(msg.decode() + '\nadmin>>', end='')


def main():
    ADDR = ('0.0.0.0', 8888)

    s = socket(AF_INET, SOCK_DGRAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    print('聊天室已开启')

    pid = os.fork()
    if pid < 0:
        sys.exit('程序出错')
    elif pid == 0:
        # 创建二级子进程避免出现僵尸进程
        p = os.fork()
        if p < 0:
            sys.exit('程序出错')
        elif p == 0:
            do_child(s, ADDR)
        else:
            sys.exit()
    else:
        # 给子进程收尸
        os.wait()
        do_parent(s, ADDR)


if __name__ == '__main__':
    main()
