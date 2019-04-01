import requests


class TokenGenerator:
    def __init__(self):
        self.__client_id = "cAIW85iqxxmuH7LG5iaAsISOJyqMZiDx1PAyWdqBVlamRig2dn"
        self.__client_secret = "PGtSQGV7hNSGMKqNeCnN9R6Cf9ccDaf6Ob69GB4U"
        self.__file_name = "token.txt"

    def __get_new_token(self):
        reply = requests.post("https://api.petfinder.com/v2/oauth2/token",
                              data={"grant_type": "client_credentials",
                                    "client_id": self.__client_id,
                                    "client_secret": self.__client_secret})
        token_map = reply.json()
        return token_map["access_token"]

    def __read_token(self):
        token_file = open(self.__file_name, "r")
        token = token_file.readline()
        token_file.close()
        return token

    def __write_token(self):
        token_file = open(self.__file_name, "w")
        token = self.__get_new_token()
        token_file.write(token)
        token_file.close()

    def __test_get_request(self):
        url = "https://api.petfinder.com/v2/animals"
        token = self.__read_token()
        bearer_token = "Bearer " + token
        header = {"Authorization": bearer_token}
        raw_data = requests.get(url, headers=header)
        if raw_data.status_code == 401:
            return False
        return True

    def get_token(self):
        if self.__test_get_request():
            return self.__read_token()
        else:
            self.__write_token()
            return self.get_token()
