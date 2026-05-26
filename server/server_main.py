import socket
import threading
import random
import secrets
from config import Config
from tools import decode, encode

config = Config()


class Server:

    clients = {}

    def __init__(self):
        self.server_ip = self.get_ip_address()  # server hostname or IP address
        self.port = config.data["port"]  # server port number
        self.blocks = [self.get_random_number()]
        self.in_game = False


    def get_ip_address(self) -> str:
        return socket.gethostbyname(socket.gethostname())

    def generate_key(self) -> str:
        key = secrets.token_hex(3)
        # checks if the key isn't already used for a client
        while key in self.clients:
            key = secrets.token_hex(3)

        return key

    def close_conn_with(self, client_key: str):
        print(f"Closing connection with client : {client_key}")
        self.clients[client_key]["socket"].send(encode("closed"))

    def start_game(self):
        for client in self.clients:
            # checks if the client is online and not already playing
            if self.clients[client]["online"]:
                self.clients[client]["socket"].send(encode("start"))
                self.clients[client]["in_game"] = True
        self.in_game = True

    def end_game(self, client_key: str):
        self.clients[client_key]["in_game"] = False
        self.close_conn_with(client_key)

        for client in self.clients:
            if self.clients[client]["in_game"]:
                self.in_game = True
                break

            else:
                self.in_game = False

    def get_key(self, client_socket: socket.socket) -> str | None:
        client_key = decode(client_socket.recv(1024))
        try:
            # if the game is already launched, we don't accept any connections
            if not self.in_game:

                if client_key in self.clients:
                    # checks if the client is already connected
                    if self.clients[client_key]["online"]:
                        raise Exception("Client already connected")

                    else:
                        self.clients[client_key]["online"] = True

                else:
                    client_key = self.generate_key()
                    self.clients[client_key] = {"online": True, "socket": client_socket, "in_game": False, "block": 0}

            else:
                raise Exception("Game is already started")

        except Exception as e:
            client_socket.send(encode(e.args))
            return None

        else:
            client_socket.send(encode(client_key))
            print(f"Accepted connection from client with key {client_key}")
            return client_key


    def handle_client(self, client_socket, addr):
        key = self.get_key(client_socket)

        if key is not None:
            try:
                while True:
                    # receive and print client messages
                    request = decode(client_socket.recv(1024))

                    if request == "close":
                        self.close_conn_with(key)

                    elif request == "start":
                        self.start_game()

                    elif request == "next":
                        self.next_block(key)

                    elif request == "over":
                        self.end_game(key)

                    else:
                        response = "accepted"

                        client_socket.send(encode(response))

                    print(f"Received: {request}")


            except Exception as e:
                print(f"Error when handling client: {e}")
            finally:
                self.clients[key]["online"] = False
                client_socket.close()
                print(f"Connection to client ({addr[0]}:{addr[1]}) closed")


    def run(self):
        # create a socket object
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # bind the socket to the host and port
            server.bind((self.server_ip, self.port))
            # listen for incoming connections
            server.listen()
            print(f"Listening on {self.server_ip}:{self.port}")

            while True:
                # accept a client connection
                client_socket, addr = server.accept()
                print(f"Incoming connection from {addr[0]}:{addr[1]}")

                # start a new thread to handle the client
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr,))
                thread.start()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            server.close()

    ################################
    # Handles all the game mechanics
    ################################

    def get_random_number(self):
        return random.randint(config.data["first_fixed_block"], config.data["last_fixed_block"])

    def next_block(self, key):
        self.clients[key]["block"] += 1
        # creates a new number
        if len(self.blocks) == self.clients[key]["block"]:
            self.blocks.append(self.get_random_number())

        # sends the new number to the client
        self.clients[key]["socket"].send(encode(self.blocks[self.clients[key]["block"]]))


server = Server()
server.run()