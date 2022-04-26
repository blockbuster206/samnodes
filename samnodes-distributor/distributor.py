import socket
import threading
import time

from samnodes.udpclient import UDPClient, message
import logging
import sys

if not "dev" in sys.argv:
    localIP = "20.212.36.238"
else:
    localIP = "127.0.0.1"
localPort = 20001
server_addr = (localIP, localPort)

# logging setup
root = logging.getLogger("samnodes-distributor")
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

startup_msg = " ____                  _   _           _           \n" \
              "/ ___|  __ _ _ __ ___ | \ | | ___   __| | ___  ___ \n" \
              "\___ \ / _` | '_ ` _ \|  \| |/ _ \ / _` |/ _ \/ __|\n" \
              " ___) | (_| | | | | | | |\  | (_) | (_| |  __/\__ \\\n" \
              "|____/ \__,_|_| |_| |_|_| \_|\___/ \__,_|\___||___/\n" \
              "   <sam-nodes Copyright (C) 2022 blockbuster206>   \n"
print(startup_msg)


class Distributor:
    def __init__(self):
        self.client = UDPClient()
        self.id = None

    def connect(self, distributor_token):
        self.client.send_data(
            message.create_command_message("distributor", "authentication",
                                           distributor_token).encode("utf-8"), (localIP, localPort))
        msg, address = self.client.receive_message()
        msg = msg.split()

        if msg[0]:
            root.info("distributor_token validated")
            self.id = msg[1]
            root.info(f"distributor id is {self.id}")
            root.info("sending private endpoint to server")
            bound_ip, bound_port = self.client.socket.getsockname()
            host_ip = socket.gethostbyname(socket.gethostname())
            self.client.send_message(f"{host_ip} {bound_port}", server_addr)
            root.info("sent private endpoint")
            return True
        else:
            root.error("distributor_token failed validation, please try connecting again")
            return False

    def request_file(self, fileid, distributorid):
        self.client.send_data(
            message.create_command_message("request", "file", f"{fileid}@{distributorid}").encode("utf-8"),
            (localIP, localPort))
        msg, addr = self.client.receive_message()

    def send_file(self, fileid, addr):
        file_chunks = []
        offset = 0
        print("splitting file into chunks")
        while True:
            with open("cache/sam_cats.mp3", "rb") as file:
                file.seek(offset)
                data = file.read(512000)
                if not data:
                    break
                file_chunks.append(data)
                offset += 512000
                print(offset)
        print("split file into chunks")
        print("sending hello message to target")
        self.client.send_message("hello", addr)
        print("message sent UDP HOLPUNCHING BLLODYU WORKKEJS")

    def establish_connection_client(self, addr):
        global loop
        root.info("attempting to connect to client")
        loop = True

        def receive_confirm_msg():
            msg1, addr1 = self.client.receive_message()
            if not msg1 == "msg_received":
                receive_confirm_msg()
            else:
                root.info("client has received my message")

        def receive_msg():
            global loop
            msg1, addr1 = self.client.receive_message()
            if msg1 == "msg_received":
                root.info("client has received message")
                msg1, addr1 = distributor.client.receive_message()
                root.info(f"message received from the client: {msg1}")
                distributor.client.send_message(
                    message.create_command_message("relay", "user", "anon msg_received"), server_addr)
            else:
                root.info(f"message received from the client: {msg1}")
                distributor.client.send_message(
                    message.create_command_message("relay", "user", "anon msg_received"), server_addr)
                receive_confirm_msg()
            loop = False

        threading.Thread(target=receive_msg, daemon=True).start()

        while loop:
            distributor.client.send_message("among us", addr)
            time.sleep(1)  # Try to send the udp hole punching packets every 1 second

        root.info("connected successfully with client")



def connect():
    global _token
    # _token = input("token: ")
    if not distributor.connect(_token):
        connect()


distributor = Distributor()

# print("Welcome to sam-nodes distributor.\n"
#       "In order to use sam-nodes distributor you need a distributor token so that\n"
#       "users can see you when they need the files that you want to distribute.\n\n")
#
# print("Do you have a distributor token?\n")
# choice = input("y/n: ")
# if not choice == "y":
#     print("Get one at sam.net/distributor/token")
#     exit()

_token = "hello"
connect()

msg, addr = distributor.client.receive_message()

msg = message.convert_command_message(msg.encode("utf-8"))
if msg["command"] == "request":
    arguments = msg["arguments"]
    distributor.client.send_message("available", (localIP, localPort))

msg, addr = distributor.client.receive_message()

target_addr = msg.split()
target_addr = (target_addr[0], int(target_addr[1]))
root.info(f"received the client's public endpoint: {target_addr}")

loop = True

distributor.establish_connection_client(target_addr)

distributor.client.send_message("Hi shiter", target_addr)

# send message to each other

# distributor.send_file("sams_cats", target_addr)

# print("Sending remove command")
# distributor.client.send_message(
#     message.create_command_message("remove",
#                                    "distributor",
#                                    f"{distributor.id} {_token}"),
#     (localIP, localPort))
#
# print(f"Server: {distributor.client.receive_message()[0]}")
