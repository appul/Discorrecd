import logging

from discorrecd.config import Config, ConfigProperty
from discorrecd.core import Core
from discorrecd.simplelogger import SimpleLogger

log = logging.getLogger(__name__)


class Discorrecd(object):
    def __init__(self):
        self.core = None  # type: Core
        self.config = None  # type: DiscorrecdConfig

    def initialize(self, config_name: str = 'config.json'):
        """Initialize Discorrecd

        :param config_name: The name of the config file, default: 'config.json'
        """
        self._setup_logging()

        self.core = Core()

        config_path = Config.get_path(config_name)
        self.config = DiscorrecdConfig()
        self.config.load(config_path)

    def start(self):
        """Start Discorrecd"""
        self.core.start(token=self.config.token, username=self.config.username, password=self.config.password)

    @staticmethod
    def _setup_logging():
        """Setup logging"""
        SimpleLogger('', logging.DEBUG)
        SimpleLogger('', logging.DEBUG, 'debug')
        SimpleLogger('', logging.INFO, 'info')
        logging.getLogger('').setLevel(logging.DEBUG)
        logging.getLogger('discord').setLevel(logging.WARNING)
        logging.getLogger('websockets').setLevel(logging.WARNING)


class DiscorrecdConfig(Config):
    token = ConfigProperty('token')  # type: str
    username = ConfigProperty('username')  # type: str
    password = ConfigProperty('password')  # type: str
