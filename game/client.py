import socket
import threading
from tools import decode, encode

# handles the connection with the server
class Client:

    def __init__(self, config, key=" "):
        # create a socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = config.data["server_ip"]  # replace with the server's IP address
        self.server_port = config.data["port"]  # replace with the server's port number
        self.key = key
        self.game_started = False

        # we will use a Queue because with the get method it will wait until the server responds
        self.response = None
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

                # when the user is connected, we wait for the server to start
                start_thread = threading.Thread(target=self.get_response)
                start_thread.start()

                return self.key

        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_response(self):
        while True:
            self.response = None
            # waits for the server to start
            self.response = decode(self.socket.recv(1024)).upper()
            print(f"Received : {self.response}")

            if self.response == "START":
                # will tell the game to start
                self.game_started = True

            elif self.response == "CLOSED":
                self.close_conn()
                break


    def send_request(self, request):
        # sending messages
        self.socket.send(encode(request))

    def get_color(self):
        self.send_request("NEXT_BLOCK")
        print("Waiting for the color ...")
        # waiting for the server to answer
        while self.response is None:
            pass
        return self.response

    def close_conn(self):
        # close client socket (connection to the server)
        self.socket.close()
        print("Connection to server closed")
