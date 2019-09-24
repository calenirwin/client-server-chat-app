from socket import *
serverPort = "50330"
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(1)
while True:
    connectionSocket, addr = serverSocket.accept()
    packet = connectionSocket.recv(512).decode
    connectionSocket.send(packet.upper().encode)
    connectionSocket.close()