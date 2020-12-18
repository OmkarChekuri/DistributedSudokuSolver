How to start the program:
To start the fresh build of the docker run the following command with all the required files.
docker-compose up --build

The docker builds the required container and creates the clients and servers. 
it now executes the node.py file.

node.py is the main file it does the following tasks. 
1. It creates clients and servers. 

2. BOTH CLIENT AND SERVER HAVE ALREADY HAD A PUBLIC KEY WITH THEM. THIS KEY CONSISTS OF ANY TWO INTEGERS.

3. WHEN THE CLIENT WANTS TO ESTABLISH A CONNECTION WITH SERVER THE CLIENT REQUESTS THE PUBLIC KEY OF THE SERVER. 

4. THE SERVER SENDS ITS PUBLIC KEY TO THE CLIENT. THE CLIENT USES THE PUBLIC KEY TO ENCRIPT THE MESSAGE WITH ITS CUSTOM 
ENCRIPT FUNCTION.

5.THE ENCRYPT FUNCTION TAKES THE PARAMETERS ORIGINAL MESSAGE, THE PUBLIC KEY (N,E) OF THE DESTINATION. 
IT TAKES THE MESSAGE AND CONVERTS EACH CHARACTER INTO ASCII CODE. 
IT THEN ADDS N^E FROM THE PUBLIC KEY (N,E) RECEIVED FROM SERVER TO THE ASCII CODE OF EACH CHARACTER.
IT THEN ADDS RANDOM CHARACTERS TO THE RESULTING NUMBER AND DOES THIS FOR ALL THE CHARACTERS WHILE
CONCATENATING THE RESULT TO FORM THE ENCRYPTED MESSAGE.

6. IT NOW SENDS  THE ENCRYPTED MESSAGE AND TWO STRINGS ,ITS HOST NAME AND THE HOST NAME OF THE SERVER TO THE SERVER.

6. THE SERVER RECIEVES THE ENCRYPTED MESSAGE FROM THE CLIENT AND DECRYPTS THE MESSAGE WITH THE DECRYPTION FUNCTION.

7.THE DECRYPT FUNCTION TAKES THE PARAMETERS THE ENCRYPTED MESSAGE, PUBLIC KEY (N,E) TO DECRYPT THE MESSAGE.
IT STARTS OF BY REMOVING THE RANDOM CHARACTERS FROM THE ENCRYPTED MESSAGE THAT SEPARATES THE NUMBERS OBTAINED FROM
ADDING N^E TO THE ASCII CODE. IT THEN SUBTRACTS N^E FROM EACH OF THE NUMBERS TO GET THE ASCII CODES
IT THEN CONVERTS THE ASCII CODES TO GET THE CHARACTERS AND THEN COMBINES THEM TO GET THE ORIGINAL MESSAGE.

8. The server stores the sudoku.The encripted message from the server consists of the client name.
once the server verifies the client name. it sends the required cells or latin square corresponding to the client that requested.

9. Each client stores the names of its neighbours.They also define their own stubs similar to the server to act as servers.

10.The server implements a round robin scheduling algorithm.  In the server their is a dictionary that corresponds to entries of token
 assigned to the clients that determines whether it can talk to its neighbours. Initially all the tokens are zero. Whenever the client wants to communicate with its neighbours
 it checks the availability of the token with the server. If the token is not already assigned to other clients, the server allots a token of three time slots.
Every time the client communicates with all of its neighbours once the token is decremented by one. The client continues communicating with its neighbours until its token becomes zero.
Now the token is assigned to next in line client. THis continues in such a way that the token is allocated to the next available client.

11. Once the client verifies that its token is greater than zero, it then requests neighbours their latin square and gets it. it stores it in its data structure.
 By doing this every client maintains a redundant copy of its data with its neighbours. This continues as long as the client and server are alive. we can use other 
 micro services to change the data in any of the clients. 
 if we do that the data is automatically updated in its neighbours and the redundant copies of the data are maintained.


12. The proto file consists of the following method signatures for the below mentioned purposes.


    a)GetPublicKey: This method is used to communicate the security key between the client and the server. THe client requests the public key of the server using this method.

    b)SendEncryptedMessage: This method is used to send the identity of the client to the server in an encrypted message.

    c)GetSubMatrix: This method is used by the client to get its initial Latin square from the server as well as storing the litin squares of the neighbours with it.

    d)GetRoundRobinToken:  This method is used by the client to get the round robin key from the server and run only if the key or the token is valid.

  