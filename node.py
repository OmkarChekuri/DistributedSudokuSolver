#to run thread pool executor
from concurrent import futures
#for logging purposes
import logging
import sudoku_pb2_grpc
import sudoku_pb2
import grpc
import time
import threading
import socket
import pandas as pd
import multiprocessing
sleepseconds = 0

#custom function to encrypt message
'''
The encrypt function takes the parameters original message, the public key (n,e) of the destination.
It takes the message and converts each character into ascii code.
It then adds n^e from the public key (n,e) received from server to the ascii code of each character.
It then adds random characters to the resulting number and does this for all the characters while
concatenating the result to form the encrypted message.

'''
def encrypt(n,e,message):
    #print( "line 2 " + messa)
    list =[]
    for i in message:
        list.append(ord(i)+(n**e))
        #print(type(ord(i)))
    #print(list)

    cipher = ""
    for i in list:
        cipher += "j" + str(i) + "l" 
    return cipher


#custom function to decrypting message
'''
The decrypt function takes the parameters the encrypted message, public key (n,e) to decrypt the message.
It starts of by removing the random characters from the encrypted message that separates the numbers obtained from
adding n^e to the ascii code. It then subtracts n^e from each of the numbers to get the ascii codes
It then converts the ascii codes to get the characters and then combines them to get the original message.
   

'''

def decrypt(n,e,message):
    #print("line 18 " + mess)
    cipher = message
    p = ""
    for i in cipher:
        if i.isnumeric():
            p+=i
        else:
            p+= ","

    templist = p.split(",")    
    decipherstring = ""
    for item in templist:
        if item.isnumeric():
            temp = int(item) - (n**e)
            decipherstring +=chr(temp)
    return decipherstring

