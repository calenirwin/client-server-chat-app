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
class PacketFormat(Enum):
    H_PACKETNUM = 0
    H_VERSION = 1
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
        readSockets, writeSockets, errorSockets = select(connectionList, [], [])

        for sock in readSockets:
            # handle a new client connection
            if sock == serverSocket:
                sd, clientAddr = sock.accept()
                connectionList.append(sd)
                clientPacket = packetStruct.unpack(sd.recv(PACKET_SIZE))
                if len(connectedClientList) > 5:
                    capacityErr = "Error: Server capacity is full. Please try again later."
                    send_packet(sd, packetStruct, VERSION, packetNum, "", clientPacket[PacketFormat.H_SOURCE], "err", capacityErr)
                # handle duplicate name
                elif clientPacket[2] in connectedClientList:
                    dupErr = "Error: That name already exists. Please try connecting using a different name"
                    send_packet(sd, packetStruct, VERSION, packetNum, "", clientPacket[PacketFormat.H_SOURCE], "err", dupErr)
                    # remove client from connection list
                    del connectionList[-1]
                else:
                    # add clients name to list of connected clients
                    connectedClientList.append(clientPacket[PacketFormat.H_SOURCE])
                    # send connection confirmation message
                    send_packet(sd, packetStruct, VERSION, packetNum, "", clientPacket[PacketFormat.H_SOURCE], "suc", "")

            # handle incoming message from existing clients
            else:
                clientPacket = packetStruct.unpack(sock.recv(PACKET_SIZE))
                verb = clientPacket[PacketFormat.H_VERB]

                if verb == 'msg':
                    if clientPacket[PacketFormat.H_DEST] not in connectedClientList:
                        destNotFoundErr = "Error: The recipient of your message is not connected."
                        send_packet(sock, packetStruct, VERSION, packetNum, "", clientPacket[PacketFormat.H_SOURCE], "err", destNotFoundErr)
                        # send the error message back to server
                    else:
                        socketIndex = connectedClientList.index(clientPacket[PacketFormat.H_DEST]) + 1
                        send_packet(connectionList[socketIndex], packetStruct, VERSION, packetNum, clientPacket[PacketFormat.H_SOURCE], clientPacket[PacketFormat.H_DEST], "err", "")

                elif verb == 'all':
                    index = 1
                    for client in connectedClientList:
                        if client != clientPacket[PacketFormat.H_SOURCE]:
                            send_packet(connectionList[index], packetStruct, VERSION, packetNum, clientPacket[PacketFormat.H_SOURCE], client, "all", clientPacket[PacketFormat.BODY])
                        index += 1
                        # send the packet back to sender

                elif verb == 'who':
                    clients = "Connected Users: " + ", ".join(connectedClientList)
                    send_packet(sock, packetStruct, VERSION, packetNum, "", clientPacket[PacketFormat.H_SOURCE], "who", clients)

                elif verb == 'bye':
                    clientIndex = connectedClientList.index(PacketFormat.H_SOURCE)
                    socketIndex = clientIndex + 1

                    connectedClientList.pop(clientIndex)
                    connectionList.pop(socketIndex)

    serverSocket.close()

if __name__ == "__main__":
    main()