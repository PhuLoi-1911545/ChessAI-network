import socket
import threading
import json
FORMAT = 'utf8'

data_list1 = []
data_list2 = []


def get_player2(conn):
    player2 = None
    if conn in data_list1:
        index = data_list1.index(conn)
        if index < len(data_list2):
            player2 = data_list2[index]
    else:
        index = data_list2.index(conn)
        if index < len(data_list1):
            player2 = data_list1[index]
    return player2


def handleClient(conn, addr):
    # with every client side
    player2 = None
    global data_list1, data_list2
    while True:
        try:
            msg = conn.recv(1024).decode(FORMAT)
        except:
            print('[CLOSE]', addr)
            conn.close()
            break
        msg = msg.split(" ")
        if msg[0] == 'USERNAME':
            if len(data_list1) <= len(data_list2):
                data_list1.append(conn)
                conn.sendall('WHITE'.encode(FORMAT))
            else:
                data_list2.append(conn)
                conn.sendall('BLACK'.encode(FORMAT))
            print('User', 'connected')


        if (msg[0] == 'EXIT'):
            print('[CLOSE]', addr)
            conn.close()
            return
        if (msg[0] == 'EXIT2'):
            print('[CLOSE]', addr)
            player2 = get_player2(conn)
            if player2 is None:
                return
            conn.close()
            return
        if (msg[0] == 'MOVE'):
            player2 = get_player2(conn)
            if player2 is None:
                return
            player2.sendall(f"MOVE {msg[1]} {msg[2]} {msg[3]} {msg[4]}".encode(FORMAT))


HOST = '127.0.0.1'
SERVER_ROOT = 65432
FORMAT = 'utf8'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# SOCK_STREAM
s.bind((HOST, SERVER_ROOT))
s.listen(10)

print('SERVER SIDE')
print('server: ', HOST, SERVER_ROOT)
print('Waiting for Client')

nClient = 0
while nClient < 10:
    try:
        conn, addr = s.accept()  # wait client connect
        # conn nhan va trao doi duong truyen
        # addr lay dia chi client
        thr = threading.Thread(target=handleClient, args=(conn, addr))
        thr.daemon = True  # kill thr
        thr.start()
    except socket.error as err:
        print('error', err)

    nClient += 1

s.close()