#create a serve function that starts when the server is started
def serve():
    print("server  started")
    n_value = 7
    e_value = 5
    timeslotDict = {"client1":0, "client2":0, "client3":0, "client4":0, "client5":0, "client6":0, "client7":0, "client8":0, "client9":0}

    #clients send their name as encripted message which is decrypted
    encriptedDictionary = {}

    #sudoku
    board = [[0,1,0,0,8,0,0,2,4],
           [5,9,0,0,0,0,0,0,1],
           [0,2,4,1,0,3,5,7,0],
           [1,0,0,0,0,0,0,0,5],
           [0,0,5,8,0,9,4,0,0],
           [9,0,0,0,0,0,0,0,7],
           [0,5,9,4,0,2,1,8,0],
           [4,0,1,0,0,0,0,0,2],
           [0,6,0,0,1,0,0,4,0]]
    
    #client topology
    neighbours =    {"client1":["client2","client4"], "client2":["client1","client3","client5"],"client3":["client2","client5"],
    "client4":["client1","client5","client7"],"client5":["client2","client4","client6","client8"], "client6":["client3","client5","client9"],
    "client7":["client4","client8"], "client8":["client5","client7","client9"],"client9":["client6","client8"]}

    activeclients = []

    class SecureMessaging1(sudoku_pb2_grpc.SecureMessagingServicer):
        def GetPublicKey(self,request,context):
            if request.status == 1:
                response = sudoku_pb2.PublicKey()
                response.n = n_value
                response.e = e_value
                print("server sending public key [" + str(response.n) + "," + str(response.e) + "]"  )
                return response
    
        def SendEncryptedMessage(self,request,context):
            #print(request)
            response = sudoku_pb2.MsgAck()
            response.status = 1
            response.src = request.src
            response.dst = request.dst
            #print(response.dst + " recieved " + request.message + " from " + response.src)
            print(request.dst + " recieved encrypted messsage " + request.message + " from " + request.src)
            message = decrypt(n_value,e_value,request.message)
            print("Server decrypted the messsage to " + message)
            print(request.dst + " sent acknowledgement to " + request.src)
            encriptedDictionary[request.src] = message
            activeclients.append(message)
            message =""

            
            return response

        def isMyNeighboursActive(self,request,context):
            
            requester = request.position
            response = sudoku_pb2.Neighbor()
            if all(x in activeclients for x in neighbours[requester]):
                response.N_list.extend(neighbours[requester])
            else:
                response.N_list.extend([])
            
            return response
            

        def GetRoundRobinToken(self,request,context):
            #print(request)
            if request.position in timeslotDict.keys() :
                response = sudoku_pb2.Token()
                requester= request.position
                #if it has already been assigned a valid token return it
                if timeslotDict[requester] > 0:
                    response.timeslot = timeslotDict[requester]
                    print(requester , "-----token------ " ,response.timeslot )
                    timeslotDict[requester] = response.timeslot -1
                #if none of the clients have a valid token then create a valid token for thid client    
                elif not(len([value for value in timeslotDict.values() if value >0])):
                    timeslotDict[requester] = 6
                    response.timeslot = 6
                else:
                    response.timeslot = 0
                
                #print(response.dst + " recieved " + request.message + " from " + response.src)
                #if response.timeslot > 0:
                    #print(request.position , "requested timeslot is " ,response.timeslot )

            
            return response


            
            
        def GetSubMatrix(self,request,context):
            pandas_board = pd.DataFrame(board)
            response = sudoku_pb2.subMatrix()
            if request.position == "client1" and request.position in encriptedDictionary.keys() :
                response.src = "server"
                response.dst = request.position
                print(response.src, "sending matrix to ", request.position)
                subsudoku = pandas_board.iloc[0:3,0:3].values.tolist()
                response.subrow0.extend(subsudoku[0])
                response.subrow1.extend(subsudoku[1])
                response.subrow2.extend(subsudoku[2])
            elif request.position == "client2" and request.position in encriptedDictionary.keys() :
                response.src = "server"
                response.dst = request.position
                print(response.src, "sending matrix to ", request.position)
                subsudoku = pandas_board.iloc[0:3,3:6].values.tolist()
                response.subrow0.extend(subsudoku[0])
                response.subrow1.extend(subsudoku[1])
                response.subrow2.extend(subsudoku[2])
            elif request.position == "client3" and request.position in encriptedDictionary.keys() :
                response.src = "server"
                response.dst = request.position
                print(response.src, "sending matrix to ", request.position)
                subsudoku = pandas_board.iloc[0:3,6:9].values.tolist()
                response.subrow0.extend(subsudoku[0])
                response.subrow1.extend(subsudoku[1])
                response.subrow2.extend(subsudoku[2])
            elif request.position == "client4" and request.position in encriptedDictionary.keys() :
                response.src = "server"
                response.dst = request.position
                print(response.src, "sending matrix to ", request.position)
                subsudoku = pandas_board.iloc[3:6,0:3].values.tolist()
                response.subrow0.extend(subsudoku[0])
                response.subrow1.extend(subsudoku[1])
                response.subrow2.extend(subsudoku[2])
            elif request.position == "client5" and request.position in encriptedDictionary.keys() :
                response.src = "server"
                response.dst = request.position
                print(response.src, "sending matrix to ", request.position)
                subsudoku = pandas_board.iloc[3:6,3:6].values.tolist()
                response.subrow0.extend(subsudoku[0])
                response.subrow1.extend(subsudoku[1])
                response.subrow2.extend(subsudoku[2]) 
            elif request.position == "client6" and request.position in encriptedDictionary.keys() :
                response.src = "server"
                response.dst = request.position
                print(response.src, "sending matrix to ", request.position)
                subsudoku = pandas_board.iloc[3:6,6:9].values.tolist()
                response.subrow0.extend(subsudoku[0])
                response.subrow1.extend(subsudoku[1])
                response.subrow2.extend(subsudoku[2])
            elif request.position == "client7" and request.position in encriptedDictionary.keys() :
                response.src = "server"
                response.dst = request.position
                print(response.src, "sending matrix to ", request.position)
                subsudoku = pandas_board.iloc[6:9,0:3].values.tolist()
                response.subrow0.extend(subsudoku[0])
                response.subrow1.extend(subsudoku[1])
                response.subrow2.extend(subsudoku[2])
            elif request.position == "client8" and request.position in encriptedDictionary.keys() :
                response.src = "server"
                response.dst = request.position
                print(response.src, "sending matrix to ", request.position)
                subsudoku = pandas_board.iloc[6:9,3:6].values.tolist()
                response.subrow0.extend(subsudoku[0])
                response.subrow1.extend(subsudoku[1])
                response.subrow2.extend(subsudoku[2])
            elif request.position == "client9" and request.position in encriptedDictionary.keys() :
                response.src = "server"
                response.dst = request.position
                print(response.src, "sending matrix to ", request.position)
                subsudoku = pandas_board.iloc[6:9,6:9].values.tolist()
                response.subrow0.extend(subsudoku[0])
                response.subrow1.extend(subsudoku[1])
                response.subrow2.extend(subsudoku[2])
            else:
                response.src = "server"
                response.dst = request.position
                print(response.src, "sending matrix to ", request.position)
                #send a dummy message
                response.subrow0.extend([0])
                response.subrow1.extend([0])
                response.subrow2.extend([0])      
            
                
            return response


        
    #print("serving")
  
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sudoku_pb2_grpc.add_SecureMessagingServicer_to_server(SecureMessaging1(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            #print("server running")
            #time.sleep(sleepseconds)
            pass
    except KeyboardInterrupt:
        print("keyboardinterrupt")
        server.stop(0)
    #server.setupserver()

def client1serve():

    print("client 1 sleeping")

    time.sleep(0)
    
    print("client 1 started")
    source = "client1"
    destination = "server"
    msg = "paris2024"

    row0 = []
    row1 = []
    row2 = []

    c2row0 = []
    c2row1 = []
    c2row2 = []

    c4row0 = []
    c4row1 = []
    c4row2 = []

    unsolved = True
    hasToken = False
    tokenValue = 0


    class SecureMessagingClient1(sudoku_pb2_grpc.SecureMessagingServicer):
               
            
        def GetSubMatrix(self,request,context):

            if request.position == "client2" or "client4":
                response.src = source
                response.dst = request.position
                #print(request.position, "requested matrix from ",response.src )
                #subsudoku = pandas_board.iloc[0:3,0:3].values.tolist()
                del response.subrow0[:]
                del response.subrow1[:]
                del response.subrow2[:]
                response.subrow0.extend(row0)
                response.subrow1.extend(row1)
                response.subrow2.extend(row2)
            
                
                
            return response


    #starting its ownserver
    client1 = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sudoku_pb2_grpc.add_SecureMessagingServicer_to_server(SecureMessagingClient1(), client1)
    client1.add_insecure_port('[::]:50052')
    client1.start()


    #client1.startclient1()
    #create aa communication channel to server
    channelServer = grpc.insecure_channel('server:50051', options=(('grpc.enable_http_proxy', 0),))
    stubToServer = sudoku_pb2_grpc.SecureMessagingStub(channelServer)
    print(source  +" requesting public key from " + destination)
    response = stubToServer.GetPublicKey(sudoku_pb2.NullMsg(status= 1 ))

    n = response.n
    e = response.e
    
    encryptedMessage = encrypt(n,e,source)
    
    print(source + " sending encrypted message " + encryptedMessage + " to " + destination)
    
    newresponse = stubToServer.SendEncryptedMessage(sudoku_pb2.EncryptedMessage(message=encryptedMessage, src = source, dst = destination))
    if newresponse.status ==1 and newresponse.src == source and newresponse.dst == destination:
        print(source + " recieved acknoledgement from " +destination)

    #initially requesting from server using stubToServer
    print(source  +" requesting client1 submatrix from " + destination)
    response = stubToServer.GetSubMatrix(sudoku_pb2.Address(position= source ))

    print(response.dst, "recieving sub sudoku from", response.src)
    row0 = response.subrow0[:]
    row1 = response.subrow1[:]
    row2 = response.subrow2[:]
    print(response.subrow0[:] )
    print(response.subrow1[:] )
    print(response.subrow2[:] )

    #print(type(response.subrow0[:]) )
    
    neighb_response = stubToServer.isMyNeighboursActive(sudoku_pb2.Address(position= source ))

    if not(neighb_response.N_list == []):
        print("neighbours are",neighb_response.N_list)
        
        #create a communication channel to client2 and client4 
        channelclient2 = grpc.insecure_channel('client2:50053', options=(('grpc.enable_http_proxy', 0),))
        stubToClient2 = sudoku_pb2_grpc.SecureMessagingStub(channelclient2)

        channelclient4 = grpc.insecure_channel('client4:50055', options=(('grpc.enable_http_proxy', 0),))
        stubToClient4 = sudoku_pb2_grpc.SecureMessagingStub(channelclient4)
    
        while unsolved :

            #request token from server
            TokenResponse = stubToServer.GetRoundRobinToken(sudoku_pb2.Address(position= source ))
            tokenValue = TokenResponse.timeslot
            if tokenValue > 0:
                
                hasToken = True

            else:
                hasToken = False

            if hasToken:
                responseFromClient2 = stubToClient2.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient2.dst, "requested", responseFromClient2.src)
                c2row0 = responseFromClient2.subrow0[:]
                c2row1 = responseFromClient2.subrow1[:]
                c2row2 = responseFromClient2.subrow2[:]
                print( "",c2row0,"\n",c2row1,"\n",c2row2)

                responseFromClient4 = stubToClient4.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient4.dst, "requested", responseFromClient4.src)
                c4row0 = responseFromClient4.subrow0[:]
                c4row1 = responseFromClient4.subrow1[:]
                c4row2 = responseFromClient4.subrow2[:]
                print( "",c4row0,"\n",c4row1,"\n",c4row2)

    try:
        while True:
            #print("server running")
            #time.sleep(sleepseconds)
            pass

    except KeyboardInterrupt:
        print("keyboardinterrupt")
        exit()

