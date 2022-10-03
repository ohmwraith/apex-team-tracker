import json
import os


class Config:
    def __init__(self, path='config.json'):
        self.content = {
            "API_KEY": "",
            "VICTIMS": []
        }
        if not self.is_file_exists():
            self.create_config()
            print("Внесите данные в config.json и запустите приложение повторно")
            exit(0)
        else:
            self.load_from_file(path)
            self.check_content()

    def load_from_file(self, path='config.json'):
        with open(path) as file:
            config = file.read()
            try:
                config_json = json.loads(config)
            except Exception as E:
                print("Ошибка чтения конфига: " + E)
                exit(-1)
            self.content['API_KEY'] = config_json['API_KEY']
            self.content['VICTIMS'] = config_json['VICTIMS']
            return config_json


    def get_victims(self):
        return self.content['VICTIMS']

    def get_key(self):
        return self.content['API_KEY']

    def get_content(self):
        return self.content

    def is_file_exists(self):
        if 'config.json' not in os.listdir():
            return False
        return True

    def set_account_pointer(self, pointer):
        self.account_pointer = pointer

    def get_account_pointer(self):
        return self.account_pointer

    def check_content(self):
        if self.content['API_KEY'] == "":
            print("API_KEY: Необходимо указать ключ для использования api.mozambiquehe.re")
            exit(0)
        if len(self.content['VICTIMS']) == 0:
            print("VICTIMS: Укажите только ники в Origin. Пример ['ohmwraith', 'chaoticbutpc']")

    def create_config(self):
        with open('config.json', 'w') as file:
            file.write(json.dumps(self.content))


if __name__ == "__main__":
    conf = Config()
    print(conf.load_config())
