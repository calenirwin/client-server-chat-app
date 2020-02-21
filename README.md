Written by Calen Irwin, Ryland Willhans 

Written for Computer Networks

Request for Comments: ##### 

Last Modified 29 November 2019 

Version 3 

 

 

 

 

#Simple Chat Transfer Protocol 

 

Status of This Memo 

This document specifies an Internet protocol for the COIS community at Trent University, and requests discussion and suggestions for enhancements. Distribution of this memo is unlimited. 

 

Abstract 

This document is a specification of the basic protocol for Internet chat message transport. It was designed for the purposes of the second assignment of COIS-4310H Computer Networks Fall 2019 at Trent University. In this document the following will be outlined: summary and purpose of the Python application, architecture of the Python application, description of packet header, description of data portion of packet, and description of commands and syntax. 

 

 

 

 

 

 

 

 

 

 

 

 

Application Summary 

The application written to demonstrate this protocol was written in Python 2.7 for UNIX based systems. The files that make up the application are server.py and client.py. 

The purpose of the application is to support a chat messaging service using a client-server connection over TCP. The application functions as follows. The server.py file is run in the command line using the command “python server.py”. Next, in another console window, clients can connect to the server using the command “python client.py”. Clients will immediately be asked to enter a username. After typing a username of maximum 20 characters, the client will be given a list of connected clients and all other connected clients will be notified of the new connection. Once connected, clients have the following commands: 

 

Send a message to another client 

Command: “john:this is my message” 

Send a message to all connected clients 

Command: “all:this is my message” 

Request a list of all connected clients 

Command: “who” 

Disconnect from the server 

Command: “bye” 

Toggle message encryption 

Command: “enc” 

 

Program Architecture 

The client-server relationship is established using sockets over TCP. Clients connect to the server on Loki’s IP Address 192.197.151.116 on Port 50330. Multiple clients can interact with each other via the central server. No more than five clients can connect to the server at one time. 

 

 

 

 

Header Format 

 

 

Note that one tick mark represents one bit position 

 

 

Version: 8 bits (1 byte) 

Version number – character 

Packet Number: 16 bits (2 bytes) 

Packet number - unsigned short integer 

Source Name: 168 bits (21 bytes) 

The name of the packet’s sender – first byte indicates length of string, next 20 bytes contain string padded with empty chars  

Destination Name: 168 bits (21 bytes) 

The name of the packet’s receiver - first byte indicates length of string, next 20 bytes contain string padded with empty chars  

Verb: 24 bits (3 bytes) 

The verb that specifies how the packet is handled – string 

Encryption: 64 bits (8 bytes) 

The type of encryption that is applied to the data portion, the receiving client should decrypt using the supplied method - string 

Checksum: 512 bits (64 bytes) 

SHA256 hash of the data portion of the packet - string 

Data: 2048 bits (256 bytes) 

The content of the message that is being sent 

Data Format 

The data portion of the packet is 256 bytes in size. The first byte is used to signify the length of the characters contained within the data portion. The remaining 255 bytes will always be filled with characters and should be interpreted as a string. If the message being sent is less than 255 characters, then the difference will be appended to the message as empty characters. The packet destination will remove the trailing characters based on the length given by the first byte before printing the message. 

 

 

Command Semantics 

Commands for the purposes of this protocol and program are referred to as verbs. Verbs are directions for how the receiving end is to handle the packet.  

 

Verbs 

all – This verb signifies that a message is being sent from one client (Source Name) to all clients connected to the server. The data portion contains the message. The server handles this verb by sending the message to all connected clients other than the sender. The client handles this verb by displaying the broadcast message source, indicating that the message is a broadcast, and displaying the message contained within the data portion. 

msg – This verb signifies that a message is being sent from one client (Source Name) to another client (Destination Name). The data portion contains the message. The server handles this verb by first determining if the destination is valid, and if so it sends the message to the client. If the destination is not valid, then it returns an error message to the sender. The client handles this verb by displaying the message source and the message contained within the data portion. 

 

srv- This verb signifies to the client that the packet is originating from the server. The data portion contains a non-error message for the client. The client handles this verb by displaying the message contained within the data portion. 

 

reb – This verb signifies to the client that their packet was corrupted. The data portion contains the packet number of the packet that needs to be rebroadcasted to the server. The client handles this verb by sending another packet containing the information from the original packet. This is possible because the client keeps track of the packet details (destination, verb, encryption, and message) for each packet sent. 

  

err- This verb signifies to the client that an error has occurred. The data portion contains a description of the error. The client handles this verb by displaying the message contained within the data portion and handles the error accordingly. 

 

con- This verb signifies that the packet (sent by a client) is an initial connection with the server. The data portion contains the desired username of the sender. The server handles this verb by checking if the given username is valid, and if so it registers the client, sends a confirmation and list of current connections to the new client, and sends a new connection notification to all other connected clients. If the username is not valid, then it returns an error message to the sender.  

 

who- This verb signifies that the client (Source Name) is requesting a list of clients connected to the server. The server handles this verb by sending a message containing all connected clients back to the sender. The client handles this verb by displaying the message contained within the data portion. 

 

 

References 

https://tools.ietf.org/html/rfc793 

https://tools.ietf.org/html/rfc5321 
