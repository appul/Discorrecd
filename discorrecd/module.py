import logging

import discord

from discorrecd.events import EventMethod

log = logging.getLogger(__name__)


class Module(object):
    """A base type for Discorrecd modules"""

    def __init__(self, *, client: discord.Client):
        """

        :param client: The Discord Client (:class:`discord.Client`)
        """
        self.client = client  # type: discord.Client

    @staticmethod
    def event(*args, **kwargs) -> EventHandlerMethod:
        """Register a method as handler for events.

        :param args: The positional arguments passed to :class:`EventHandlerMethod`
        :param kwargs: The keyword arguments passed to :class:`EventHandlerMethod`
        """
        return EventHandlerMethod(*args, **kwargs)

    @staticmethod
    def command(*args, **kwargs) -> CommandHandlerMethod:
        """Register a method as handler for commands.

        :param args: The positional arguments passed to :class:`CommandHandlerMethod`
        :param kwargs: The keyword arguments passed to :class:`CommandHandlerMethod`
        """
        return CommandHandlerMethod(*args, **kwargs)


class EventHandlerMethod(EventMethod):
    category = 'events'


class CommandHandlerMethod(EventMethod):
    category = 'commands'
