# server.py
 
import sys, socket, select, utils

HOST = '' 
SOCKET_LIST = []
CHANNEL_LIST = []
SOCKET_USERNAME = {}
SOCKET_CHANNEL = {}
INC_MSG = {}
RECV_BUFFER = utils.MESSAGE_LENGTH

def pad_message(message):
  while len(message) < utils.MESSAGE_LENGTH:
    message += " "
  return message[:utils.MESSAGE_LENGTH]

def server():

    if(len(sys.argv) < 2) :
        print 'Usage : python server.py port'
        sys.exit()

    PORT = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
 
    # print "Chat server started on port " + str(PORT)
 
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
      
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                SOCKET_CHANNEL[sockfd] = None
                SOCKET_USERNAME[sockfd] = None
                INC_MSG[sockfd] = ""
                # print "Client (%s, %s) connected" % addr

            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        #case where message is less than 200 characters
                        if len(INC_MSG[sock]) < 200:
                            INC_MSG[sock] += data
                            if len(INC_MSG[sock]) < 200:
                                continue
                        data = INC_MSG[sock]
                        INC_MSG[sock] = ''
                        # initializing username
                        if SOCKET_USERNAME[sock] == None:
                            username = data.rstrip()
                            SOCKET_USERNAME[sock] = username
                            continue

                        message = data.rstrip()
                        length = len(message)
                        #control messages
                        if message[0] == '/':
                            #list
                            if length == 5 and message[1:5] == "list":
                                for channel in CHANNEL_LIST:
                                    sock.send(pad_message((channel)))
                            #join
                            elif length >= 5 and message[1:5] == "join":
                                if length == 5:
                                    sock.send(pad_message( "/join command must be followed by the name of a channel to join."))

                                elif message[6:length] != "":
                                    if message[5] != " ":
                                        sock.send(pad_message("%s is not a valid control message. Valid messages are /create, /list, and /join." %message))
                                    ch = message[6:length]
                                    if ch in CHANNEL_LIST:
                                        SOCKET_CHANNEL[sock] = ch
                                        broadcast(server_socket, sock, pad_message("%s has joined" % SOCKET_USERNAME[sock]))
                                    else:
                                        sock.send(pad_message( "No channel named %s exists. Try '/create %s'?" %(ch, ch)))
                            #create
                            elif length >= 7 and message[1:7] == "create":
                                if length == 7:
                                    sock.send(pad_message( "/create command must be followed by the name of a channel to create"))
                                elif message[8:length] != "":
                                    if message[7] != " ":
                                        sock.send(pad_message("%s is not a valid control message. Valid messages are /create, /list, and /join." %message))
                                    new_ch = message[8:length]

                                    if new_ch in CHANNEL_LIST:
                                        sock.send(pad_message("%s already exists, so cannot be created." %new_ch))
                                    else:
                                        if (SOCKET_CHANNEL[sock] != None):
                                            broadcast(server_socket, sock, pad_message("%s has left" % SOCKET_USERNAME[sock]))
                                        CHANNEL_LIST.append(new_ch)
                                        SOCKET_CHANNEL[sock] = new_ch

                            else:
                                sock.send(pad_message("%s is not a valid control message. Valid messages are /create, /list, and /join." %message))
                        #regular messages
                        else:
                            #user not in any channel
                            if SOCKET_CHANNEL[sock] == None:
                                sock.send(pad_message('Not currently in any channel. Must join a channel before sending messages.'))
                            else:
                                broadcast(server_socket, sock, '[' + SOCKET_USERNAME[sock] + '] ' + message)  
                    else: 
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "%s has left" % SOCKET_USERNAME[sock])

                # exception 
                except:
                    broadcast(server_socket, sock, "%s has left\n" % SOCKET_USERNAME[sock])
                    continue

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock and SOCKET_CHANNEL[sock] == SOCKET_CHANNEL[socket]:
            try :
                socket.send(pad_message(message))
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

 
if __name__ == "__main__":

    sys.exit(server())
