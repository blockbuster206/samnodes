from samnodes.udpclient import Client, message
from authentication import Authentication


class commands:
    @staticmethod
    def parse_command(msg: dict, addr):
        if msg["command"] in command_table.keys():
            command_table[msg["command"]](msg["parameter"], msg["arguments"], addr)
        else:
            print("command doesnt exist")

    @staticmethod
    def distributor(parameter, arguments, addr):
        if parameter == "authentication":
            distributor_token = arguments
            valid = Authentication().validate_distributor_token(distributor_token)
            if valid[0]:
                client.send_data(f"validated {valid[1]}".encode("utf-8"), addr)
                print(f"validated id {valid[1]}")
                distributors[valid[1]] = addr
            else:
                client.send_data("failed none".encode("utf-8"), addr)

    @staticmethod
    def user(parameter, arguments, addr):
        if parameter == "authentication":
            if arguments == "anonymous":
                client.send_message("anonymous_authorised", addr)
                return
            arguments = arguments.split()
            authentication.validate_user_credentials(arguments[0], arguments[1])
            client.send_message("user_authorised", addr)

    @staticmethod
    def remove(parameter, arguments, addr):
        if parameter == "distributor":
            arguments = arguments.split()
            valid = Authentication().validate_distributor_token(arguments[1])
            if valid[0]:
                if arguments[0] in distributors.keys():
                    print(f"removed distributor {arguments[0]} from online distributors")
                    distributors.pop(arguments[0])
                    client.send_data("Removed you from online distributors".encode("utf-8"), addr)
                else:
                    print("Not connected to sam-nodes")

    @staticmethod
    def request(parameter, arguments, addr):
        if parameter == "file":
            arguments = arguments.split("@")
            if arguments[1] in distributors:
                distributor_addr = distributors.get(arguments[1])
                client.send_message(message.create_command_message("request", "file", f"{arguments[0]}"),
                                    distributor_addr)
                msg, distributor_addr = client.receive_message()
                distributors[arguments[1]] = distributor_addr
                addr = f"{addr[0]} {addr[1]}"
                client.send_message(addr, distributor_addr)


command_table = {
    "distributor": commands.distributor,
    "user": commands.user,
    "remove": commands.remove,
    "request": commands.request
}


def parse_message(msg: bytes, addr: tuple):
    msg_type = msg.splitlines()[0].decode("utf-8")
    if msg_type == "command":
        msg = message.convert_command_message(msg)
        commands.parse_command(msg, addr)


localIP = "127.0.0.1"
localPort = 20001

authentication = Authentication()
client = Client()

client.socket.bind((localIP, localPort))

users = {}

distributors = {}

while True:
    msg, address = client.receive_data()
    parse_message(msg, address)