def client2serve():
    
    print("client 2 sleeping")
    time.sleep(0)

    print("client 2 started")
    source = "client2"
    destination = "server"
    msg = "la2028"

    row0 = []
    row1 = []
    row2 = []

    c1row0 = []
    c1row1 = []
    c1row2 = []


    c3row0 = []
    c3row1 = []
    c3row2 = []
    
    c5row0 = []
    c5row1 = []
    c5row2 = []
    
    unsolved = True
    hasToken = False
    tokenValue = 0




    class SecureMessagingClient1(sudoku_pb2_grpc.SecureMessagingServicer):
               
            
        def GetSubMatrix(self,request,context):

            if request.position == "client1" or "client3" or "client5" :
                response.src = source
                response.dst = request.position
                #print(request.position, "requested matrix from ",response.src )
                #subsudoku = pandas_board.iloc[0:3,0:3].values.tolist()
                del response.subrow0[:]
                del response.subrow1[:]
                del response.subrow2[:]
                response.subrow0.extend(row0)
                response.subrow1.extend(row1)
                response.subrow2.extend(row2)
                
                
            return response


    #starting its ownserver
    client2 = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sudoku_pb2_grpc.add_SecureMessagingServicer_to_server(SecureMessagingClient1(), client2)
    client2.add_insecure_port('[::]:50053')
    client2.start()
    



    #client1.startclient1()
    channelServer = grpc.insecure_channel('server:50051', options=(('grpc.enable_http_proxy', 0),))
    stubToServer = sudoku_pb2_grpc.SecureMessagingStub(channelServer)
    print(source  +" requesting public key from " + destination)
    response = stubToServer.GetPublicKey(sudoku_pb2.NullMsg(status= 1 ))
    n = response.n
    e = response.e

    encryptedMessage = encrypt(n,e,source)
    
    print(source + " sending encrypted message " + encryptedMessage + " to " + destination)
    newresponse = stubToServer.SendEncryptedMessage(sudoku_pb2.EncryptedMessage(message=encryptedMessage, src = source, dst = destination))
    if newresponse.status ==1 and newresponse.src == source and newresponse.dst == destination:
        print(source + " recieved acknoledgement from " +destination)
    #initially requesting from server using stubToServer
    print(source  +" requesting client1 submatrix from " + destination)
    response = stubToServer.GetSubMatrix(sudoku_pb2.Address(position= source ))

    print(response.dst, "recieving sub sudoku from", response.src)
    row0 = response.subrow0[:]
    row1 = response.subrow1[:]
    row2 = response.subrow2[:]
    print(response.subrow0[:] )
    print(response.subrow1[:] )
    print(response.subrow2[:] )
 
    neighb_response = stubToServer.isMyNeighboursActive(sudoku_pb2.Address(position= source ))

    if not(neighb_response.N_list == []):
        print("neighbours are",neighb_response.N_list)

    
        #create a communication channel to client1
        channelToClient1 = grpc.insecure_channel('client1:50052', options=(('grpc.enable_http_proxy', 0),))
        stubToClient1= sudoku_pb2_grpc.SecureMessagingStub(channelToClient1)

        channelToClient3 = grpc.insecure_channel('client3:50054', options=(('grpc.enable_http_proxy', 0),))
        stubToClient3= sudoku_pb2_grpc.SecureMessagingStub(channelToClient3)

        channelToClient5 = grpc.insecure_channel('client5:50056', options=(('grpc.enable_http_proxy', 0),))
        stubToClient5= sudoku_pb2_grpc.SecureMessagingStub(channelToClient5)

        while unsolved:

            #request token from server

            TokenResponse = stubToServer.GetRoundRobinToken(sudoku_pb2.Address(position= source ))
            tokenValue = TokenResponse.timeslot
            if tokenValue > 0:
                hasToken = True
            else:
                hasToken = False

            if hasToken:
                #print(type(response.subrow0[:]) )
                responseFromClient1 = stubToClient1.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient1.dst, "requested", responseFromClient1.src)
                c1row0 = responseFromClient1.subrow0[:]
                c1row1 = responseFromClient1.subrow1[:]
                c1row2 = responseFromClient1.subrow2[:]
                print( "",c1row0,"\n",c1row1,"\n",c1row2)

                responseFromClient3 = stubToClient3.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient3.dst, "requested", responseFromClient3.src)
                c3row0 = responseFromClient3.subrow0[:]
                c3row1 = responseFromClient3.subrow1[:]
                c3row2 = responseFromClient3.subrow2[:]
                print( "",c3row0,"\n",c3row1,"\n",c3row2)
                
                responseFromClient5 = stubToClient5.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient5.dst, "requested", responseFromClient5.src)
                c5row0 = responseFromClient5.subrow0[:]
                c5row1 = responseFromClient5.subrow1[:]
                c5row2 = responseFromClient5.subrow2[:]
                print( "",c5row0,"\n",c5row1,"\n",c5row2)

    try:
        while True:
            #print("server running")
            #time.sleep(sleepseconds)
            pass
    except KeyboardInterrupt:
        print("keyboardinterrupt")
        exit()

