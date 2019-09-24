from socket import *
lokiAddr = "192.197.151.116"
serverPort = "50330"
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((lokiAddr, serverPort))
clientSocket.send("toast".encode())
toast = clientSocket.recv(512).decode()
print(toast)
clientSocket.close()
