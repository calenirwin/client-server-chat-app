# =============================================================================================
# Name: client.py
# Made for COIS-4310H Assignment 2
# Author: Calen Irwin [0630330] & Ryland Whillans [0618437]
# Last Modification Date: 2019-11-07
# Purpose: Client portion of Client/Server chat application
# Instructions for running => "python client.py"
# References:   https://www.binarytides.com/code-chat-application-server-client-sockets-python/
#               https://docs.python.org/3/library/struct.html
# =============================================================================================

from socket import *                # import all from socket library
from struct import *                # import all from struct library
from hashlib import *               # import all from hashlib library
from select import select           # import select from select library
from sys import stdin, exit         # import stdin and exit from sys library
from random import random           # import random from random library

VERSION = "2"                       # version of application/rfc
SERVER_ADDRESS = "192.197.151.116"  # address of server
SERVER_PORT = 50330                 # port of server

# constants for accessing packet elements as indices
H_VERSION = 0
H_PACKETNUM = 1
H_SOURCE = 2
H_DEST = 3
H_VERB = 4
CHECKSUM = 5
BODY = 6

# wrapper function to create and send a packet and then iterate the packet number
def send_packet(socket, struct, version, packetNum, src, dest, verb, checksum, body):
    rand = random()
    # corrupt checksum
    if rand > 0.9:
        checksum = ""
    packet = struct.pack(version, packetNum, src, dest, verb, checksum, body)
    socket.send(packet)
    return packetNum + 1

# function to generate and return md5 hash
def get_sha256(body):
    hash = sha256()                      # sha256 hashing algorithm
    hash.update(body.encode("utf-8"))    # hash the given argument
    return hash.hexdigest()              # 64 character hash string

def main():

    # Struct Description
    # Structs are C structs represented as Python byte objects
    # Our packet struct is defined using the format string passed to the Struct() function
    # The format string is a compact description of the layout of the C struct
    # We use the following functions contained within the Struct module:
    # pack() - Returns a bytes object according to the format string
    # unpack() - Unpack the buffer according to the format string into a tuple
    # -------------------------------------------------------------------------------------
    # Format String Description
    # ! = byte-ordering
    # H = unsigned short
    # c = character
    # p = varaible length string where the maximum length is specified by the number
    #     proceeding it minus 1 (e.g. 21p is a string of maximum 20 characters)
    #--------------------------------------------------------------------------------------
    packetStruct = Struct("!cH21p21p3s64s256p")

    packetNum = 0       # counter for total number of packets sent by client

    messageList = []    # stores ALL sent messages

    # loop to establish connection with server
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
        clientSocket = socket(AF_INET, SOCK_STREAM)             # open new socket
        try:
            clientSocket.connect((SERVER_ADDRESS, SERVER_PORT)) # connect to server on socket
        except:
            print("Unable to connect to server")
            exit()
        # send an initial connection packet to the server
        packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, "", "con", get_sha256(""), "")
        messageList.append(("", "con", ""))
        # receive and unpack return message from server
        serverPacket = packetStruct.unpack(clientSocket.recv(packetStruct.size))
        # if packet rebroadcast requested, attempt to resend packet until successful
        while (serverPacket[H_VERB] == "reb"):

            clientSocket = socket(AF_INET, SOCK_STREAM)             # open new socket
            try:
                clientSocket.connect((SERVER_ADDRESS, SERVER_PORT)) # connect to server on socket
            except:
                print("Unable to connect to server")
                exit()
            rebroadcastMsg = messageList[int(serverPacket[BODY])]
            packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, rebroadcastMsg[2], rebroadcastMsg[1], get_sha256(rebroadcastMsg[0]), rebroadcastMsg[0])
            messageList.append(rebroadcastMsg)
            serverPacket = packetStruct.unpack(clientSocket.recv(packetStruct.size))

        # if an error occured while trying to connect
        if serverPacket[H_VERB] == "err":
            print(serverPacket[BODY])       # print the error
            clientSocket.close()            # close the socket
        # if the server responds with a confirmation message
        elif serverPacket[H_VERB] == "srv":
            print(serverPacket[BODY])       # print the server message
            break                           # break from the while loop

    # main loop to handle incoming packets and command line input using select
    while True:
        socketList = [stdin, clientSocket]  # standard input stream and client socket
        readSockets, writeSockets, errorSockets = select(socketList, [], [])    # use select to get readable sockets

        # loop through readable sockets
        for s in readSockets:
            # if the socket is the client socket, then the client is being sent
            # data from the server
            if s == clientSocket:
                rawPacket = clientSocket.recv(packetStruct.size)
                # handle an unexpected disconnect
                if(len(rawPacket) == 0):
                    print("Disconnected Unexpectedly")
                    clientSocket.close()
                    messageList[:] = []
                    exit()
                else:
                    serverPacket = packetStruct.unpack(rawPacket)
                    # if packet wasn't unpacked properly, disconnect
                    if not serverPacket:
                        print('\nTerminanting chat room connection.')
                        messageList[:] = []
                        exit()
                    else:
                        verb = serverPacket[H_VERB]
                        # handle the packet based on the supplied verb
                        # if the server is requesting a rebroadcast then the packet number of the
                        # packet to be rebroadcasted is contained within the body of the incomming packets
                        # the packet number corresponds to the index of the message to be rebroadcasted in the message list
                        if verb == "reb":
                            rebroadcastMsg = messageList[int(serverPacket[BODY])]
                            packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, rebroadcastMsg[2], rebroadcastMsg[1], get_sha256(rebroadcastMsg[0]), rebroadcastMsg[0])
                            messageList.append(rebroadcastMsg)
                        elif verb == "msg":
                            print(serverPacket[H_SOURCE] + ": " + serverPacket[BODY])
                        elif verb == "all":
                            print(serverPacket[H_SOURCE] + " -> All: " + serverPacket[BODY])
                        elif verb == "who" or verb == "srv" or verb == "err":
                            print(serverPacket[BODY])
            # otherwise, the client has written in the console
            else:
                # read input from client and split it once at the first ":" character into a list
                # userInput is a 2 item list where userInput[0] = text left of ":" and userInput[1] = text right of ":"
                userInput = stdin.readline().strip().split(":", 1)
                # if the list has 2 items, then a message is being sent
                if len(userInput) == 2:
                    if (len(userInput[1]) > 255):
                        print("Message too long")
                    else:
                        if userInput[0] == "all":
                            packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, "", "all", get_sha256(userInput[1]), userInput[1])
                            messageList.append((userInput[1], "all", ""))
                        else:
                            if (len(userInput[0]) > 20 or not userInput[0]):
                                print("Invalid username")
                            else:
                                packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, userInput[0], "msg", get_sha256(userInput[1]), userInput[1])
                                messageList.append((userInput[1], "msg", userInput[0]))
                elif userInput[0] == "who":
                    packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, "", "who", get_sha256(""), "")
                    messageList.append(("", "who", ""))
                elif  userInput[0] == "bye":
                    packetNum = send_packet(clientSocket, packetStruct, VERSION, packetNum, user, "", "bye", get_sha256(""), "")
                    clientSocket.close()
                    exit()
                # an unexpected input was given
                else:
                    print("Unknown Command")

if __name__ == "__main__":
    main()
