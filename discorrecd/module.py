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

    class Event(EventMethod):
        pass
