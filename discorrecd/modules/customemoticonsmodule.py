import logging
import os
import sys

import discord

from discorrecd.module import Module

log = logging.getLogger(__name__)

_IMG_DIR = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), 'custom-emoticons')
_IMG_EXTENSIONS = ['.jpg', '.png', '.gif']
_EMOTICON_PREFIX = '/'


class CustomEmoticonsModule(Module):
    @Module.Event(['message'])
    async def on_message(self, message: discord.Message):
        if message.author.id == self.client.connection.user.id:
            word, image = self.parse_message(message.content)
            if word and image:
                new_content = message.content.replace(word, '').strip()
                await self.client.delete_message(message)
                await self.client.send_file(message.channel, image, content=new_content)

    def parse_message(self, message: str):
        for word in message.split():
            if word.startswith(_EMOTICON_PREFIX):
                image = self.find_emoticon(word[1:])
                if image is not None:
                    return word, image
        return None, None

    @staticmethod
    def find_emoticon(name):
        for ext in _IMG_EXTENSIONS:
            path = os.path.join(_IMG_DIR, name + ext)
            if os.path.isfile(path):
                return path
        return None
