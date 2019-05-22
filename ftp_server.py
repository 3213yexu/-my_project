'''
    ftp文件服务器思路分析
    1.技术点分析

      *并发模型
      *数据传输  tcp传输

    2.结构设计

      *客户端发起请求，打印请求提示界面
      *文件传输功能封装为类

    3.功能分析

      *网络搭建
      *查看文件库信息
      *下载文件
      *上传文件
      *客户端推出

    4.协议
      L  表示请求文件列表
'''

from socket import *
from threading import Thread
import os,sys
import signal
from time import sleep

#  全局变量
ADDR = ('0.0.0.0',8080)
FTP = '/home/tarena/python/'    #  文件库路径

#  讲客户端请求功能封装为类
class FtpServer:
    def __init__(self,connfd,FTP_PATH):
        self.connfd = connfd
        self.path = FTP_PATH  # 目录地址

    def do_list(self):
        #  获取文件列表
        files = os.listdir(self.path)
        if not files:
            self.connfd.send('该文件类别为空'.encode())
            return
        else:
            self.connfd.send(b'OK')
            sleep(0.1) #防粘包
        fs = ''
        for file in files:  #  遍历列表中的文件循环发送
            #  判断是否为隐藏文件或是否为文件
            if file[0] != '.' and os.path.isfile(self.path+file):
                fs += file + '\n'  #  设边界防粘包
        self.connfd.send(fs.encode())
        # self.connfd.send(b'##') #  表示发完了

    def do_get(self,filename):
        try:
            fd = open(self.path+filename,'rb')
        except Exception:
            self.connfd.send('文件不存在'.encode())
        else:
            self.connfd.send(b'OK')
            sleep(0.1)
        #  发送文件内容
        while True:
            data = fd.read(1024)
            if not data:    #  文件结束
                sleep(0.1)
                self.connfd.send(b'##')
                break
            self.connfd.send(data)

    def do_put(self,filename):
        #  判断文件是否存在
        if os.path.exists(self.path + filename):
            self.connfd.send('该文件已存在'.encode())
            return
        self.connfd.send(b'OK')
        fd = open(self.path + filename,'wb')
        #  接收文件
        while True:
            data = self.connfd.recv(1024)
            if data == b'##':

                break
            fd.write(data)

        fd.close()


#  客户端请求函数
def handle(connfd):
    cls = connfd.recv(1024).decode()
    FTP_PATH = FTP + cls + '/'

    ftp = FtpServer(connfd,FTP_PATH)  #创建文件请求对象，传入链接套接字及目录地址
    while True:
        #  接收客户端请求
        data = connfd.recv(1024).decode()

        # print(FTP_PATH,':',data)
        #  如果客户端断开data返回为空
        if not data or data[0] == 'Q':
            return
        elif data[0] == 'L':
            ftp.do_list()
        elif data[0] == 'G':
            filename = data.split(' ')[-1]
            ftp.do_get(filename)
        elif data[0] == 'P':
            filename = data.split(' ')[-1]
            ftp.do_put(filename)

#  网络搭建
def main():
    #  创建套接字
    sockfd = socket(AF_INET,SOCK_STREAM)
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    sockfd.listen(5)
    print('Listen the port 9527.....')

    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    while True:
        try:
            connfd,addr = sockfd.accept()
        except KeyboardInterrupt:
            print('退出服务器程序')
            continue
        except Exception as e:
            print(e)
            continue
        print('链接的客户端：',addr)

        #  创建线程处理请求
        client = Thread(target= handle,args=(connfd,))
        client.setDaemon(True)
        client.start()




if __name__ == '__main__':
    main()









