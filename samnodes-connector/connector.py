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
            valid = authentication.validate_distributor_token(distributor_token)
            validated = valid[0]
            distributor_id = valid[1]
            if validated:
                client.send_data(f"validated {valid[1]}".encode("utf-8"), addr)
                print(f"validated id {valid[1]}")
                print("getting private and public for distributor")
                msg, addr = client.receive_message()
                private_ip, private_port = msg.split()
                private_addr = (private_ip, private_port)
                print(f"Private endpoint: {private_addr}\n"
                      f"Public endpoint: {addr}")
                distributors[distributor_id] = {"public": addr, "private": private_addr}
            else:
                client.send_data("failed none".encode("utf-8"), addr)

    @staticmethod
    def user(parameter, arguments, addr):
        if parameter == "authentication":
            if arguments == "anonymous":
                client.send_message("anonymous_authorised", addr)
            else:
                arguments = arguments.split()
                authentication.validate_user_credentials(arguments[0], arguments[1])
                client.send_message("user_authorised", addr)

            print("getting private and public endpoints for user")
            msg, addr = client.receive_message()
            private_ip, private_port = msg.split()
            private_addr = (private_ip, private_port)
            print(f"Private endpoint: {private_addr}\n"
                  f"Public endpoint: {addr}")
            users["anon"] = {"public": addr, "private": private_addr}

    @staticmethod
    def remove(parameter, arguments, addr):
        if parameter == "distributor":
            arguments = arguments.split()
            valid = authentication.validate_distributor_token(arguments[1])
            validated = valid[0]
            distributor_id = valid[1]
            if validated:
                if distributor_id in distributors.keys():
                    print(f"removed distributor {distributor_id} from online distributors")
                    distributors.pop(distributor_id)
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
                                    distributor_addr.get("public"))
                msg, distributor_addr = client.receive_message()
                client_text_addr = f"{addr[0]} {addr[1]}"
                distributor_text_addr = f"{distributor_addr[0]} {distributor_addr[1]}"
                client.send_message(client_text_addr, distributor_addr)
                client.send_message(distributor_text_addr, addr)


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


localIP = ""
localPort = 20001

authentication = Authentication()
client = Client()

client.socket.bind((localIP, localPort))

users = {}

distributors = {}

while True:
    print(distributors, users)
    msg, address = client.receive_data()
    parse_message(msg, address)