def client3serve():
    print("client 3 sleeping")
    time.sleep(0)

    print("client 3 started")
    source = "client3"
    destination = "server"
    msg = "la2028"

    row0 = []
    row1 = []
    row2 = []

    c2row0 = []
    c2row1 = []
    c2row2 = []


    c6row0 = []
    c6row1 = []
    c6row2 = []
    
    
    unsolved = True
    hasToken = False
    tokenValue = 0


    class SecureMessagingClient1(sudoku_pb2_grpc.SecureMessagingServicer):
               
            
        def GetSubMatrix(self,request,context):

            if request.position == "client2" or "client6" :
                response.src = source
                response.dst = request.position
                #print(request.position, "requested matrix from ",response.src )
                #subsudoku = pandas_board.iloc[0:3,0:3].values.tolist()
                del response.subrow0[:]
                del response.subrow1[:]
                del response.subrow2[:]
                response.subrow0.extend(row0)
                response.subrow1.extend(row1)
                response.subrow2.extend(row2)
                
                
            return response

    #client1.startclient1()

    #starting its ownserver
    client3 = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sudoku_pb2_grpc.add_SecureMessagingServicer_to_server(SecureMessagingClient1(), client3)
    client3.add_insecure_port('[::]:50054')
    client3.start()



    channelServer = grpc.insecure_channel('server:50051', options=(('grpc.enable_http_proxy', 0),))
    stubToServer = sudoku_pb2_grpc.SecureMessagingStub(channelServer)
    print(source  +" requesting public key from " + destination)
    response = stubToServer.GetPublicKey(sudoku_pb2.NullMsg(status= 1 ))
    n = response.n
    e = response.e

    encryptedMessage = encrypt(n,e,source)
    
    print(source + " sending encrypted message " + encryptedMessage + " to " + destination)
    newresponse = stubToServer.SendEncryptedMessage(sudoku_pb2.EncryptedMessage(message=encryptedMessage, src = source, dst = destination))
    if newresponse.status ==1 and newresponse.src == source and newresponse.dst == destination:
        print(source + " recieved acknoledgement from " +destination)

    #initially requesting from server using stubToServer
    print(source  +" requesting client1 submatrix from " + destination)
    response = stubToServer.GetSubMatrix(sudoku_pb2.Address(position= source ))

    print(response.dst, "recieving sub sudoku from", response.src)
    row0 = response.subrow0[:]
    row1 = response.subrow1[:]
    row2 = response.subrow2[:]
    print(response.subrow0[:] )
    print(response.subrow1[:] )
    print(response.subrow2[:] )
 
    neighb_response = stubToServer.isMyNeighboursActive(sudoku_pb2.Address(position= source ))

    if not(neighb_response.N_list == []):
        print("neighbours are",neighb_response.N_list)
        #create a communication channel to client1
        channelToClient2 = grpc.insecure_channel('client2:50053', options=(('grpc.enable_http_proxy', 0),))
        stubToClient2= sudoku_pb2_grpc.SecureMessagingStub(channelToClient2)

        channelToClien6 = grpc.insecure_channel('client6:50057', options=(('grpc.enable_http_proxy', 0),))
        stubToClient6= sudoku_pb2_grpc.SecureMessagingStub(channelToClien6)
    
        while unsolved:

            #request token from server

            TokenResponse = stubToServer.GetRoundRobinToken(sudoku_pb2.Address(position= source ))
            tokenValue = TokenResponse.timeslot
            if tokenValue > 0:
                hasToken = True
            else:
                hasToken = False

            if hasToken:
                #print(type(response.subrow0[:]) )
                responseFromClient2 = stubToClient2.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient2.dst, "requested", responseFromClient2.src)
                c2row0 = responseFromClient2.subrow0[:]
                c2row1 = responseFromClient2.subrow1[:]
                c2row2 = responseFromClient2.subrow2[:]
                print( "",c2row0,"\n",c2row1,"\n",c2row2)
                
                responseFromClient6 = stubToClient6.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient6.dst, "requested", responseFromClient6.src)
                c6row0 = responseFromClient6.subrow0[:]
                c6row1 = responseFromClient6.subrow1[:]
                c6row2 = responseFromClient6.subrow2[:]
                print( "",c6row0,"\n",c6row1,"\n",c6row2)
                

    try:
        while True:
            #print("server running")
            #time.sleep(sleepseconds)
            pass

    except KeyboardInterrupt:
        print("keyboardinterrupt")
        exit()
       
def client4serve():
   #time.sleep(0)(4)
    time.sleep(0)
    print("client 4 started")
    source = "client4"
    destination = "server"
    msg = "la2028"

    row0 = []
    row1 = []
    row2 = []

    c1row0 = []
    c1row1 = []
    c1row2 = []


    c5row0 = []
    c5row1 = []
    c5row2 = []
    
    c7row0 = []
    c7row1 = []
    c7row2 = []
    
    
    unsolved = True
    hasToken = False
    tokenValue = 0

    class SecureMessagingClient1(sudoku_pb2_grpc.SecureMessagingServicer):
               
            
        def GetSubMatrix(self,request,context):

            if request.position == "client1" or "client5" or "client7" :
                response.src = source
                response.dst = request.position
                #print(request.position, "requested matrix from ",response.src )
                #subsudoku = pandas_board.iloc[0:3,0:3].values.tolist()
                del response.subrow0[:]
                del response.subrow1[:]
                del response.subrow2[:]
                response.subrow0.extend(row0)
                response.subrow1.extend(row1)
                response.subrow2.extend(row2)
                
                
            return response

    #starting its ownserver
    client4 = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sudoku_pb2_grpc.add_SecureMessagingServicer_to_server(SecureMessagingClient1(), client4)
    client4.add_insecure_port('[::]:50055')
    client4.start()
    print("client 4 sleeping")
   #time.sleep(0)(1)

    #client1.startclient1()
    channelServer = grpc.insecure_channel('server:50051', options=(('grpc.enable_http_proxy', 0),))
    stubToServer = sudoku_pb2_grpc.SecureMessagingStub(channelServer)
    print(source  +" requesting public key from " + destination)
    response = stubToServer.GetPublicKey(sudoku_pb2.NullMsg(status= 1 ))
    n = response.n
    e = response.e

    encryptedMessage = encrypt(n,e,source)
    
    print(source + " sending encrypted message " + encryptedMessage + " to " + destination)
    newresponse = stubToServer.SendEncryptedMessage(sudoku_pb2.EncryptedMessage(message=encryptedMessage, src = source, dst = destination))
    if newresponse.status ==1 and newresponse.src == source and newresponse.dst == destination:
            print(source + " recieved acknoledgement from " +destination)
    #initially requesting from server using stubToServer
    print(source  +" requesting client1 submatrix from " + destination)
    response = stubToServer.GetSubMatrix(sudoku_pb2.Address(position= source ))

    print(response.dst, "recieving sub sudoku from", response.src)
    row0 = response.subrow0[:]
    row1 = response.subrow1[:]
    row2 = response.subrow2[:]
    print(response.subrow0[:] )
    print(response.subrow1[:] )
    print(response.subrow2[:] )

    neighb_response = stubToServer.isMyNeighboursActive(sudoku_pb2.Address(position= source ))

    if not(neighb_response.N_list == []):
        print("neighbours are",neighb_response.N_list)
        #create a communication channel to client1
        channelToClient1 = grpc.insecure_channel('client1:50052', options=(('grpc.enable_http_proxy', 0),))
        stubToClient1= sudoku_pb2_grpc.SecureMessagingStub(channelToClient1)

        channelToClient5 = grpc.insecure_channel('client5:50056', options=(('grpc.enable_http_proxy', 0),))
        stubToClient5= sudoku_pb2_grpc.SecureMessagingStub(channelToClient5)

        channelToClient7 = grpc.insecure_channel('client7:50058', options=(('grpc.enable_http_proxy', 0),))
        stubToClient7 = sudoku_pb2_grpc.SecureMessagingStub(channelToClient7)
 
        while unsolved:

            #request token from server

            TokenResponse = stubToServer.GetRoundRobinToken(sudoku_pb2.Address(position= source ))
            tokenValue = TokenResponse.timeslot
            if tokenValue > 0:
                hasToken = True
            else:
                hasToken = False

            if hasToken:
                #print(type(response.subrow0[:]) )
                responseFromClient1 = stubToClient1.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient1.dst, "requested", responseFromClient1.src)
                c1row0 = responseFromClient1.subrow0[:]
                c1row1 = responseFromClient1.subrow1[:]
                c1row2 = responseFromClient1.subrow2[:]
                print( "",c1row0,"\n",c1row1,"\n",c1row2)
                
               
                responseFromClient5 = stubToClient5.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient5.dst, "requested", responseFromClient5.src)
                c5row0 = responseFromClient5.subrow0[:]
                c5row1 = responseFromClient5.subrow1[:]
                c5row2 = responseFromClient5.subrow2[:]
                print( "",c5row0,"\n",c5row1,"\n",c5row2)

                responseFromClient7 = stubToClient7.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient7.dst, "requested", responseFromClient7.src)
                c7row0 = responseFromClient7.subrow0[:]
                c7row1 = responseFromClient7.subrow1[:]
                c7row2 = responseFromClient7.subrow2[:]
                print( "",c7row0,"\n",c7row1,"\n",c7row2)
                
    try:
        while True:
            #print("server running")
            #time.sleep(sleepseconds)
            pass

    except KeyboardInterrupt:
        print("keyboardinterrupt")
        exit()
    
    
