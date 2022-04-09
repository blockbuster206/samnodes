import sys
from samnodes.udpclient import *

if not "dev" in sys.argv:
    localIP = "20.212.36.238"
else:
    localIP = "127.0.0.1"
localPort = 20001
server_addr = (localIP, localPort)


class Distributor:
    def __init__(self):
        self.client = Client()

    def connect(self, username=None, password=None):
        if username and password:
            auth = f"{username} {password}"
        else:
            auth = "anonymous"
        self.client.send_data(
            message.create_command_message("user", "authentication", auth).encode("utf-8"), (localIP, localPort))
        msg, addr = self.client.receive_message()
        print(msg)

    def request_file(self, file_addr):
        self.client.send_data(
            message.create_command_message("request", "file", f"{file_addr}").encode("utf-8"),
            (localIP, localPort))


peers = []

distributor = Distributor()
distributor.connect()
bound_ip, bound_port = distributor.client.socket.getsockname()
host_ip = socket.gethostbyname(socket.gethostname())
distributor.client.send_message(f"{host_ip} {bound_port}", server_addr)

distributor.request_file("sams_cat@0001")
msg, addr = distributor.client.receive_message()
target_addr = msg.split()
target_addr = (target_addr[0], int(target_addr[1]))
print(target_addr)

distributor.client.send_message("test", target_addr)
msg, addr1 = distributor.client.receive_message()
print(msg)

# msg, addr = distributor.client.receive_message()
# print(msg)
