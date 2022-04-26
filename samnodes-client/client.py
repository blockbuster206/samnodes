import sys
import threading
import time

from samnodes.udpclient import *

if not "dev" in sys.argv:
    localIP = "20.212.36.238"
else:
    localIP = "127.0.0.1"
localPort = 20001
server_addr = (localIP, localPort)

startup_msg = " ____                  _   _           _           \n" \
              "/ ___|  __ _ _ __ ___ | \ | | ___   __| | ___  ___ \n" \
              "\___ \ / _` | '_ ` _ \|  \| |/ _ \ / _` |/ _ \/ __|\n" \
              " ___) | (_| | | | | | | |\  | (_) | (_| |  __/\__ \\\n" \
              "|____/ \__,_|_| |_| |_|_| \_|\___/ \__,_|\___||___/\n" \
              "   <sam-nodes Copyright (C) 2022 blockbuster206>   \n"
print(startup_msg)


class Client:
    def __init__(self):
        self.client = UDPClient()

    def connect(self, username=None, password=None):
        if username and password:
            auth = f"{username} {password}"
        else:
            auth = "anonymous"
        self.client.send_data(
            message.create_command_message("user", "authentication", auth).encode("utf-8"), (localIP, localPort))
        msg, addr = self.client.receive_message()
        print(f"Response: {msg}")

    def request_file(self, file_addr):
        self.client.send_data(
            message.create_command_message("request", "file", f"{file_addr}").encode("utf-8"),
            (localIP, localPort))

    def establish_connection_distributor(self, addr):
        global loop
        print("attempting to connect with distributor")
        loop = True

        def receive_confirm_msg():
            msg1, addr1 = self.client.receive_message()
            if not msg1 == "msg_received":
                receive_confirm_msg()
            else:
                print("distributor has received my message")

        def receive_msg():
            global loop
            msg1, addr1 = self.client.receive_message()
            if msg1 == "msg_received":
                print("distributor has received my message")
                msg1, addr1 = distributor.client.receive_message()
                distributor.client.send_message(
                    message.create_command_message("relay", "distributor", "0001 msg_received"), server_addr)
                print(f"Received message from distributor: {msg1}")
            else:
                print(f"Received message from distributor: {msg1}")
                distributor.client.send_message(
                    message.create_command_message("relay", "distributor", "0001 msg_received"), server_addr)
                receive_confirm_msg()
            loop = False

        threading.Thread(target=receive_msg, daemon=True).start()

        while loop:
            distributor.client.send_message("no", addr)
            time.sleep(1)

        print("Successfully connected to distributor")


peers = []

distributor = Client()
distributor.connect()
bound_ip, bound_port = distributor.client.socket.getsockname()
host_ip = socket.gethostbyname(socket.gethostname())
distributor.client.send_message(f"{host_ip} {bound_port}", server_addr)

print("Requesting file from distributor 0001")
distributor.request_file("sams_cat@0001")
msg, addr = distributor.client.receive_message()
target_addr = msg.split()
target_addr = (target_addr[0], int(target_addr[1]))
print("Received distributor public endpoint")

loop = True

distributor.establish_connection_distributor(target_addr)

msg, target_addr = distributor.client.receive_message()
print(f"Distributor sent: {msg}")


# msg, addr = distributor.client.receive_message()
# print(msg)
