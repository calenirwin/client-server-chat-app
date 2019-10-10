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
H_VERSION = 0
H_PACKETNUM = 1
H_SOURCE = 2
H_DEST = 3
H_VERB = 4
BODY = 5

def send_packet(socket, struct, version, packetNum, src, dest, verb, body):
    packet = struct.pack(version, packetNum, src, dest, verb, body)
    socket.send(packet)
    packetNum += 1

def main():
    # Packet Definition
    # ! = byte-ordering
    # H = unsigned short
    # c = character
    # p = varaible length string where the maximum length is specified by the number
    #     proceeding it minus 1 (e.g. 21p is a string of maximum 20 characters)
    packetStruct = Struct("!cH21p21p3s256p")

    

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
        readSockets, writeSockets, errorSockets = select(connectionList, [], [])

        for sock in readSockets:
            # handle a new client connection
            if sock == serverSocket:
                sd, clientAddr = sock.accept()
                clientPacket = packetStruct.unpack(sd.recv(packetStruct.size))
                if len(connectedClientList) >= 5:
                    capacityErr = "Error: Server capacity is full. Please try again later."
                    send_packet(sd, packetStruct, VERSION, packetNum, "", clientPacket[H_SOURCE], "err", capacityErr)
                    sd.close()
                # handle duplicate name
                elif clientPacket[2] in connectedClientList:
                    dupNameErr = "Error: That name already exists. Please try connecting using a different name"
                    send_packet(sd, packetStruct, VERSION, packetNum, "", clientPacket[H_SOURCE], "err", dupNameErr)
                    # remove client from connection list
                    sd.close()
                else:
                    # add clients name to list of connected clients
                    connectionList.append(sd)
                    connectedClientList.append(clientPacket[H_SOURCE])
                    # send connection confirmation message
                    clients = "Connected Users: " + ", ".join(connectedClientList)
                    send_packet(sd, packetStruct, VERSION, packetNum, "", clientPacket[H_SOURCE], "srv", "Connected!\n" + clients)
                    index = 1
                    for client in connectedClientList:
                        if client != clientPacket[H_SOURCE]:
                            send_packet(connectionList[index], packetStruct, VERSION, packetNum, clientPacket[H_SOURCE], client, "srv", "New User \"" + clientPacket[H_SOURCE] + "\" has connected")
                        index += 1

            # handle incoming message from existing clients
            else:
                rawPacket = sock.recv(packetStruct.size)
                if(len(rawPacket) == 0):
                    socketIndex = connectionList.index(sock)
                    clientName = connectedClientList.pop(socketIndex-1)
                    connectionList.pop(socketIndex)
                    sock.close()
                    index = 1
                    for client in connectedClientList:
                        send_packet(connectionList[index], packetStruct, VERSION, packetNum, "", client, "srv", "\"" + clientName + "\" has disconnected")
                        index += 1
                else:
                    clientPacket = packetStruct.unpack(rawPacket)
                    verb = clientPacket[H_VERB]

                    if verb == 'msg':
                        if clientPacket[H_DEST] not in connectedClientList:
                            destNotFoundErr = "Error: The recipient of your message is not connected."
                            send_packet(sock, packetStruct, VERSION, packetNum, "", clientPacket[H_SOURCE], "err", destNotFoundErr)
                            # send the error message back to server
                        else:
                            socketIndex = connectedClientList.index(clientPacket[H_DEST]) + 1
                            send_packet(connectionList[socketIndex], packetStruct, VERSION, packetNum, clientPacket[H_SOURCE], clientPacket[H_DEST], "msg", clientPacket[BODY])

                    elif verb == 'all':
                        index = 1
                        for client in connectedClientList:
                            if client != clientPacket[H_SOURCE]:
                                send_packet(connectionList[index], packetStruct, VERSION, packetNum, clientPacket[H_SOURCE], client, "all", clientPacket[BODY])
                            index += 1
                            # send the packet back to sender

                    elif verb == 'who':
                        clients = "Connected Users: " + ", ".join(connectedClientList)
                        send_packet(sock, packetStruct, VERSION, packetNum, "", clientPacket[H_SOURCE], "who", clients)

                    elif verb == 'bye':
                        clientIndex = connectedClientList.index(clientPacket[H_SOURCE])
                        connectedClientList.pop(clientIndex)
                        connectionList.pop(clientIndex+1).close()
                        index = 1
                        for client in connectedClientList:
                            send_packet(connectionList[index], packetStruct, VERSION, packetNum, clientPacket[H_SOURCE], client, "srv", "\"" + clientPacket[H_SOURCE] + "\" has disconnected")
                            index += 1

    serverSocket.close()

if __name__ == "__main__":
    main()