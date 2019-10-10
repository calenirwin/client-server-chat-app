# ==========================================================================================
# Name: client.py
# Made for COIS-4310H Assignment 1
# Author: Calen Irwin [0630330] & Ryland Whillens [0618437]
# Purpose: Client portion of Client/Server chat application
# References: https://www.binarytides.com/code-chat-application-server-client-sockets-python/
# ==========================================================================================

from socket import *
from struct import *
from select import select
from enum import Enum
from sys import stdin, exit

VERSION = "1"                       # version of application/rfc
SERVER_ADDRESS = "192.197.151.116"  # address of server
SERVER_PORT = 50330                 # port of server
#Constants for accessing packet elements as indices
H_VERSION = 0   
H_PACKETNUM = 1 
H_SOURCE = 2    
H_DEST = 3      
H_VERB = 4      
BODY = 5        

 # global counter for number of packets sent


def send_packet(socket, struct, version, packetNum, src, dest, verb, body):
    packet = struct.pack(version, packetNum, src, dest, verb, body)
    socket.send(packet)
    return packetNum + 1

def main():
    # Packet Definition
    # ! = byte-ordering
    # H = unsigned short
    # c = character
    # p = varaible length string where the maximum length is specified by the number
    #     proceeding it minus 1 (e.g. 21p is a string of maximum 20 characters)
    packetStruct = Struct("!cH21p21p3s256p")
    packetNum = 0

    

    while True:
        user = raw_input("Enter username: ")
        if len(user) == 0:
            print("Username cannot be empty")
            continue
        elif len(user) > 20:
            print("Username cannot exceed 20 characters")
            continue
        elif user == "all":
            print("Username cannot be \"all\"")
            continue
        clientSocket = socket(AF_INET, SOCK_STREAM)
        try:
            clientSocket.connect((SERVER_ADDRESS, SERVER_PORT))
        except:
            print("Unable to connect to server")
            exit()
        packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, "", "con", "")
        serverPacket = packetStruct.unpack(clientSocket.recv(packetStruct.size))
        if serverPacket[H_VERB] == "err":
            print(serverPacket[BODY])
            clientSocket.close()
        elif serverPacket[H_VERB] == "srv":
            print(serverPacket[BODY])
            break

    while True:
        # standard input socket and client socket
        socketList = [stdin, clientSocket]
        # use select to get sockets ready to be read
        readSockets, writeSockets, errorSockets = select(socketList, [], [])
        # loop through readable sockets
        for s in readSockets:
            # if the socket is the client socket, then the client is being sent
            # data from the server
            if s == clientSocket:
                rawPacket = clientSocket.recv(packetStruct.size)
                if(len(rawPacket) == 0):
                    print("Disconnected Unexpectedly")
                    clientSocket.close()
                    exit()
                else:
                    serverPacket = packetStruct.unpack(rawPacket)
                    if not serverPacket:
                        print('\nTerminanting chat room connection.')
                        exit()
                    else:
                        verb = serverPacket[H_VERB]
                        if verb == "msg":
                            print(serverPacket[H_SOURCE] + ": " + serverPacket[BODY])
                        elif verb == "all":
                            print(serverPacket[H_SOURCE] + " -> All: " + serverPacket[BODY])
                        elif verb == "who" or verb == "srv" or verb == "err":
                            print(serverPacket[BODY])
            # otherwise, the client has written in the console
            else:
                # read input from client
                userInput = stdin.readline().strip().split(":", 1)
                if len(userInput) == 2:
                    if (len(userInput[1]) > 255):
                        print("Message too long")
                    else:
                        if userInput[0] == "all":
                            packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, "", "all", userInput[1])
                        else:
                            if (len(userInput[0]) > 20 or not userInput[0]):
                                print("Invalid username")
                            else:
                                packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, userInput[0], "msg", userInput[1])
                elif userInput[0] == "who":
                    packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, "", "who", "")
                elif  userInput[0] == "bye":
                    packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, "", "bye", "")
                    clientSocket.close()
                    exit()
                else:
                    print("Unknown Command")

if __name__ == "__main__":
    main()
