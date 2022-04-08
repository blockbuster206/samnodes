from samnodes.udpclient import *

localIP = "127.0.0.1"
localPort = 20001


class Distributor:
    def __init__(self):
        self.client = Client()

    def connect(self, username=None, password=None):
        if username and password: auth = f"{username} {password}"
        else: auth = "anonymous"
        self.client.send_data(
            message.create_command_message("user", "authentication", auth).encode("utf-8"), (localIP, localPort))
        msg, addr = self.client.receive_message()
        print(msg)

    def request_file(self, file_addr):
        self.client.send_data(
            message.create_command_message("request", "file", f"{file_addr}").encode("utf-8"),
            (localIP, localPort))


distributor = Distributor()
distributor.connect()
distributor.request_file("sams_cat@0001")
msg, addr = distributor.client.receive_message()
print(msg)