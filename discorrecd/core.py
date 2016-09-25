import logging
from typing import List, Type

from discorrecd.coreclient import CoreClient
from discorrecd.events import EventManager
from discorrecd.module import Module

log = logging.getLogger(__name__)


class Core(object):
    """The Discorrecd Core that handles core functionalities such as events"""

    def __init__(self):
        self.events = EventManager()  # type: EventManager
        self.client = CoreClient(self.events)  # type: CoreClient
        self._modules = []  # type: List[Module]

    def start(self, *, username: str = None, password: str = None, token: str = None):
        """Login and start the core

        Either the token, or the

        :param username: The user's username
        :param password: The user's password
        :param token: The bot's token
        """
        if token:
            self.client.run(token)
        elif username and password:
            self.client.run(username, password)
        else:
            raise ValueError('Did not receive valid credentials to log into Discord')

    def add(self, module: Type[Module], *args, **kwargs) -> Module:
        """

        :param module: The module that should be added
        :param args: The arguments that will be passed on to the module constructor
        :param kwargs: The keyword arguments that will be passed to the module constructor
        """
        if any(instance.__class__ is module for instance in self._modules):
            raise LookupError('Module {0} has already been added'.format(module.__name__))

        log.info('Adding module to Discorrecd core: {0}'.format(module.__name__))

        instance = module(*args, **kwargs, client=self.client)
        Module.Event.register_methods(self.events, instance)
        self._modules.append(instance)
        return instance
