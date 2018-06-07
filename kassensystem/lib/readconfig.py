import configparser
import os.path

config = configparser.ConfigParser()

config.read([
    os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../config/config.ini'),
    '/etc/kassensystem/config.ini',
    '/etc/kassensystem.ini',
])
