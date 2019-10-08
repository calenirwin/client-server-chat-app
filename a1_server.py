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
from enum import Enum
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

class PktFormat(Enum):
    H_PACKETNUM = 0
    H_VERSION = 1
    H_SOURCE = 2
    H_DEST = 3
    H_VERB = 4
    BODY = 5

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
                capacityErr = "Error: Server capacity is full. Please try again later."
                pkt = packetStruct.pack(VERSION, packetNum, "", cliPkt[PktFormat.H_SOURCE], "err", capacityErr)
                sd.send(pkt)
            # handle duplicate name
            elif cliPkt[2] in connectedClientList:
                dupErr = "Error: That name already exists. Please try connecting using a different name"
                pkt = packetStruct.pack(VERSION, packetNum, "", cliPkt[PktFormat.H_SOURCE], "err", dupErr)
                sd.send(pkt);
                # remove client from connection list
                del connectionList[-1]
            else
                # add clients name to list of connected clients
                connectedClientList.append(cliPkt[PktFormat.H_SOURCE])
                # send connection confirmation message
                pkt = packetStruct.pack(VERSION, packetNum, "", cliPkt[PktFormat.H_SOURCE], "suc", "")

        # handle incoming message from existing clients
        else:
            cliPkt = packetStruct.unpack(clientSocket.recv(packetBuf))
            verb = cliPkt[PktFormat.H_VERB]

            if verb == 'msg':
                if cliPkt[PktFormat.H_DEST] not in connectedClientList:
                    destNotFoundErr = "Error: The recipient of your message is not connected."
                    pkt = packetStruct.pack(VERSION, packetNum, "", cliPkt[PktFormat.H_SOURCE], "err", destNotFoundErr)
                    # send the error message back to server
                    socketIndex = connectedClientList.index(cliPkt[PktFormat.H_SOURCE]) + 1
                    connectionList[socketIndex].send(pkt)
                else:
                    pkt = packetStruct.pack(VERSION, packetNum, cliPkt[PktFormat.H_SOURCE], cliPkt[PktFormat.H_DEST], "err", "")
                    socketIndex = connectedClientList.index(cliPkt[PktFormat.H_DEST]) + 1
                    connectionList[socketIndex].send(pkt)

            elif verb == 'all':
                for client in connectedClientList:
                    pkt = packetStruct.pack(VERSION, packetNum, cliPkt[PktFormat.H_SOURCE], client, "all", cliPkt[PktFormat.BODY])
                    # send the packet back to sender
                    socketIndex = connectedClientList.index(client) + 1
                    connectionList[socketIndex].send(pkt)

            elif verb == 'who':
                clients = "Connected Users: "
                for client in connectedClientList:
                    clients += client + " | "
                pkt = packetStruct.pack(VERSION, packetNum, "", cliPkt[pktformat.H_SOURCE], "who", clients)
                socketIndex = connectedClientList.index(cliPkt[pktformat.H_SOURCE]) + 1
                connectionList[socketIndex].send(pkt)

            elif verb == 'bye':
                clientIndex = connectedClientList.index(PktFormat.H_SOURCE)
                socketIndex = clientIndex + 1

                connectedClientList.pop(clientIndex)
                connectionList.pop(socketIndex)

serverSocket.close()
