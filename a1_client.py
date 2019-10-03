# Name: a1_client.py
# Made for COIS-4310H Assignment 1
# Author: Calen Irwin [0630330] & Ryland Whillens [0618437]
# Purpose: Client portion of Client/Server chat application
# References: https://www.pubnub.com/blog/socket-programming-in-python-client-server-p2p/
#             https://www.geeksforgeeks.org/socket-programming-multi-threading-python/
#             https://www.binarytides.com/code-chat-application-server-client-sockets-python/
from socket import *
from struct import *
VERSION = "1"

# Packet Definition
# ! = byte-ordering
# H = unsigned short
# c = character
# p = varaible length string where the maximum length is specified by the number
#     proceeding it minus 1 (e.g. 21p is a string of maximum 20 characters)
packetStruct = Struct("!Hc21p21p11p256p")
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
        print("Usernamme cannot exceed 20 characters")
        continue
    elif userInput == "all":
        print("Username cannot be \"all\"")
        continue
    pkt = packetStruct.pack(VERSION, packetNum, user, "", "login", "")
    clientSocket.send(pkt)
    packetNum += 1
    srvPkt = packetStruct.unpack(clientSocket.recv(311))
    if srvPkt[4] == "dupName":
        print("Username already in use")
        continue
    break
# todo: get username/confirm
while True:
    # standard input socket and client socket
    socketList = [sys.stdin, clientSocket]
    # use select to get sockets ready to be read
    readSockets, writeSockets, errorSockets = select.select(socketList, [], [])
    # loop through readable sockets
    for s in readSockets:
        # if the socket is the client socket, then the client is being sent
        # data from the server
        # TODO: add proper packet handling
        if s == clientSocket:
            data = s.recv(311)
            if not data:
                print('\nTerminanting chat room connection.')
                sys.exit()
            else:
                sys.stdout.write(data)
        # otherwise, the client has written in the console
        else:
            # read input from client
            userInput = sys.stdin.readline()
            userInput = userInput.split(":", 1)

            if len(usrInput) == 2:
                if (len(usrInput[1]) > 255):
                    print("Message too long")
                else:
                    if usrInput[0] == "all":
                        pkt = packetStruct.pack(VERSION, packetNum, user, "all", "msgAll", usrInput[1])
                        clientSocket.send(pkt)
                        packetNum += 1
                    else:
                        if (len(usrInput[0]) > 20 or not usrInput[0]):
                            print("Invalid username")
                        else:
                            pkt = packetStruct.pack(VERSION, packetNum, user, userInput[0], "msg", usrInput[1])
                            clientSocket.send(pkt)
                            packetNum += 1
            elif usrInput == "who":
                pkt = packetStruct.pack(VERSION, packetNum, user, "", "who", "")
                clientSocket.send(pkt)
                packetNum += 1
            elif  usrInput == "bye":
                pkt = packetStruct.pack(VERSION, packetNum, user, "", "bye", "")
                clientSocket.send(pkt)
                clientSocket.close()
            else:
                print("Unknown Command")
clientSocket.close()