def client5serve():

    #time.sleep(0)(4)
    time.sleep(0)
    print("client 5 started")
    source = "client5"
    destination = "server"
    msg = "paris2024"
    
    row0 = []
    row1 = []
    row2 = []

    c2row0 = []
    c2row1 = []
    c2row2 = []

    c4row0 = []
    c4row1 = []
    c4row2 = []

    c6row0 = []
    c6row1 = []
    c6row2 = []

    c8row0 = []
    c8row1 = []
    c8row2 = []




    unsolved = True
    hasToken = False
    tokenValue = 0

    class SecureMessagingClient1(sudoku_pb2_grpc.SecureMessagingServicer):
               
            
        def GetSubMatrix(self,request,context):

            if request.position == "client2" or "client4" or "client6" or "client8" :
                response.src = source
                response.dst = request.position
                #print(request.position, "requested matrix from ",response.src )
                #subsudoku = pandas_board.iloc[0:3,0:3].values.tolist()
                del response.subrow0[:]
                del response.subrow1[:]
                del response.subrow2[:]
                response.subrow0.extend(row0)
                response.subrow1.extend(row1)
                response.subrow2.extend(row2)
                
                
            return response


    #starting its ownserver
    client5 = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sudoku_pb2_grpc.add_SecureMessagingServicer_to_server(SecureMessagingClient1(), client5)
    client5.add_insecure_port('[::]:50056')
    client5.start()
    print("client 5 sleeping")
   #time.sleep(0)(1)

    #client1.startclient1()
    #create aa communication channel to server
    channelServer = grpc.insecure_channel('server:50051', options=(('grpc.enable_http_proxy', 0),))
    stubToServer = sudoku_pb2_grpc.SecureMessagingStub(channelServer)
    print(source  +" requesting public key from " + destination)
    response = stubToServer.GetPublicKey(sudoku_pb2.NullMsg(status= 1 ))
    n = response.n
    e = response.e

    encryptedMessage = encrypt(n,e,source)
    
    print(source + " sending encrypted message " + encryptedMessage + " to " + destination)
    newresponse = stubToServer.SendEncryptedMessage(sudoku_pb2.EncryptedMessage(message=encryptedMessage, src = source, dst = destination))
    if newresponse.status ==1 and newresponse.src == source and newresponse.dst == destination:
            print(source + " recieved acknoledgement from " +destination)
    
    #initially requesting from server using stubToServer
    print(source  +" requesting client1 submatrix from " + destination)
    response = stubToServer.GetSubMatrix(sudoku_pb2.Address(position= source ))

    print(response.dst, "recieving sub sudoku from", response.src)
    row0 = response.subrow0[:]
    row1 = response.subrow1[:]
    row2 = response.subrow2[:]
    print(response.subrow0[:] )
    print(response.subrow1[:] )
    print(response.subrow2[:] )

    #print(type(response.subrow0[:]) )

    neighb_response = stubToServer.isMyNeighboursActive(sudoku_pb2.Address(position= source ))

    if not(neighb_response.N_list == []):
        print("neighbours are",neighb_response.N_list)
       
        #create a communication channel to client2
        channelclient2 = grpc.insecure_channel('client2:50053', options=(('grpc.enable_http_proxy', 0),))
        stubToClient2 = sudoku_pb2_grpc.SecureMessagingStub(channelclient2)

        channelclient4 = grpc.insecure_channel('client4:50055', options=(('grpc.enable_http_proxy', 0),))
        stubToClient4 = sudoku_pb2_grpc.SecureMessagingStub(channelclient4)

        channelclient6 = grpc.insecure_channel('client6:50057', options=(('grpc.enable_http_proxy', 0),))
        stubToClient6 = sudoku_pb2_grpc.SecureMessagingStub(channelclient6)

        channelclient8 = grpc.insecure_channel('client8:50059', options=(('grpc.enable_http_proxy', 0),))
        stubToClient8 = sudoku_pb2_grpc.SecureMessagingStub(channelclient8)

        while unsolved :

            #request token from server
            TokenResponse = stubToServer.GetRoundRobinToken(sudoku_pb2.Address(position= source ))
            tokenValue = TokenResponse.timeslot
            if tokenValue > 0:
                
                hasToken = True

            else:
                hasToken = False

            if hasToken:
                responseFromClient2 = stubToClient2.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient2.dst, "requested", responseFromClient2.src)
                c2row0 = responseFromClient2.subrow0[:]
                c2row1 = responseFromClient2.subrow1[:]
                c2row2 = responseFromClient2.subrow2[:]
                print( "",c2row0,"\n",c2row1,"\n",c2row2)

                responseFromClient4 = stubToClient4.GetSubMatrix(sudoku_pb2.Address(position= source))
                print(responseFromClient4.dst, "requested", responseFromClient4.src)
                c4row0 = responseFromClient4.subrow0[:]
                c4row1 = responseFromClient4.subrow1[:]
                c4row2 = responseFromClient4.subrow2[:]
                print( "",c4row0,"\n",c4row1,"\n",c4row2)

                responseFromClient6 = stubToClient6.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient6.dst, "requested", responseFromClient6.src)
                c6row0 = responseFromClient6.subrow0[:]
                c6row1 = responseFromClient6.subrow1[:]
                c6row2 = responseFromClient6.subrow2[:]
                print( "",c6row0,"\n",c6row1,"\n",c6row2)

                responseFromClient8 = stubToClient8.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient8.dst, "requested", responseFromClient8.src)
                c8row0 = responseFromClient8.subrow0[:]
                c8row1 = responseFromClient8.subrow1[:]
                c8row2 = responseFromClient8.subrow2[:]
                print( "",c8row0,"\n",c8row1,"\n",c8row2)

    try:
        while True:
            #print("server running")
            #time.sleep(sleepseconds)
            pass

    except KeyboardInterrupt:
        print("keyboardinterrupt")
        exit()

