from socket import *
from struct import *
import time
import threading
import random


Red = "\033[31;1m"
Green = "\033[32;1m"
Yellow = "\033[33;1m"
Blue = "\033[34;1m"
End = "\033[0;1m"
#define some global variables for the server
team_1 = ""
team_1_connection = None
team_2 = ""
team_2_connection = None
question = []
answer = ''
answer_team = -1
lock1 = threading.Lock()
lock2 = threading.Lock()
question_bank = [["2+2","4"],["(5*2*7+8)*(5*0*5)+3","3"],["(6^2)/4","9"],["7+6+5-10","8"],["6*5*2/12","5"],["(17+18)/5","7"],["5!/20","6"],["2+6+1","9"],["(7+5*6+3)/5","8"],
 ["(2^5+18)/10","5"],["1+1","2"],["7*7/7","7"],["3^4/9","9"],["4^2-7","9"],["10*9*8*7*0*4","0"],["500/25/5","4"],["69*2/6-15","8"],["6*5/3-1","9"],["1024/256","4"],["7+10-8-6","3"]]
BroadcastIP = '255.255.255.255'
BroadcastPort = 13117
buff_size = 1024

# Press the green button in the gutter to run the script.


def clientThread(connection):

    #getting the client's name. on a timer of 10 seconds
    name, name_received = getTeamName(connection)

    if name_received:
        setTeamName(name, connection)
    return



def getClientAnswer(connection, client_num):
    global answer_team, answer
    message = ("you have 10 seconds to answer the following question:\n" + question[0])
    try:
        connection.sendall(message.encode('utf-8'))
    except:
        print(f"{Yellow}connection from client lost{End}")
        try:
            connection.close()
            return
        except:
            return
    end = time.time() + 10
    while time.time() < end:
        try:
            data = connection.recv(1)
            if data:
                processed_data = data.decode('utf-8')
                print(processed_data)
                lock1.acquire()
                if len(answer_team) == 0:
                    answer = processed_data
                    answer_team = client_num
                    lock1.release()
        except:
            try:
                connection.close()
            except:
                pass
    try:
        connection.sendall(conclude().encode('utf-8'))
        try:
            connection.close()
        except:
            return
    except:
        try:
            connection.close()
        except:
            return




def setTeamName(name, connection):
    lock1.acquire()
    global team_1, team_2, team_1_connection,team_2_connection
    if len(team_1) == 0:
        team_1 = name
        team_1_connection = connection
        lock1.release()
        return
    else:
        team_2 = name
        team_2_connection = connection
        lock1.release()
        return




def getTeamName(connection):
    name = ""
    name_received = False
    end = time.time() + 10
    while time.time() < end and not name_received:
        try:
            data = connection.recv(1)
            if data.decode('utf-8') == '\n':
                name_received = True
            else:
                name = name + data.decode('utf-8')
        except:
            name_received = False
    return name, name_received

def UDPInitConnection():
    cs = socket(AF_INET, SOCK_DGRAM)
    cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    return cs


def TCPInitConnection(port):
    host = gethostname()
    sock = socket(AF_INET, SOCK_STREAM)
    server_address = ("127.0.0.1", port)
    try:
        sock.bind(server_address)
    except:
        print(f"{Red}error binding{End}")
    return sock

def Main():
    global team_1,team_2,team_1_connection,team_2_connection,question,answer,answer_team
    host = gethostname()
    port = random.randint(2000,40000)
    print(port)
    print(f"{Blue}server started, listening on IP address\n{End}",gethostbyname(host))

    sock = TCPInitConnection(port)

    cs = UDPInitConnection()
    msg = pack('!IBH', 0xfeedbeef, 0x2, port)


    try:
        sock.listen()
        counter = 0
        client_threads = []
        while True:
            if(counter < 2):
                try:
                    cs.sendto(msg, (BroadcastIP, BroadcastPort))
                except:
                    print(f"{Red}broadcast failed{End}")
                time.sleep(1)
                sock.settimeout(0)
                try:
                    print("attempt to connect client")
                    connection, addr = sock.accept()
                    print("client has connected")
                    connection.settimeout(0)
                    t = threading.Thread(target= clientThread, args=(connection,))
                    client_threads.append(t)
                    counter = counter + 1
                except:
                    pass
            elif (counter == 2):
                n = random.randint(0,len(question_bank))
                question = question_bank[n]
                print(question)
                for ct in client_threads:
                    ct.start()
                for ct in client_threads:
                    ct.join()
                t1 = threading.Thread(target=getClientAnswer, args=(team_1_connection, 1))
                t2 = threading.Thread(target=getClientAnswer, args=(team_2_connection, 2))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
                print(conclude())
                team_1 = ""
                team_1_connection = None
                team_2 = ""
                team_2_connection = None
                question = []
                answer = ''
                answer_team = -1
                counter = 0
                client_threads = []
    except:
        pass


def conclude():
    to_return = ""
    global answer,question,answer_team
    to_return += ("the correct answer was - " + question[1] + "\n")
    if answer == '':
        to_return =  "It's a Draw!"
    else:
        if answer == question[1]:
            if answer_team == 1:
                to_return += ("team " + team_1 + " is victorious!")
            else:
                to_return += ("team " + team_2 + " is victorious!")
        else:
            if answer_team == 1:
                to_return += ("team " + team_2 + " is victorious!")
            else:
                to_return += ("team " + team_1 + " is victorious!")
    return to_return


if __name__ == '__main__':
    Main()

