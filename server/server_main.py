import socket
import threading
import random
import secrets
from builtins import print

from config import Config
from tools import decode, encode, recv_nb_bytes

config = Config()


class Server:

    # dict to handle all the clients
    clients = {}

    def __init__(self):
        self.server_ip = self.get_ip_address()  # server hostname or IP address
        self.port = config.data["port"]  # server port number
        # list of random numbers to send to the clients to know what is the next block
        self.blocks = [self.get_random_number()]

        self.in_game = False
        self.nb_players = 0


    def get_ip_address(self) -> str:
        return socket.gethostbyname(socket.gethostname())

    def get_nb_players(self) -> int:
        return len([client for client in self.clients if self.clients[client]["in_game"]])

    def send_response(self, key, response: dict):

        print(f"Sent : {response}")

        data = encode(response)
        # transform the reseponse size in four bytes
        size = len(data).to_bytes(config.data["header_size"], byteorder="big")

        print(key)

        # sending messages with the size of the data in front
        self.clients[key]["socket"].sendall(size + data)

    def generate_key(self) -> str:
        # generates a key
        key = secrets.token_hex(3)
        # checks if the key isn't already used for a client
        while key in self.clients:
            key = secrets.token_hex(3)

        return key

    def close_conn_with(self, client_key: str):
        self.end_game(client_key)

        print(f"Closing connection with client : {client_key}")
        self.send_response(client_key, {"name": "CLOSED", "args": None})

    def start_game(self):
        if not self.in_game:
            for client in self.clients:
                # checks if the client is online
                if self.clients[client]["online"]:
                    self.send_response(client, {"name": "GAME_STARTED", "args": None})
                    self.clients[client]["in_game"] = True

        self.nb_players = self.get_nb_players()
        self.in_game = True

    def end_game(self, key: str):
        self.clients[key]["in_game"] = False

        # checks if a client is still playing
        for client in self.clients:
            if self.clients[client]["in_game"]:
                self.in_game = True
                break

            else:
                self.in_game = False


    def get_key(self, client_socket: socket.socket) -> str | None:
        # receives the key that the client sent
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
                    # creates a new key
                    client_key = self.generate_key()
                    self.clients[client_key] = {"online": True, "socket": client_socket, "in_game": False, "block": 0}

            else:
                raise Exception("Game is already started")

        # handles exceptions
        except Exception as e:
            client_socket.send(encode(e.args[0]))
            return None

        else:
            client_socket.send(encode(client_key))
            print(f"Accepted connection from client with key {client_key}")
            return client_key


    def handle_client(self, client_socket, addr):
        key = self.get_key(client_socket)

        # if the key is valid
        if key is not None:
            try:
                while True:
                    # getting the size of the request which is stored in 4 bytes in front of the request itself
                    request_size = recv_nb_bytes(self.clients[key]["socket"], config.data["header_size"])
                    # transforming bytes to int
                    request_size = int.from_bytes(request_size, byteorder="big")

                    # receive the message, knowing the size allow us to make sure the request doesn't mix with other
                    request = decode(recv_nb_bytes(self.clients[key]["socket"], request_size))
                    print(f"Received from {key}: {request}")

                    # when the user sends a request to change a state
                    if request["type"] == "EVENT":

                        if request["name"] == "CLOSE":
                            self.close_conn_with(key)
                            break

                        elif request["name"] == "START":
                            self.start_game()

                        elif request["name"] == "OVER":
                            self.end_game(key)

                    # if the user wants to transfer data to the other players
                    elif request["type"] == "TRANSFER":
                            self.send_data(key, request["name"], request["args"])

                    # when the user sends a request and waits for a value
                    elif request["type"] == "GET":

                        if request["name"] == "NEXT_BLOCK":
                            self.next_block(key)

                        elif request["name"] == "NB_PLAYERS":
                            self.send_response(key, {"name": "NB_PLAYERS", "args": self.nb_players})


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
        block = self.blocks[self.clients[key]["block"]]
        self.send_response(key, {"name": "NEXT_BLOCK", "args": block})

    def send_data(self, key, data_name, data):

        # get the opponent's key
        # the opponent must be in game
        opponent = [client for client in self.clients if client != key and self.clients[client]["in_game"]]

        if opponent != []:
            self.send_response(opponent[0], {"name": data_name.upper(), "args": data})




server = Server()
server.run()