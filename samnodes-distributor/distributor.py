import socket

from samnodes.udpclient import Client, message
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

print("<sam-nodes Copyright (C) 2022 blockbuster206>")


class Distributor:
    def __init__(self):
        self.client = Client()
        self.id = None

    def connect_distributor(self, distributor_token):
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


def connect():
    global _token
    # _token = input("token: ")
    if not distributor.connect_distributor(_token):
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
print(target_addr)

distributor.client.send_message("test", target_addr)
msg, addr1 = distributor.client.receive_message()
print(msg)

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
