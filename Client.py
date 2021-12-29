import socket
import struct
from threading import Thread
import time
import getch

Red = "\033[31;1m"
Green = "\033[32;1m"
Yellow = "\033[33;1m"
Blue = "\033[34;1m"
End = "\033[0;1m"
UDPPort = 13117
buf_size = 1024


# thread that sends packets to the server
def Start_Game(socket):
    try:
                #socket.settimeout(max(0, time_to_end - time_now))  # recive the max for timeout
                send = getch.getch()  # receive the charactars as hiding chars , which dosent shown
                print(send)
                socket.sendall(send.encode('utf-8'))
                print("was sent")
    except:
        pass


# thread that listen to the server in the game so he can print the result of the game
def Print_the_Score_Res(sock):
    try:
        time_now = time.time()
        time_to_end = time.time() + 10
        while time_now < time_to_end:
            output = sock.recv(buf_size)
            if output:
                print(output.decode('utf-8'))
            time_now = time.time()
    except:
        pass


def Main():
    name_of_team = "Beholder\n"
    print(f"{Blue}Client started,listening for offer requests...\n{End}")
    # initial the udp connection
    cl = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cl.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    cl.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        cl.bind(("", UDPPort))
    except:
        print(f"{Red}error binding{End}")

    while True:
        # recivind the
        data1, addr = cl.recvfrom(buf_size)
        host, UDP_Port = addr
        try:
            data1, data2, TCP_Port = struct.unpack('!IBH', data1)
            print("tcp_port = /n", TCP_Port)
            print("host = /n", host)
            print("UDP_PORT = /n", UDP_Port)
            print("data1 = /n", hex(data1))
            print("data2 = /n", hex(data2))
            
            if data2 == 0x2 and data1 == 0xfeedbeef:  # checking recieved message from broadcast
                print(f"{Blue}received offer from{End}", host, f"{Blue},attempting to connect...\n{End}")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = ("127.0.0.1", TCP_Port)
                try:
                    sock.connect(server_address)
                except:
                    print(f"{Red}connection failed{End}")
                try:
                    print("sending the name")
                    # sending the team name
                    sock.sendall(name_of_team.encode('utf-8'))
                    is_data_found = False
                    time_to_end = time.time() + 10
                    time_now = time.time()
                    # give the server 10 sec to give us the permition to start the game
                    while not is_data_found and time_now < time_to_end:
                        data = sock.recv(2048)
                        # starting the game
                        if data is not None:
                            print(data.decode('utf-8'))
                            # open two threads on for sending, the other for lisining for the result of the end of the game
                            # starting the first thread to send packets for 10 sec
                            send = Thread(target=Start_Game, args=(sock,))
                            send.start()
                            send.join()
                            # starting  the second thread which prints the server responses for 10 sec
                            listen = Thread(target=Print_the_Score_Res, args=(sock,))
                            listen.start()
                            listen.join()
                            is_data_found = True
                        time_now = time.time()
                except:
                    print(f"{Red}server closed{End}")
                finally:
                    sock.close()
        except:
            pass


if __name__ == '__main__':
    Main()
