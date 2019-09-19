/*==============================================================
|Program Name: server.c
|Written by: Calen Irwin [ 0630330 ] for COIS-4310H Assignment 1
|on April 12, 2019
|Purpose: To function as the server in a client/server
| 		  relationship that acts as a messenger application
================================================================*/

#include <sys/socket.h>
#include <netinet/in.h>
#include <ctype.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>

#define HEADER_SIZE 128
#define DATA_SIZE 256

int fd_new;

int main () {
	int sd;					// socket descriptor

	struct sockaddr_in server;
	struct sockaddr_in client;

	int client_length = sizeof(client);

	struct packet {
		char header[HEADER_SIZE];
		char data[DATA_SIZE];
	};

	if ((sd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {	// socket call
		perror("socket call failed");
		exit(1);
	}

	server.sin_family = AF_INET;
	server.sin_port = htons(50330);				// open on port 50330
	server.sin_addr.s_addr = htonl(INADDR_ANY);

	if (bind(sd, (struct sockaddr *) &server, sizeof(server)) < 0) {	// bind call
		perror("bind call failed");
		exit(1);
	}

	if (listen(sd, 5) < 0) {											// wait for clients to connect, max of 5
		perror ("listen call failed");
		exit(1);
	}

	while (conn = accept(sd, (struct sockaddr *)NULL, NULL)) {
		int pid;
		char username;

		if ((pid = fork()) == 0) {

			while (recv(conn, message, 100, 0) > 0) {
				printf("Messsage: %s", message);
				message = "";
			}
			exit(0);
		}
	}

	if ((fd_new = accept(sd, (struct sockaddr *) &client, &client_length)) < 0) {
		perror("accept call failed");
		exit(1);
	}

	read(fd_new, &file_path, BUF_SIZE);

	fd_from = open(file_path, O_RDONLY);

	while ((bits_read = read(fd_from, &packet, BUF_SIZE)) > 0) {		// read from opened file
		write(fd_new, &packet, bits_read);								// write to client
	}

	close(fd_new);
	close(fd_from);

	return 0;
}
