/*  Program:    COIS 3380 Lab 6 Client
 *  Author:     Ryland Whillans
 *  SN:         0618437
 *  Date:       2019-04-04
 *  Purpose:
 *      Connects to a server and requests a file to be transfered. Saves the result as a local copy.
 *  Dependancies:
 *      See include statements
 *  Software/Language:
 *      C
 *  Assumptions:
 *      file path will be less than 1024 characters long
 */


// attempt to connect
// if successful ask for username (not "all")
// send to Server
// fork child to wait for incoming messages and display
// main process waits for input
// input :
//  username
//  all
//  who

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define NAME_LENGTH 50
#define BLOCK_SIZE 1024                 // size of data exchange block
#define LOKI_ADDRESS "192.197.151.116"  // address of loki server

int Connect();                              // function to connect to server
int GetFile(int socketD, char inputName[]); // function to get file from server

// Connects to a server
int main(int argc, char *argv[])
{
    int socketD;                // socket to connect to server
    char fileName[BLOCK_SIZE];  // file name/path

    // Checks if too few or too many arguments, exits with code 1 if so
    if (argc < 2)
    {
        printf("Too few arguments\n");
        exit(1);
    }
    else if (argc > 2)
    {
        printf("Too many arguments\n");
        exit(1);
    }
    // copies file path parameter
    strncpy(fileName, argv[1], BLOCK_SIZE);

    // attempts to connect to server
    // exits with code 2 on failure
    if ((socketD = Connect()) < 0)
        exit(2);
    // Attempts to copy file from server
    // exits with code 3 on failure
    // if (GetFile(socketD, fileName) < 0)
    // {
    //     close(socketD);
    //     exit(3);
    // }

    // if successful, exit normally
    close(socketD);
    printf("\nClient - Exited normally\n");
    exit(0);
}

// connects to server using socket
// returns:
//  -1 on failure
//  socket descriptor on success
int Connect()
{
    int socketD;            // socket descriptor
    struct sockaddr_in srv; // used to connect socket
    fd_set fds;             // used with select to facilitate timeout
    struct timeval timeout; // used with select to facilitate timeout

    // create socket (non-blocking)
    if ((socketD = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0)) < 0)
    {
        perror("Creating Socket");
        return (-1);
    }
    // set values to connect to server
    srv.sin_family = AF_INET;
    srv.sin_port = htons(58437);
    srv.sin_addr.s_addr = inet_addr(LOKI_ADDRESS);

    printf("\nConnecting to server\n");
    // Attempt to connect to server
    connect(socketD, (struct sockaddr *)&srv, sizeof(srv));
    // set values for select/timeout
    timeout.tv_sec = 1;
    FD_ZERO(&fds);
    FD_SET(socketD, &fds);
    // wait for one second and if server not connected, exit
    if (select(socketD+1, &fds, 0, 0, &timeout) != 0){
        printf("Failed to connect to server\n");
        close(socketD);
        return (-1);
    }
    // set socket to blocking
    if (fcntl(socketD, F_SETFL, fcntl(socketD, F_GETFL) & ~O_NONBLOCK))
    {
        perror("fcntl");
        close(socketD);
        return (-1);
    }
    // return socket
    return socketD;
}

int Login(int socketD){
  char username[NAME_LENGTH];
}
// recieves file from server and saves to file
// Parameters:
//  int socketD     - socket to connect with
//  char inputName  - file name to request
// returns:
//  -1 on failure
//  0 on success
int GetFile(int socketD, char inputName[BLOCK_SIZE])
{
    int fd;                 // file descriptor for output
    int numBytes;           // number of bytes recieved
    char buf[BLOCK_SIZE];   // buffer for data from server
    char outputName[BLOCK_SIZE + 12];      // holds output file name
    char message[] = "Finished recieving file"; // message to send on completion
    int namePos;            // start position of filename in path
    // search path for last instance of "/" and save position
    for (namePos = BLOCK_SIZE - 1; namePos >= 0; namePos--)
    {
        if (inputName[namePos] == '/')
        {
            namePos++;
            break;
        }
    }
    // copy path after last "/" (input file name) for output file name
    strncpy(outputName, inputName + namePos, BLOCK_SIZE - namePos);
    outputName[BLOCK_SIZE - 1] = '\0';
    // add "_local_clone" to output file name
    strncat(outputName, "_local_clone", 13);

    // opens file for output
    if ((fd = open(outputName, O_WRONLY | O_CREAT | O_TRUNC, 0644)) == -1)
    {
        perror("Opening Output File");
        return (-1);
    }

    // sends file path to server
    if (send(socketD, inputName, BLOCK_SIZE, 0) < 0)
    {
        perror("Sending to Server");
        close(fd);
        close(socketD);
        return (-1);
    }

    // loop receiving until less than BLOCK_SIZE transfered (assumes end of file)
    do
    {
        // recieve data from server
        if ((numBytes = recv(socketD, &buf, BLOCK_SIZE, 0)) < 0)
        {
            perror("Receiving from Server");
            close(fd);
            close(socketD);
            return (-1);
        }
        printf("\nClient - Recieved %i bytes\n", numBytes);
        // writes data to file
        if (write(fd, buf, numBytes) < 0)
        {
            perror("Writing to Output File");
            close(fd);
            close(socketD);
            return (-1);
        }
    } while (numBytes == BLOCK_SIZE);

    // sends completion message to server
    if (send(socketD, message, sizeof(message), 0) < 0)
    {
        perror("Sending to Server");
        close(fd);
        close(socketD);
        return (-1);
    }
    close(fd);
    return (0);
}
