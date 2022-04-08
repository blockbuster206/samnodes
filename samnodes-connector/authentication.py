import os
import json


class Authentication:
    def __init__(self):
        if os.path.isfile("samnodes.auth"):
            with open("samnodes.auth", "r") as auth:
                self.auth = json.load(auth)
                auth.close()
                return

        self.auth = {
            "distributor_tokens": {},
            "user_credentials ": {}
        }

    def validate_distributor_token(self, distributor_token):
        if distributor_token in self.auth["distributor_tokens"].keys():
            return True, self.auth["distributor_tokens"].get(distributor_token)
        else:
            return False, None

    def validate_user_credentials(self, username, password):
        return True

