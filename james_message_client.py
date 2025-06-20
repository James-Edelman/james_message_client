import socket
import asyncio

# sets the top buffer and title
print("\033]1;James' message client\007\x1b[4;r", end = "", flush = True)
print("https://github.com/James-Edelman/James-message-client/")
print("❭")
print("--------")

# determines if the user wants to host or join
U_TYPE = input("'join' or 'host': ")
while not U_TYPE in ['join', 'host']:

    # moves back to the previous line and clears, before asking again
    U_TYPE = input("\x1b[1F\x1b[2K'join' or 'host': ")

# gets desired port
# I know that U_TYPE isn't a constant since it's overwritten, but close enough
if U_TYPE == "host":
    while True:
        U_PORT = input("\x1b[1F\x1b[2Kchoose port: ")
        try:
            int(U_PORT)
        except ValueError:
            print("\x1b[1F\x1b[2K", end="", flush="")
        else:
            U_PORT = int(U_PORT)
            break

U_NAME = socket.gethostname()
U_IP_V4 = socket.gethostbyname(U_NAME)
last_msg = ""

clients = []

# creates a new socket using IPV4 and as streaming type
my_sock_inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def shutdown():
    """stops all running tasks"""
    loop = asyncio.get_running_loop()
    for task in asyncio.all_tasks(loop):
        task.cancel()
    loop.stop()

async def check_sent_msg():
    """checks if other user has sent any messages"""

    loop = asyncio.get_running_loop()

    if U_TYPE != "host":
        while True:
            try:
                msg = await loop.run_in_executor(None, my_sock_inst.recv, 1024)

            # if the other socket is not responding,
            # then the program automatically closes  
            except ConnectionAbortedError:
                print("\x1b8 === connection lost ===")
                shutdown()

            except ConnectionResetError:
                print("\x1b8 === connection lost ===")
                shutdown()

            if msg == b"$%name":
                my_sock_inst.sendall(U_NAME.encode())
                continue

            # ensures echoed messages aren't printed twice
            elif msg == last_msg:
                continue

            # restores cursor pos, prints message
            print("\x1b8", str(msg)[2:-1])

            # saves cursor pos; moves to top; clears line; adds '❭' symbol
            print("\x1b7\x1b[2;0H\x1b[0K❭ ", end = "", flush="True")

    # clients are caught by the first loop
    while True:
        for socket_ in clients: 
            try:
                msg = socket_.recv(1024)
            except BlockingIOError:
                continue

            print("\x1b8", str(msg)[2:-1])
            print("\x1b7\x1b[2;0H\x1b[0K❭ ", end = "", flush=True)

            # echos the message back to the other clients
            # there are checks to ensure the sender doesn't receive it
            for socket__ in clients:
                socket__.sendall(msg)
        await asyncio.sleep(0.5)
       

async def send_new_msg():
    """gets user input and sends message"""
    global last_msg

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
            for client_ in clients:
                client_.sendall(f"{U_NAME}: {msg}".encode())
        else:
            my_sock_inst.sendall(f"{U_NAME}: {msg}".encode())
            last_msg = f"{U_NAME}: {msg}".encode()
        
        # prints message on sender side
        print(f"\x1b8{U_NAME}: {msg}")
        print("\x1b7\x1b[2;0H\x1b[0K❭ ", end = "", flush="True")

async def receive_users():
    """enables multiple people to join 1 host"""
    if U_TYPE != "host":
        return

    loop = asyncio.get_running_loop()

    while True:
        x, y = await loop.run_in_executor(None, my_sock_inst.accept)
        clients.append(x)
        clients[-1].setblocking(False)

async def main():
    if U_TYPE == "host":

        # binds the socket to a 'location' on my computer
        my_sock_inst.bind((U_IP_V4, U_PORT))

        # provides the details for another user to connect with
        print(f"\x1b[1F\x1b[2Kconnection details: {U_IP_V4}-{U_PORT}")
        print("\x1b7== WAITING FOR CONNECTION ==")

        # enables the socket to accept data
        my_sock_inst.listen()

        global client_sock
        global CLIENT_PORT

        # checks for another program to send data to it
        client_sock, CLIENT_PORT = my_sock_inst.accept()
        clients.append(client_sock)

        # gets client name
        clients[-1].sendall(b"$%name")
        name = clients[-1].recv(1024)

        # sets non-blocking AFTER name received
        clients[-1].setblocking(False)
      
        # returns to previous line; clears;
        print(f"\x1b8\x1b[2K{str(name)[2:-1]} joined")

    else:

        # asks if user wants to use port 80 to get around Barker firewall
        u_input = input("\x1b[1F\x1b[2Kenter port: ")
        my_sock_inst.bind((U_IP_V4, int(u_input)))

        SERVER_IP_V4, SERVER_PORT = input("\x1b[1F\x1b[2Kconnection details: ").strip().split("-")
        SERVER_PORT = int(SERVER_PORT)

        my_sock_inst.connect((SERVER_IP_V4, SERVER_PORT))

    print("--------")

    # saves cursor pos; moves to top; clears line; adds '❭' symbol
    print("\x1b7\x1b[2;0H\x1b[2K❭ ", end = "", flush="True")
    await asyncio.gather(check_sent_msg(), send_new_msg(), receive_users())
    
    # closes sockets
    my_sock_inst.close()

    if U_TYPE == "host":
        for client_ in clients:
            client_.close()

asyncio.run(main())