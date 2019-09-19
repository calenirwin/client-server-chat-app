/*  Program:    COIS 3380 Lab 6 Server
 *  Author:     Ryland Whillans
 *  SN:         0618437
 *  Date:       2019-04-04
 *  Purpose:    
 *      Creates a socket and waits for a client to connect. Accepts a file path and transfers the requested file to the client, then waits for a new client
 *  Dependancies:
 *      See include statements
 *  Software/Language:
 *      C
 */

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define BLOCK_SIZE 1024 // size of data exchange block

int ConnectSocket();    // sets up socket for connection
int ProcessClient(int socketD); // processes a connected client

// connects with clients via sockets and transfers files
// Exit codes:
//  0 exit normally
//  1 error connecting socket
//  2 error processing client
int main(int argc, char *argv[])
{
    int socketD;    // socket descriptor

    // connect socket
    if ((socketD = ConnectSocket()) < 0)
        exit(1);
    // loop infinitely processing clients
    while (1)
    {
        printf("\nServer - Waiting for client to connect\n");
        if (ProcessClient(socketD) < 0)
            exit(2);
    }
    exit(0);
}

// creates socket and sets up for client to connect 
// returns:
//  -1 on failure
//  socket descripter otherwise
int ConnectSocket()
{
    int socketD;    // socket descriptor
    struct sockaddr_in srv; // used to create socket
    // Creates socket
    if ((socketD = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("Creating Socket");
        return (-1);
    }
    // Set properties for socket
    srv.sin_family = AF_INET;
    srv.sin_port = htons(58437);
    srv.sin_addr.s_addr = htonl(INADDR_ANY);
    // bind to port
    if (bind(socketD, (struct sockaddr *)&srv, sizeof(srv)) < 0)
    {
        perror("Binding");
        close(socketD);
        return (-1);
    }
    // set to listen
    if (listen(socketD, 5) < 0)
    {
        perror("Listening");
        close(socketD);
        return (-1);
    }
    return socketD;
}

// Processes a client by accpeting a file path and transfering that file
// Parameters:
//  int socketD - socket for connection
// Returns:
//  -1 on failure
//  0 on success
int ProcessClient(int socketD)
{
    int newSocketD;         // socket descriptor to accept client
    struct sockaddr_in cli; // used to create client socket
    int fd;                 // file to transfer
    int numBytes;           // number of bytes transfered
    socklen_t cli_len = sizeof(cli);    // length for accept
    char buf[BLOCK_SIZE];       // buffer for reading
    char message[BLOCK_SIZE];   // message from client
    // wait to accept client connection
    if ((newSocketD = accept(socketD, (struct sockaddr *)&cli, &cli_len)) < 0)
    {
        perror("Accepting");
        return (-1);
    }
    printf("\nServer - Client Connected\n");

    // recieve file path to open
    if ((numBytes = recv(newSocketD, buf, BLOCK_SIZE, 0)) < 0)
    {
        perror("Receiving from Client");
        close(newSocketD);
        return (-1);
    }
    // open file path
    if ((fd = open(buf, O_RDONLY)) < 0)
    {
        perror("Opening Input File");
        close(newSocketD);
        return (-1);
    }
    
    printf("\nServer - Transfering file\n");
    // loop until file read completely
    // reads file into
    while ((numBytes = read(fd, buf, BLOCK_SIZE)) > 0)
    {
        // send data read into buffer from file to client
        if (send(newSocketD, buf, numBytes, 0) < 0)
        {
            perror("Sending to Client");
            close(fd);
            close(newSocketD);
            return (-1);
        }
        printf("\nServer - Sent %i bytes\n", numBytes);
    }
    if (numBytes < 0)
    {
        perror("Reading from File");
        close(fd);
        close(newSocketD);
        return (-1);
    }
    printf("\nServer - Finished transfering file \n");
    // Wait for comfirmation message from client
    if ((numBytes = recv(newSocketD, &buf, BLOCK_SIZE, 0)) < 0)
    {
        perror("Receiving from Server");
        close(fd);
        close(newSocketD);
        return (-1);
    }
    // output message and return
    strncpy(message, buf, numBytes);
    printf("\nServer - Recieved message from client: %s\n", message);

    close(fd);
    close(newSocketD);
    return (0);
}
