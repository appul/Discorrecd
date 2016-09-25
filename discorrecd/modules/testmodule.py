import logging

import discord

from discorrecd.module import Module

log = logging.getLogger(__name__)


class TestModule(Module):
    @Module.event(['message'])
    async def on_message(self, message: discord.Message):
        if message.author.id == self.client.connection.user.id:
            msg = ('Me @', message.channel.name, ':', message.content)
            log.info(' '.join(map(str, msg)))

            if message.content == '.testme':
                await self.client.send_message(message.channel, 'Test: success!')
