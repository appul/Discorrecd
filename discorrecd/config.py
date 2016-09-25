import json
import logging
import os
import sys
from typing import Any, Type
from typing import Dict

log = logging.getLogger(__name__)

ConfigData = Dict[str, Any]


class Config(object):
    """An abstract base type for configs"""
    default_dir = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), 'config')

    def __init__(self):
        self._config = {}  # type: ConfigData

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value of a setting from the config

        :param key: The key of the config setting
        :param default: The default value if the key doesn't exist
        :return: The value of the setting
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Set the value of a config setting

        :param key: The key of the config setting
        :param value: The new value of the setting
        """
        self._config[key] = value

    def update(self, config: ConfigData):
        """Updates the config with new data

        :param config: The new config data
        """
        self._config.update(config)

    def load(self, path: str, surpress: bool = False):
        with open(path) as data:
            try:
                config = json.load(data)
                self.update(config)
            except json.decoder.JSONDecodeError:
                if not surpress:
                    raise

    @classmethod
    def get_path(cls, name: str) -> str:
        """Get the filepath for a config in the default config directory

        This merely generates a filepath and does not validate existence of the file.

        :param name: The name of the config file
        :return: The path to the config file
        """
        return os.path.join(cls.default_dir, name)


class ConfigProperty(object):
    """A simple property-like type for :class:`Config` subclasses

    A simple property-like type with a predefined getter, and optionally
    a setter. These are not customizable; for that use regular properties.
    :class:`ConfigProperty` objects are basically properties that return
    specified settings from the :class:`Config` with defined defaults.
    """

    def __init__(self, key: str, default: Any = None, setter: bool = False):
        """

        :param key: The key of the setting in the :class:`Config`
        :param default: The default value of the setting
        :param setter: Whether the setter should be enabled, default: False
        """
        self.key = key  # type: str
        self.default = default  # type: Any
        self.setter = setter  # type: bool

    def __get__(self, instance: Config, owner: Type[Config]) -> Any:
        return instance.get(self.key, self.default)

    def __set__(self, instance: Config, value: Any):
        if not self.setter:
            raise ConfigPropertySetError('Cannot change the value of this setting')


class ConfigPropertySetError(Exception):
    """Raised an attempt is made to set the value of a :class:`ConfigProperty`
    that has its setter disabled."""
