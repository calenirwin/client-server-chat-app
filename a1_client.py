from socket import *
from struct import *
VERSION = "1"
packetStruct = Struct("!Hc21p21p11p256p")
packetNum = 0

lokiAddr = "192.197.151.116"
serverPort = 50330
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((lokiAddr, serverPort))
# todo: get username/confirm
# todo: get input/ select
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



