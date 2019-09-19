/*==============================================================
|Program Name: client.c
|Written by: Calen Irwin [ 0630330 ] for COIS-4310H Assignment 1
|on Sept 12, 2019
|Purpose: To function as the client in a client/server
| 		  relationship that acts as a messenger application
================================================================*/

#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

#define HEADER_SIZE 128
#define DATA_SIZE 256

int main(int argc, char *argv[]) {

	int sd, fd;					// socket descriptor & file descriptor

	struct sockaddr_in server;

	struct packet {
		char header[HEADER_SIZE];
		char data[DATA_SIZE];
	};

	if ((sd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		perror("socket call failed");
		exit(1);
	}

	server.sin_family = AF_INET;

	server.sin_port = htons(50330);

	server.sin_addr.s_addr = inet_addr("192.197.151.116");

	if (connect(sd, (struct sockaddr *) &server, sizeof(server)) < 0) {		// connect to socket
		perror("connect call failed");
		exit(1);
	}

	fd = open("chat_logs", O_WRONLY|O_CREAT|O_TRUNC, 0644);	// open file to write to

	write(sd, argv[1], strlen(argv[1]));	// write the path given by the user to the server

	while ((bits_read = read(sd, &packet, BUF_SIZE)) > 0) {		// read from the server until no bits are read
		write(fd, &packet, bits_read);							// write to the opened file
	}

	close(fd);	// close file descriptor

	return 0;
}
