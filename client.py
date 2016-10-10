# client.py

import sys, socket, select, utils
 
def pad_message(message):
  while len(message) < utils.MESSAGE_LENGTH:
    message += " "
  return message[:utils.MESSAGE_LENGTH]

def client():
    if(len(sys.argv) < 4) :
        print 'Usage : python client.py username hostname port'
        sys.exit()

    username = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect to %s:%d' %(host, port) 
        sys.exit()
     
    s.send(pad_message(username))    
    sys.stdout.write('[Me] '); sys.stdout.flush()
     
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:            
            if sock == s:
                # incoming message from remote server
                data = sock.recv(4096)
                if not data :
                    print '\nServer at %s:%d has disconnected' %(host, port)
                    sys.exit()
                else :
                    message = data.rstrip()
                    sys.stdout.write(utils.CLIENT_WIPE_ME)
                    sys.stdout.write('\r' + message + '\n')
                    sys.stdout.write('[Me] '); sys.stdout.flush()     
            
            else :
                # user entered a message
                msg = sys.stdin.readline()
                s.send(pad_message(msg))
                sys.stdout.write('[Me] '); sys.stdout.flush() 

if __name__ == "__main__":

    sys.exit(client())