def client6serve():
   #time.sleep(0)(4)
    time.sleep(0)
    print("client 6 started")
    source = "client6"
    destination = "server"
    msg = "la2028"

    row0 = []
    row1 = []
    row2 = []

    c3row0 = []
    c3row1 = []
    c3row2 = []


    c5row0 = []
    c5row1 = []
    c5row2 = []

    c9row0 = []
    c9row1 = []
    c9row2 = []

    
    unsolved = True
    hasToken = False
    tokenValue = 0

    class SecureMessagingClient1(sudoku_pb2_grpc.SecureMessagingServicer):
               
            
        def GetSubMatrix(self,request,context):

            if request.position == "client3" or "client5" or "client9" :
                response.src = source
                response.dst = request.position
                #print(request.position, "requested matrix from ",response.src )
                #subsudoku = pandas_board.iloc[0:3,0:3].values.tolist()
                del response.subrow0[:]
                del response.subrow1[:]
                del response.subrow2[:]
                response.subrow0.extend(row0)
                response.subrow1.extend(row1)
                response.subrow2.extend(row2)
                
                
            return response

    #starting its ownserver
    client6 = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sudoku_pb2_grpc.add_SecureMessagingServicer_to_server(SecureMessagingClient1(), client6)
    client6.add_insecure_port('[::]:50057')
    client6.start()
    print("client 6 sleeping")
   #time.sleep(0)(1)

    #client1.startclient1()
    channelServer = grpc.insecure_channel('server:50051', options=(('grpc.enable_http_proxy', 0),))
    stubToServer = sudoku_pb2_grpc.SecureMessagingStub(channelServer)
    print(source  +" requesting public key from " + destination)
    response = stubToServer.GetPublicKey(sudoku_pb2.NullMsg(status= 1 ))
    n = response.n
    e = response.e

    encryptedMessage = encrypt(n,e,source)
    
    print(source + " sending encrypted message " + encryptedMessage + " to " + destination)
    newresponse = stubToServer.SendEncryptedMessage(sudoku_pb2.EncryptedMessage(message=encryptedMessage, src = source, dst = destination))
    if newresponse.status ==1 and newresponse.src == source and newresponse.dst == destination:
            print(source + " recieved acknoledgement from " +destination)

    #initially requesting from server using stubToServer
    print(source  +" requesting client1 submatrix from " + destination)
    response = stubToServer.GetSubMatrix(sudoku_pb2.Address(position= source ))

    print(response.dst, "recieving sub sudoku from", response.src)
    row0 = response.subrow0[:]
    row1 = response.subrow1[:]
    row2 = response.subrow2[:]
    print(response.subrow0[:] )
    print(response.subrow1[:] )
    print(response.subrow2[:] )
 
    neighb_response = stubToServer.isMyNeighboursActive(sudoku_pb2.Address(position= source ))

    if not(neighb_response.N_list == []):
        print("neighbours are",neighb_response.N_list)
         
        #create a communication channel to client3 5 9
        channelToClient3 = grpc.insecure_channel('client3:50054', options=(('grpc.enable_http_proxy', 0),))
        stubToClient3= sudoku_pb2_grpc.SecureMessagingStub(channelToClient3)

        channelToClient5 = grpc.insecure_channel('client5:50056', options=(('grpc.enable_http_proxy', 0),))
        stubToClient5= sudoku_pb2_grpc.SecureMessagingStub(channelToClient5)

        channelclient9 = grpc.insecure_channel('client9:50060', options=(('grpc.enable_http_proxy', 0),))
        stubToClient9 = sudoku_pb2_grpc.SecureMessagingStub(channelclient9)
        while unsolved:

            #request token from server

            TokenResponse = stubToServer.GetRoundRobinToken(sudoku_pb2.Address(position= source ))
            tokenValue = TokenResponse.timeslot
            if tokenValue > 0:
                hasToken = True
            else:
                hasToken = False

            if hasToken:
                #print(type(response.subrow0[:]) )
                responseFromClient3 = stubToClient3.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient3.dst, "requested", responseFromClient3.src)
                c3row0 = responseFromClient3.subrow0[:]
                c3row1 = responseFromClient3.subrow1[:]
                c3row2 = responseFromClient3.subrow2[:]
                print( "",c3row0,"\n",c3row1,"\n",c3row2)
                
                responseFromClient5 = stubToClient5.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient5.dst, "requested", responseFromClient5.src)
                c5row0 = responseFromClient5.subrow0[:]
                c5row1 = responseFromClient5.subrow1[:]
                c5row2 = responseFromClient5.subrow2[:]
                print( "",c5row0,"\n",c5row1,"\n",c5row2)

                responseFromClient9 = stubToClient9.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient9.dst, "requested", responseFromClient9.src)
                c9row0 = responseFromClient9.subrow0[:]
                c9row1 = responseFromClient9.subrow1[:]
                c9row2 = responseFromClient9.subrow2[:]
                print( "",c9row0,"\n",c9row1,"\n",c9row2)
                

    try:
        while True:
            #print("server running")
            #time.sleep(sleepseconds)
            pass

    except KeyboardInterrupt:
        print("keyboardinterrupt")
        exit()
    
  
