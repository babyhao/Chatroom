from socket import *
import sys, os


# 发送消息
def send_msg(s, name, addr):
    while True:
        msg = input('>>')

        # 如果发送的是 # 表示退出聊天室
        if msg == '#':
            msg = 'Q ' + name
            s.sendto(msg.encode(), addr)
            sys.exit()

        msg = 'C %s %s' % (name, msg)
        s.sendto(msg.encode(), addr)


# 接收消息
def recv_msg(s):
    while True:
        msg, addr = s.recvfrom(1024)

        if msg.decode() == 'EXIT':
            print('您已退出聊天室')
            return

        print(msg.decode() + '\n>>', end='')


def main():
    if len(sys.argv) < 3:
        sys.exit('argv is error')

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST, PORT)

    s = socket(AF_INET, SOCK_DGRAM)

    while True:
        # 首先要进入聊天室
        while True:
            name = input('请输入您的用户名：')
            msg = 'L ' + name
            s.sendto(msg.encode(), ADDR)
            msg, addr = s.recvfrom(1024)
            if msg.decode() == 'OK':
                print('欢迎来到聊天室^_^')
                break
            else:
                print(msg.decode())

        pid = os.fork()
        if pid < 0:
            sys.exit('程序出错')
        elif pid == 0:
            # 创建二级子进程避免出现僵尸进程
            p = os.fork()
            if p < 0:
                sys.exit('程序出错')
            elif p == 0:
                send_msg(s, name, ADDR)
            else:
                sys.exit()
        else:
            # 给子进程收尸
            os.wait()
            recv_msg(s)


if __name__ == '__main__':
    main()