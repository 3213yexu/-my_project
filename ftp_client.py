from socket import *
import sys
import time

#  具体功能
class FtpClient:
    def __init__(self,sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b'L')  #  发送请求
        #  等待回复
        data = self.sockfd.recv(128).decode()
        #  ok 表示请求成功
        if data == 'OK':
            # while True:
            #     data = self.sockfd.recv(128)
            #     if data == b'##':
            #         break
            #     print(data.decode())
            data = self.sockfd.recv(4096)   #  接收文件列表
            print(data.decode())
        else:
            print(data)


    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit('sb')

    def do_get(self,filename):
        #  发送请求
        self.sockfd.send(("G "+filename).encode())
        #  等待回复
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            fd = open(filename,"wb")
            #  接收内容写入文件
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":
                    break
                fd.write(data.encode())
            fd.close()
        else:
            print(data)

    def do_put(self,filename):
        try:
            f = open(filename,'rb')
        except Exception:
            print('没有该文件')
            return

        #  发送请求
        filename = filename.split()[-1]
        self.sockfd.send(("P " + filename).encode())
        #  等待回复
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            while True:
                a = f.read(1024)
                if not a:
                    time.sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(a)
            f.close()
        print(data)





#  发起请求
def request(sockfd):
    ftp = FtpClient(sockfd)

    while True:
        print('''
            \n------命令提示------'
            list
            get file
            put file
            quit         
        ''')
        cmd = input('输入命令：')
        if cmd == 'list':
            ftp.do_list()
        elif cmd == 'quit':
            ftp.do_quit()
        elif cmd[:3] == 'get':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_get(filename)
        elif cmd[:3] == 'put':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_put(filename)



#  网络链接
def main():
    #  服务器地址
    ADDR = ('176.209.104.68',8080)
    sockfd = socket()
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print('链接服务器失败')
    else:
        print('''****************
                  day01   day02
                 ****************
        ''')
        cls =input('请输入文件种类：')
        if cls not in ['day01','day02']:
            print('Sorry input Error!!')
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd) #具体发送请求

if __name__ == '__main__':
    main()