def client7serve():

   #time.sleep(0)(4)
    time.sleep(0)
    print("client 7 started")
    source = "client7"
    destination = "server"
    msg = "paris2024"
    
    row0 = []
    row1 = []
    row2 = []


    c4row0 = []
    c4row1 = []
    c4row2 = []


    c8row0 = []
    c8row1 = []
    c8row2 = []




    unsolved = True
    hasToken = False
    tokenValue = 0

    class SecureMessagingClient1(sudoku_pb2_grpc.SecureMessagingServicer):
               
            
        def GetSubMatrix(self,request,context):

            if request.position == "client4" or "client8" :
                response.src = source
                response.dst = request.position
                #print(request.position, "requested matrix from ",response.src )
                #subsudoku = pandas_board.iloc[0:3,0:3].values.tolist()
                del response.subrow0[:]
                del response.subrow1[:]
                del response.subrow2[:]
                response.subrow0.extend(row0)
                response.subrow1.extend(row1)
                response.subrow2.extend(row2)
                
                
            return response

    #print(type(response.subrow0[:]) )
    #starting its ownserver
    client7 = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sudoku_pb2_grpc.add_SecureMessagingServicer_to_server(SecureMessagingClient1(), client7)
    client7.add_insecure_port('[::]:50058')
    client7.start()

    print("client 7 sleeping")
   #time.sleep(0)(1)


    #client1.startclient1()
    #create aa communication channel to server
    channelServer = grpc.insecure_channel('server:50051', options=(('grpc.enable_http_proxy', 0),))
    stubToServer = sudoku_pb2_grpc.SecureMessagingStub(channelServer)
    print(source  +" requesting public key from " + destination)
    response = stubToServer.GetPublicKey(sudoku_pb2.NullMsg(status= 1 ))
    n = response.n
    e = response.e

    encryptedMessage = encrypt(n,e,source)
    
    print(source + " sending encrypted message " + encryptedMessage + " to " + destination)
    newresponse = stubToServer.SendEncryptedMessage(sudoku_pb2.EncryptedMessage(message=encryptedMessage, src = source, dst = destination))
    if newresponse.status ==1 and newresponse.src == source and newresponse.dst == destination:
            print(source + " recieved acknoledgement from " +destination)
    
    #initially requesting from server using stubToServer
    print(source  +" requesting client1 submatrix from " + destination)
    response = stubToServer.GetSubMatrix(sudoku_pb2.Address(position= source ))

    print(response.dst, "recieving sub sudoku from", response.src)
    row0 = response.subrow0[:]
    row1 = response.subrow1[:]
    row2 = response.subrow2[:]
    print(response.subrow0[:] )
    print(response.subrow1[:] )
    print(response.subrow2[:] )


    neighb_response = stubToServer.isMyNeighboursActive(sudoku_pb2.Address(position= source ))

    if not(neighb_response.N_list == []):
        print("neighbours are",neighb_response.N_list)
        
        channelclient4 = grpc.insecure_channel('client4:50055', options=(('grpc.enable_http_proxy', 0),))
        stubToClient4 = sudoku_pb2_grpc.SecureMessagingStub(channelclient4)

        channelclient8 = grpc.insecure_channel('client8:50059', options=(('grpc.enable_http_proxy', 0),))
        stubToClient8 = sudoku_pb2_grpc.SecureMessagingStub(channelclient8)

        while unsolved :

            #request token from server
            TokenResponse = stubToServer.GetRoundRobinToken(sudoku_pb2.Address(position= source ))
            tokenValue = TokenResponse.timeslot
            if tokenValue > 0:
                
                hasToken = True

            else:
                hasToken = False

            if hasToken:
                responseFromClient4 = stubToClient4.GetSubMatrix(sudoku_pb2.Address(position= source))
                print(responseFromClient4.dst, "requested", responseFromClient4.src)
                c4row0 = responseFromClient4.subrow0[:]
                c4row1 = responseFromClient4.subrow1[:]
                c4row2 = responseFromClient4.subrow2[:]
                print( "",c4row0,"\n",c4row1,"\n",c4row2)

                responseFromClient8 = stubToClient8.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient8.dst, "requested", responseFromClient8.src)
                c8row0 = responseFromClient8.subrow0[:]
                c8row1 = responseFromClient8.subrow1[:]
                c8row2 = responseFromClient8.subrow2[:]
                print( "",c8row0,"\n",c8row1,"\n",c8row2)

    try:
        while True:
            #print("server running")
            #time.sleep(sleepseconds)
            pass
    except KeyboardInterrupt:
        print("keyboardinterrupt")
        exit()
    
def client8serve():
   #time.sleep(0)(4)
    time.sleep(0)
    print("client 8 started")
    source = "client8"
    destination = "server"
    msg = "la2028"

    row0 = []
    row1 = []
    row2 = []

    c9row0 = []
    c9row1 = []
    c9row2 = []


    c5row0 = []
    c5row1 = []
    c5row2 = []
    
    c7row0 = []
    c7row1 = []
    c7row2 = []
    
    
    unsolved = True
    hasToken = False
    tokenValue = 0

    class SecureMessagingClient1(sudoku_pb2_grpc.SecureMessagingServicer):
               
            
        def GetSubMatrix(self,request,context):

            if request.position == "client9" or "client5" or "client7" :
                response.src = source
                response.dst = request.position
                #print(request.position, "requested matrix from ",response.src )
                #subsudoku = pandas_board.iloc[0:3,0:3].values.tolist()
                del response.subrow0[:]
                del response.subrow1[:]
                del response.subrow2[:]
                response.subrow0.extend(row0)
                response.subrow1.extend(row1)
                response.subrow2.extend(row2)
                
                
            return response

    #starting its ownserver
    client8 = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sudoku_pb2_grpc.add_SecureMessagingServicer_to_server(SecureMessagingClient1(), client8)
    client8.add_insecure_port('[::]:50059')
    client8.start()

    print("client 8 sleeping")
   #time.sleep(0)(1)

    #client1.startclient1()
    channelServer = grpc.insecure_channel('server:50051', options=(('grpc.enable_http_proxy', 0),))
    stubToServer = sudoku_pb2_grpc.SecureMessagingStub(channelServer)
    print(source  +" requesting public key from " + destination)
    response = stubToServer.GetPublicKey(sudoku_pb2.NullMsg(status= 1 ))
    n = response.n
    e = response.e

    encryptedMessage = encrypt(n,e,source)
    
    print(source + " sending encrypted message " + encryptedMessage + " to " + destination)
    newresponse = stubToServer.SendEncryptedMessage(sudoku_pb2.EncryptedMessage(message=encryptedMessage, src = source, dst = destination))
    if newresponse.status ==1 and newresponse.src == source and newresponse.dst == destination:
            print(source + " recieved acknoledgement from " +destination)

    #initially requesting from server using stubToServer
    print(source  +" requesting client1 submatrix from " + destination)
    response = stubToServer.GetSubMatrix(sudoku_pb2.Address(position= source ))

    print(response.dst, "recieving sub sudoku from", response.src)
    row0 = response.subrow0[:]
    row1 = response.subrow1[:]
    row2 = response.subrow2[:]
    print(response.subrow0[:] )
    print(response.subrow1[:] )
    print(response.subrow2[:] )
 

    
    #create a communication channel to client1
    neighb_response = stubToServer.isMyNeighboursActive(sudoku_pb2.Address(position= source ))

    if not(neighb_response.N_list == []):
        print("neighbours are",neighb_response.N_list) 
        channelToClient5 = grpc.insecure_channel('client5:50056', options=(('grpc.enable_http_proxy', 0),))
        stubToClient5= sudoku_pb2_grpc.SecureMessagingStub(channelToClient5)

        channelToClient7 = grpc.insecure_channel('client7:50058', options=(('grpc.enable_http_proxy', 0),))
        stubToClient7 = sudoku_pb2_grpc.SecureMessagingStub(channelToClient7)

        channelToClient9 = grpc.insecure_channel('client9:50060', options=(('grpc.enable_http_proxy', 0),))
        stubToClient9= sudoku_pb2_grpc.SecureMessagingStub(channelToClient9)
        while unsolved:

            #request token from server

            TokenResponse = stubToServer.GetRoundRobinToken(sudoku_pb2.Address(position= source ))
            tokenValue = TokenResponse.timeslot
            if tokenValue > 0:
                hasToken = True
            else:
                hasToken = False

            if hasToken:
                #print(type(response.subrow0[:]) )
              
               
                responseFromClient5 = stubToClient5.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient5.dst, "requested", responseFromClient5.src)
                c5row0 = responseFromClient5.subrow0[:]
                c5row1 = responseFromClient5.subrow1[:]
                c5row2 = responseFromClient5.subrow2[:]
                print( "",c5row0,"\n",c5row1,"\n",c5row2)

                responseFromClient7 = stubToClient7.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient7.dst, "requested", responseFromClient7.src)
                c7row0 = responseFromClient7.subrow0[:]
                c7row1 = responseFromClient7.subrow1[:]
                c7row2 = responseFromClient7.subrow2[:]
                print( "",c7row0,"\n",c7row1,"\n",c7row2)

                responseFromClient9 = stubToClient9.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient9.dst, "requested", responseFromClient9.src)
                c9row0 = responseFromClient9.subrow0[:]
                c9row1 = responseFromClient9.subrow1[:]
                c9row2 = responseFromClient9.subrow2[:]
                print( "",c9row0,"\n",c9row1,"\n",c9row2)
                
    try:
        while True:
            #print("server running")
            #time.sleep(sleepseconds)
            pass

    except KeyboardInterrupt:
        print("keyboardinterrupt")
        exit()
   

