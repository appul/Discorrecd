import logging
import os
import sys
from typing import Tuple

import discord

from discorrecd.module import Module

log = logging.getLogger(__name__)

_IMG_DIR = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), 'custom-emoticons')
_IMG_EXTENSIONS = ['.jpg', '.png', '.gif']
_EMOTICON_PREFIX = '/'


class CustomEmoticonsModule(Module):
    """Automatically replaces messages with custom images if emoticon names are found in the text.

    Images are searched for in the ``/custom-emoticons`` directory relative to the directory
    of the `__main__` file. If a word replaceable with an emoticon is found, the message is
    deleted and replaced with a new message that includes the emoticon image.
    """

    @Module.Event(['message'])
    async def on_message(self, message: discord.Message):
        """Event handler for new messages"""
        if message.author.id == self.client.connection.user.id:
            word, image = self.parse_message(message.content)
            if word and image:
                new_content = message.content.replace(word, '').strip()
                await self.client.delete_message(message)
                await self.client.send_file(message.channel, image, content=new_content)

    def parse_message(self, message: str) -> Tuple[str, str]:
        """Parse the content of a message and finds the replaceable word-image combination

        :param message: The content of a message
        :returns: The word and the path to the image.
        """
        for word in message.split():
            if word.startswith(_EMOTICON_PREFIX):
                image = self.find_emoticon(word[1:])
                if image is not None:
                    return word, image
        return None, None

    @staticmethod
    def find_emoticon(name: str) -> str:
        """Find an image in the emoticon directory based on a name

        :param name: The name of the image
        :return: The path to the image, None if no image was found
        """
        for ext in _IMG_EXTENSIONS:
            path = os.path.join(_IMG_DIR, name + ext)
            if os.path.isfile(path):
                return path
        return None
