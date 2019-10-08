# =========================================================================================
# Name: a1_server.py
# Made for COIS-4310H Assignment 1
# Author: Calen Irwin [0630330] & Ryland Whillens [0618437]
# Purpose: Server portion of Client/Server chat application
# References: https://www.binarytides.com/code-chat-application-server-client-sockets-python/
# ==========================================================================================
  
from socket import *
from struct import *
from select import select
VERSION = "1"


if __name__ == "__main__":
# Packet Definition
# ! = byte-ordering
# H = unsigned short
# c = character
# p = varaible length string where the maximum length is specified by the number
#     proceeding it minus 1 (e.g. 21p is a string of maximum 20 characters)
packetStruct = Struct("!Hc21p21p11p256p")
packetNum = 0

connectionList = []
connectedClientNames = []

lokiAddr = "192.197.151.116"
serverPort = 50330
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((lokiAddr, serverPort))
serverSocket.listen(5)

connectionList.append(serverSocket)

while True:
    readSockets, writeSockets, errorSockets = select.select(connectionList, [], [])

    for s in readSockets:
        # handle a new client connection
        if s == serverSocket:

        # handle incoming message from existing client
        else:

serverSocket.close()
