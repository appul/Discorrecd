import logging

import discord

from discorrecd.events import EventManager

log = logging.getLogger(__name__)

_EVENT_METHODS = [
    ('on_ready', 'ready'),
    ('on_resumed', 'resumed'),
    ('on_message', 'message'),
    ('on_message_delete', 'message_delete'),
    ('on_message_edit', 'message_edit'),
    ('on_typing', 'typing'),
    ('on_channel_create', 'channel_create'),
    ('on_channel_delete', 'channel_delete'),
    ('on_channel_update', 'channel_update'),
    ('on_member_create', 'member_create'),
    ('on_member_delete', 'member_delete'),
    ('on_member_update', 'member_update'),
    ('on_member_ban', 'member_ban'),
    ('on_member_unban', 'member_unban'),
    ('on_group_join', 'group_join'),
    ('on_group_remove', 'group_remove'),
    ('on_server_join', 'server_join'),
    ('on_server_remove', 'server_remove'),
    ('on_server_update', 'server_update'),
    ('on_server_available', 'server_available'),
    ('on_server_unavailable', 'server_unavailable'),
    ('on_server_role_create', 'server_role_create'),
    ('on_server_role_delete', 'server_role_delete'),
    ('on_server_role_update', 'server_role_update'),
    ('on_server_emojis_update', 'server_emojis_update'),
    ('on_voice_state_update', 'voice_state_update'),
    ('on_socket_raw_receive', 'socket_raw_receive'),
    ('on_socket_raw_send', 'socket_raw_send')
]


class CoreClient(discord.Client):
    """A wrapper client for the Discorrecd Core"""

    def __init__(self, event_manager: EventManager, **options):
        """

        :param event_manager: The event manager to events should be registered
        :param options: The options which will passed onto the parent (:class:`discord.Client`) constructor
        """
        super().__init__(**options)
        self._event_manager = event_manager  # type: EventManager
        self._hook_events()

    def _hook_events(self):
        """Populate the event manager by hooking the :class:`discord.Client` event methods."""
        self._hook_error_method()
        for method_name, event in _EVENT_METHODS:
            self._hook_method(method_name, event)

    def _hook_method(self, method_name: str, event: str):
        """Hook a :class:`discord.Client` event method.

        :param method_name: The name of the method to be hooked
        :param event: The name of the event
        """

        async def method(*args, **kwargs):
            await self._event_manager.emit(event, *args, **kwargs)

        method.__name__ = method_name
        if event not in self._event_manager:
            self._event_manager.add(event)
        self.event(method)

    def _hook_error_method(self):
        """Hook the `on_error` method"""

        async def on_error(*args, **kwargs):
            log.error(*args, **kwargs)
            await self._event_manager.emit('client_error', *args, **kwargs)
            await super().on_error(*args, **kwargs)

        if 'client_error' not in self._event_manager:
            self._event_manager.add('client_error')
        self.event(on_error)
