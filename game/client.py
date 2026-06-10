import socket
import threading
from tools import decode, encode, recv_nb_bytes

# handles the connection with the server
class Client:

    def __init__(self, config, key=" "):
        self.config = config

        # create a socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = self.config.data["server_ip"]  # replace with the server's IP address
        self.server_port = self.config.data["port"]  # replace with the server's port number
        self.key = key
        self.game_started = False

        # dict to store the server's responses depending on the name of the response
        self.responses = {}

    def connect(self) -> str | None:
        """""
        return the client's key
        """""

        try:
            # establish connection with server
            self.socket.connect((self.server_ip, self.server_port))
            # client sends its key to check if it's valid
            self.socket.send(encode(self.key))

            response = decode(self.socket.recv(1024))
            if response == 'Client already connected':
                raise Exception("Client already connected")

            elif response == 'Game is already started':
                raise Exception("Game is already started")

            else:
                self.key = response
                print(f"Your key to connect to the server is {self.key}")

                # when the user is connected, we start a thread that will listen for incoming responses and store
                # them is self.responses
                start_thread = threading.Thread(target=self.get_response)
                start_thread.start()

                return self.key

        # when the server isn't online
        except OSError:
            print("Connection failed, the server is shutdown")

        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_response(self):
        while True:

            # getting the size of the request which is stored in 4 bytes in front of the request itself
            response_size = recv_nb_bytes(self.socket, self.config.data["header_size"])
            # transforming bytes to int
            response_size = int.from_bytes(response_size, byteorder="big")

            # receive the message, knowing the size allow us to make sure the request doesn't mix with other
            response = decode(recv_nb_bytes(self.socket, response_size))

            # store the response's arguments in self.responses
            self.responses[response["name"]] = response["args"]

            print(f"Received : {response}")

            if response["name"] == "GAME_STARTED":
                # will tell the game to start
                self.game_started = True

            elif response["name"] == "CLOSED":
                self.close_conn()
                break


    def send_request(self, request: dict):

        print(f"Sent : {request}")

        # delete the old value so we can know when the new value has arrived
        # only works for GET request because the others don't expect a response
        if request["name"] in self.responses and request["type"] == 'GET':
            self.responses[request["name"]] = None


        data = encode(request)
        # transform the size in four bytes
        size = len(data).to_bytes(self.config.data["header_size"], byteorder="big")

        # sending messages with the size of the data in front
        self.socket.sendall(size + data)

    def get_color(self):
        # sends a request for the next block
        self.send_request({"type": "GET", "name": "NEXT_BLOCK", "args": None})
        # waits for the server to answer
        while not "NEXT_BLOCK" in self.responses or self.responses["NEXT_BLOCK"] is None :
            pass
        return self.responses["NEXT_BLOCK"]

    def get_nb_players(self):
        # sends a request for the next block
        self.send_request({"type": "GET", "name": "NB_PLAYERS", "args": None})
        # waits for the server to answer
        while not "NB_PLAYERS" in self.responses or self.responses["NB_PLAYERS"] is None:
            pass
        return self.responses["NB_PLAYERS"]

    def close_conn(self):
        # close client socket (connection to the server)
        self.socket.close()
        print("Connection to server closed")
