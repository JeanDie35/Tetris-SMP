import socket
import threading
from queue import Queue
from tools import decode, encode

# handles the connection with the server
class Client:

    def __init__(self, config, key=" "):
        # create a socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = config.data["server_ip"]  # replace with the server's IP address
        self.server_port = config.data["port"]  # replace with the server's port number
        self.key = key
        self.in_game = False

        # we will use a Queue because with the get method it will wait until the server responds
        self.responses = Queue()
    def connect(self) -> str | None:
        """""
        return the client's key
        """""

        try:
            print(self.socket)
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

                # when the user is connected, we wait for the server to start
                start_thread = threading.Thread(target=self.get_response)
                start_thread.start()

                return self.key

        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_response(self):
        while True:
            print("Waiting ...")
            # waits for the server to start
            response = decode(self.socket.recv(1024))
            print(f"Received : {response}")

            if response == "start":
                # will tell the game to start
                self.in_game = True

            elif response == "closed":
                self.close_conn()
                break

            else:
                self.responses.put(response)

    def send_request(self, request):
        # sending messages
        self.socket.send(encode(request))

    def get_color(self):
        self.send_request("next")
        return self.responses.get()

    def close_conn(self):
        # close client socket (connection to the server)
        self.socket.close()
        print("Connection to server closed")
