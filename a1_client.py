# Name: a1_client.py
# Made for COIS-4310H Assignment 1
# Author: Calen Irwin [0630330] & Ryland Whillens [0618437]
# Purpose: Client portion of Client/Server chat application
# References: https://www.pubnub.com/blog/socket-programming-in-python-client-server-p2p/
#             https://www.geeksforgeeks.org/socket-programming-multi-threading-python/
#             https://www.binarytides.com/code-chat-application-server-client-sockets-python/
from socket import *
from struct import *
from select import select
from enum import Enum
VERSION = "1"
PACKET_SIZE = 305

# Packet Definition
# ! = byte-ordering
# H = unsigned short
# c = character
# p = varaible length string where the maximum length is specified by the number
#     proceeding it minus 1 (e.g. 21p is a string of maximum 20 characters)
packetStruct = Struct("!Hc21p21p4p256p")
class PacketFormat(Enum):
    H_PACKETNUM = 0
    H_VERSION = 1
    H_SOURCE = 2
    H_DEST = 3
    H_VERB = 4
    BODY = 5
packetNum = 0

lokiAddr = "192.197.151.116"
serverPort = 50330
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((lokiAddr, serverPort))
while True:
    user = input("Enter username: ")
    if len(user) == 0:
        print("Username cannot be empty")
        continue
    elif len(user) > 20:
        print("Username cannot exceed 20 characters")
        continue
    elif user == "all":
        print("Username cannot be \"all\"")
        continue
    send_packet(VERSION, packetNum, user, "", "login", "")
    serverPacket = packetStruct.unpack(clientSocket.recv(PACKET_SIZE))
    if serverPacket[PacketFormat.H_VERB] == "err":
        print(serverPacket[PacketFormat.BODY])
    elif serverPacket[PacketFormat.H_VERB] == "suc":
        break
# todo: get username/confirm
while True:
    # standard input socket and client socket
    socketList = [sys.stdin, clientSocket]
    # use select to get sockets ready to be read
    readSockets, writeSockets, errorSockets = select(socketList, [], [])
    # loop through readable sockets
    for s in readSockets:
        # if the socket is the client socket, then the client is being sent
        # data from the server
        # TODO: add proper packet handling
        if s == clientSocket:
            serverPacket = packetStruct.unpack(clientSocket.recv(PACKET_SIZE))
            if not serverPacket:
                print('\nTerminanting chat room connection.')
                sys.exit()
            else:
                verb = serverPacket[PacketFormat.H_VERB]
                if verb == "msg":
                    print(serverPacket[PacketFormat.H_SOURCE] + ": " + serverPacket[PacketFormat.BODY])
                elif verb == "all":
                    print(serverPacket[PacketFormat.H_SOURCE] + " -> All: " + serverPacket[PacketFormat.BODY])
                elif verb == "noUser":
                    print("User does not exist")
        # otherwise, the client has written in the console
        else:
            # read input from client
            userInput = sys.stdin.readline()
            userInput = userInput.split(":", 1)

            if len(userInput) == 2:
                if (len(userInput[1]) > 255):
                    print("Message too long")
                else:
                    if userInput[0] == "all":
                        send_packet(VERSION, packetNum, user, "", "all", userInput[1])
                    else:
                        if (len(userInput[0]) > 20 or not userInput[0]):
                            print("Invalid username")
                        else:
                            send_packet(VERSION, packetNum, user, userInput[0], "msg", userInput[1])
            elif userInput == "who":
                send_packet(VERSION, packetNum, user, "", "who", "")
            elif  userInput == "bye":
                send_packet(VERSION, packetNum, user, "", "bye", "")
                clientSocket.close()
                break
            else:
                print("Unknown Command")
clientSocket.close()


def send_packet(version, packetNum, src, dest, verb, body)
    packet = packetStruct.pack(version, packetNum, src, dest, verb, body)
    clientSocket.send(packet)
    packetNum += 1