def client9serve():

   #time.sleep(0)(4)
    time.sleep(0)
    print("client 9 started")
    source = "client9"
    destination = "server"
    msg = "paris2024"
    
    row0 = []
    row1 = []
    row2 = []


    c6row0 = []
    c6row1 = []
    c6row2 = []

    c8row0 = []
    c8row1 = []
    c8row2 = []




    unsolved = True
    hasToken = False
    tokenValue = 0

    class SecureMessagingClient1(sudoku_pb2_grpc.SecureMessagingServicer):
               
            
        def GetSubMatrix(self,request,context):

            if request.position ==  "client6" or "client8" :
                response.src = source
                response.dst = request.position
                print(request.position, "requested matrix from ",response.src )
                #subsudoku = pandas_board.iloc[0:3,0:3].values.tolist()
                del response.subrow0[:]
                del response.subrow1[:]
                del response.subrow2[:]
                response.subrow0.extend(row0)
                response.subrow1.extend(row1)
                response.subrow2.extend(row2)
                
                
            return response

    #starting its ownserver
    client9 = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sudoku_pb2_grpc.add_SecureMessagingServicer_to_server(SecureMessagingClient1(), client9)
    client9.add_insecure_port('[::]:50056')
    client9.start()
    print("client 9 sleeping")
   #time.sleep(0)(1)


    #client1.startclient1()
    #create aa communication channel to server
    channelServer = grpc.insecure_channel('server:50051', options=(('grpc.enable_http_proxy', 0),))
    stubToServer = sudoku_pb2_grpc.SecureMessagingStub(channelServer)
    print(source  +" requesting public key from " + destination)
    response = stubToServer.GetPublicKey(sudoku_pb2.NullMsg(status= 1 ))
    n = response.n
    e = response.e

    encryptedMessage = encrypt(n,e,source)
    
    print(source + " sending encrypted message " + encryptedMessage + " to " + destination)
    newresponse = stubToServer.SendEncryptedMessage(sudoku_pb2.EncryptedMessage(message=encryptedMessage, src = source, dst = destination))
    if newresponse.status ==1 and newresponse.src == source and newresponse.dst == destination:
            print(source + " recieved acknoledgement from " +destination)
    
    #initially requesting from server using stubToServer
    print(source  +" requesting client1 submatrix from " + destination)
    response = stubToServer.GetSubMatrix(sudoku_pb2.Address(position= source ))

    print(response.dst, "recieving sub sudoku from", response.src)
    row0 = response.subrow0[:]
    row1 = response.subrow1[:]
    row2 = response.subrow2[:]
    print(response.subrow0[:] )
    print(response.subrow1[:] )
    print(response.subrow2[:] )

    #print(type(response.subrow0[:]) )


    neighb_response = stubToServer.isMyNeighboursActive(sudoku_pb2.Address(position= source ))

    if not(neighb_response.N_list == []):
        print("neighbours are",neighb_response.N_list)
        channelclient6 = grpc.insecure_channel('client6:50057', options=(('grpc.enable_http_proxy', 0),))
        stubToClient6 = sudoku_pb2_grpc.SecureMessagingStub(channelclient6)

        channelclient8 = grpc.insecure_channel('client8:50059', options=(('grpc.enable_http_proxy', 0),))
        stubToClient8 = sudoku_pb2_grpc.SecureMessagingStub(channelclient8)

        while unsolved :

            #request token from server
            TokenResponse = stubToServer.GetRoundRobinToken(sudoku_pb2.Address(position= source ))
            tokenValue = TokenResponse.timeslot
            if tokenValue > 0:
                
                hasToken = True

            else:
                hasToken = False

            if hasToken:
               
                responseFromClient6 = stubToClient6.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient6.dst, "requested", responseFromClient6.src)
                c6row0 = responseFromClient6.subrow0[:]
                c6row1 = responseFromClient6.subrow1[:]
                c6row2 = responseFromClient6.subrow2[:]
                print( "",c6row0,"\n",c6row1,"\n",c6row2)

                responseFromClient8 = stubToClient8.GetSubMatrix(sudoku_pb2.Address(position= source ))
                print(responseFromClient8.dst, "requested", responseFromClient8.src)
                c8row0 = responseFromClient8.subrow0[:]
                c8row1 = responseFromClient8.subrow1[:]
                c8row2 = responseFromClient8.subrow2[:]
                print( "",c8row0,"\n",c8row1,"\n",c8row2)

    try:
        while True:
            #print("server running")
            #time.sleep(sleepseconds)
            pass

    except KeyboardInterrupt:
        print("keyboardinterrupt")
        exit()




if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s %(message)s', level=logging.DEBUG)
    #serve()
    
    
    if socket.gethostname()  == "server":
        serve()
    time.sleep(10)


    if socket.gethostname() == "client1":
        client1serve()
    elif socket.gethostname() == "client2":
        client2serve()
    elif socket.gethostname() == "client3":
        client3serve()
    elif socket.gethostname() == "client4":
        client4serve()
    elif socket.gethostname() == "client5":
        client5serve()
    elif socket.gethostname() == "client6":
        client6serve()
    elif socket.gethostname() == "client7":
        client7serve()
    elif socket.gethostname() == "client8":
        client8serve()
    elif socket.gethostname() == "client9":
        client9serve()     
    
    
