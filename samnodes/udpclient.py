import socket


class message:
    @staticmethod
    def create_command_message(command: str, parameter: str, arguments: str):
        return "command\n"\
               f"{command}\n" \
               f"{parameter}\n" \
               f"{arguments}"

    @staticmethod
    def convert_command_message(structured_msg: bytes):
        structured_msg = structured_msg.decode("utf-8").splitlines()
        try:
            return {"command": structured_msg[1],
                    "parameter": structured_msg[2],
                    "arguments": " ".join(structured_msg[3:])}
        except IndexError:
            print(f'message "{" ".join(structured_msg)}" was not structured properly.')
            return None

    @staticmethod
    def create_file_message(part_number, data: bytes):
        return "file_part\n" \
               f"{part_number}\n".encode("utf-8") \
               + data


class UDPClient:
    def __init__(self):
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def receive_data(self):
        return self.socket.recvfrom(513000)

    def send_data(self, data: bytes, address: tuple):
        self.socket.sendto(data, address)

    def send_message(self, msg: str, addr):
        self.send_data(msg.encode("utf-8"), addr)

    def receive_message(self):
        msg, addr = self.receive_data()
        msg = msg.decode("utf-8")
        return msg, addr
