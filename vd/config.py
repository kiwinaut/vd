import argparse
import os
from vip_tools.saver import SAVE_PATH
from vdbs.vip_2_0 import __version__ as dbv

HOME = os.environ['HOME']
DIRPATH = os.path.dirname(os.path.realpath(__file__))

class ConfigManager(object):
    "Config manager"

    def __init__(self):
        self.defaults = {
            'database.path': f'{HOME}/.cache/vip{dbv}.db',
            # 'database.path': f'{HOME}/.cache/vip.db',
            'server.port': 8000,
            'worker_count': 4,
            'save_location': SAVE_PATH + '/incomplete',
            'complete_path': SAVE_PATH,
            'sha':'1953125930f206197496109b7fc1e94899c552fe1'
        }
        self.config = {}
        self.options = {}
        # self.arguments = []

    def parse(self):
        parser = argparse.ArgumentParser(description='vip server', prog='vip')
        parser.add_argument('--test', action="store_true", help="Use Test Files")
        parser.add_argument('-d', '--db', type=str, help="Select local db")
        parser.add_argument('-s', '--saveloc', type=str, help="Select save loc")
        parser.add_argument('-f', '--filter', type=str, help="*filter*")

        args = parser.parse_args()
        self.options['dev'] = args.test
        if args.test:
            self.options['database.path'] = ':memory:'
        if args.db:
            self.options['database.path'] = args.db
        if args.saveloc:
            if not os.path.isdir(args.saveloc):
                os.mkdir(args.saveloc)
            self.options['save_location'] = args.saveloc
        if args.filter:
            self.options['filter'] = args.filter



    def __setitem__(self, key, value, config=True):
        self.options[key] = value
        if config:
            self.config[key] = value

    def __getitem__(self, key):
        return self.options.get(key, self.config.get(key,
            self.defaults.get(key)))


CONFIG = ConfigManager()
