import socket
import struct
from threading import Thread
import time
import getch

def Main():
    while True:
        data = getch.getch()
        print("\n",data,"\n")


if __name__ == '__main__':
    Main()
