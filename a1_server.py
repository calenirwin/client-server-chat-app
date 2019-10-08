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
PACKET_SIZE = 311


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
connectedClientList = []

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
            sd, clientAddr = serverSocket.accept()
            connectionList.append(sd)
            cliPkt = packetStruct.unpack(clientSocket.recv(PACKET_SIZE))
            if len(connectedClientList) > 5
                pkt = packetStruct.pack(VERSION, packetNum, "", cliPkt[2], "connError", "")
                sd.send(pkt)
            # handle duplicate name
            elif cliPkt[2] in connectedClientList:
                pkt = packetStruct.pack(VERSION, packetNum, "", cliPkt[2], "nameError", "")
                sd.send(pkt);
                # remove client from connection list
                del connectionList[-1]
            else
                # add clients name to list of connected clients
                connectedClientList.append(cliPkt[2])
                # send welcome message
                pkt = packetStruct.pack(VERSION, packetNum, "server", cliPkt[2], "conn", "")

        # handle incoming message from existing client
        else:
            cliPkt = packetStruct.unpack(clientSocket.recv(packetBuf))
            # specified receiver not connected to server
            if cliPkt[3] not in connectedClientList:
                pkt = packetStruct.pack(VERSION, packetNum, "server", cliPkt[2], "noUser", "")
                # send the packet back to sender
                socketIndex = connectedClientList.index(cliPkt[2])
                connectionList[socketIndex + 1].send(pkt)
            elif cliPkt[]



serverSocket.close()
