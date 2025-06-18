import socket
import asyncio

# sets the top buffer and title
print("\033]1;James' message client\007\x1b[4;r", end = "", flush = True)
print("-------- check for updates on ")
print("❭")
print("--------")

# determines if the user wants to host or join
U_TYPE = input("'join' or 'host': ")
while not U_TYPE in ['join', 'host']:

    # moves back to the previous line and clears, before asking again
    U_TYPE = input("\x1b[1F\x1b[2K'join' or 'host': ")

if U_TYPE == "host":
    while True:
        MY_PORT = input("choose port (if unsure, '69420', or '80' as backup): ")
        try:
            int(MY_PORT)
        except ValueError:
            print("\x1b[1F\x1b[2K", end="", flush="")
        else:
            MY_PORT = int(MY_PORT)
            break

U_NAME = socket.gethostname()
U_IP_V4 = socket.gethostbyname(U_NAME)
timeout_count = 0
MAX_TIMEOUT = 3

# creates a new instance of socket, the first arg is saying AddresFrom_Internet,
# and second arg is saying it is a STREAMing type, using TCP
my_sock_inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def shutdown():
    """stops all running tasks"""
    loop = asyncio.get_running_loop()
    for task in asyncio.all_tasks(loop):
        task.cancel()
    loop.stop()

async def check_sent_msg():
    """checks if other user has sent any messages"""
    global timeout_count

    while True:
        loop = asyncio.get_running_loop()

        try:
            if U_TYPE == 'host':
                msg = await loop.run_in_executor(None, client_sock.recv, 1024)
            else:
                msg = await loop.run_in_executor(None, my_sock_inst.recv, 1024)
        
        # if the other socket is not responding,
        # then the program automatically closes        
        except ConnectionResetError:
            print("\x1b8 === connection lost ===")
            shutdown()
            return

        # responds to the ping with an acknowledgment 
        if msg == b"$%ping":
            if U_TYPE == 'host':
                client_sock.sendall(b"$%ack")
            else:
                my_sock_inst.sendall(b"$%ack")

        # resets the timeout_count to 0
        elif msg == b"$%ack":
            timeout_count = 0
        else:
            # restores cursor pos, prints message
            print("\x1b8", str(msg)[2:-1])

            # saves cursor pos; moves to top; clears line; adds '❭' symbol
            print("\x1b7\x1b[2;0H\x1b[2K❭ ", end = "", flush="True")

async def send_new_msg():
    """gets user input and sends message"""
    while True:

        # gets user input
        loop = asyncio.get_running_loop()
        msg = await loop.run_in_executor(None, input)

        # ensures spam is (semi-)prevented
        if msg == "":
            print("\x1b[1F❭ ", end= "", flush = True)
            continue

        # send to other person
        if U_TYPE == 'host':
            client_sock.sendall(f"{U_NAME}: {msg}".encode())
        else:
            my_sock_inst.sendall(f"{U_NAME}: {msg}".encode())
        
        # prints message on sender side
        print(f"\x1b8{U_NAME}: {msg}")
        print("\x1b7\x1b[2;0H\x1b[0K❭ ", end = "", flush="True")

async def check_connection():
    """pings the other user every three seconds"""
    global timeout_count

    while True:
        await asyncio.sleep(2)
        if U_TYPE == 'host':
            client_sock.sendall(b"$%ping")
        else:
            my_sock_inst.sendall(b"$%ping")

        timeout_count += 1

        # if there have been 3 pings in a row not acknowledged,
        # then it is assumed that the other user has quit
        if timeout_count > MAX_TIMEOUT:
            print("\x1b8 === connection lost ===")
            shutdown()
            return


async def main():
    if U_TYPE == "host":

        # binds the socket to a 'location' on my computer
        my_sock_inst.bind((U_IP_V4, MY_PORT))

        # provides the details for another user to connect with
        print(f"connection details: {U_IP_V4}-{MY_PORT}")
        print("\x1b7== WAITING FOR CONNECTION ==")

        # enables the socket to accept data
        my_sock_inst.listen()

        global client_sock
        global CLIENT_PORT

        # checks for another program to send data to it
        client_sock, CLIENT_PORT = my_sock_inst.accept()

        # returns to previous line; clears; moves up another line; clears; prints
        print(f"\x1b8\x1b[2K\x1b[1F\x1b[2Kconnected by {CLIENT_PORT}")

    else:
        SERVER_IP_V4, SERVER_PORT = input("connection details: ").strip().split("-")
        SERVER_PORT = int(SERVER_PORT)

        my_sock_inst.connect((SERVER_IP_V4, SERVER_PORT))

    print("--------")

    # saves cursor pos; moves to top; clears line; adds '❭' symbol
    print("\x1b7\x1b[2;0H\x1b[2K❭ ", end = "", flush="True")
    await asyncio.gather(check_sent_msg(), send_new_msg(), check_connection())
    
    # closes sockets
    my_sock_inst.close()

    if U_TYPE == "host":
        client_sock.close()

asyncio.run(main())
