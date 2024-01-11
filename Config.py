import configparser

class Config:
    def __init__(self):
        self.conf = configparser.ConfigParser()
        self.conf.read('config.ini')
        # print(list(self.conf))
        # print([key for key in self.conf['DEFAULT']])

    def write_to_config_file(self):
        with open('config.ini', 'w') as configfile:
            self.conf.write(configfile)

    def ip_address(self):
        if (self.conf.get('DEFAULT', 'ip address', fallback=None)) is None:
            self.conf['DEFAULT']['ip address'] = 'http://192.168.1.11:8080'
            self.write_to_config_file()
        return self.conf.get('DEFAULT', 'ip address')


config = Config()
print(config.ip_address())
