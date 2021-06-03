"""Enver is a simple config / environment helper.

Features:
- Automatic validation of environment variables.
- Automatic casting to desired data type using Pydantic.
- Optional default values.
- Fails fast if a variable has no value (either default or override).
- Allows lookup using dot notation, e.g. env.DB_PASSWORD, as well as subscript and the get() method.
"""

from typing import Any

from pydantic import BaseSettings, MissingError, ValidationError
from pydantic.main import ModelMetaclass


class EnverMissingError(Exception):
    """Exception signalling that a required field is missing a value.

    To fix this, either provide a default value in the model, or create an environment
    variable with the same name.
    """


class Singleton(ModelMetaclass):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Enver(BaseSettings, metaclass=Singleton):
    """The main interface to enver.

    Create a subclass of this class with typed attributes, and optionally, default values. If
    environment variables with the same name exists, these will override the defaults values.

    Putting your Enver subclass in a separate config.py file might be a good idea, but not
    mandatory.

    Example:

        >>> from enver import Enver
        ... from typing import Optional, List, Dict
        ...
        ... class Config(Enver):
            ... MY_DB_HOST: str = "127.0.0.1"
            ... MY_DB_USER: str = "user"
            ... MY_DB_PASSWORD: str  # No default value, will be supplied as environment value.
            ... OPTIONAL: Optional[str]
            ... PI: float  # Read from env and converted to float, if possible.
            ... LOCATIONS: List[str] = ["/opt", "/etc"]
            ... MAPPING: Dict[str, float]

        >>> conf = Config()
        >>> conf.MY_DB_HOST
        "127.0.0.1"
        >>> conf.MY_DB_PASSWORD
        "changeit"

    There are three ways to access values, and these are exactly equivalent:
        conf.MY_DB_PASS
        conf['MY_DB_PASS']
        conf.get('MY_DB_PASS')

    This class and any derived classes are singletons, meaning the same instance is always returned.
    So:

        >>> a = Config()
        >>> b = Config()
        >>> a is b
        True

    This means there is no need to pass a single instance between different files.
    """

    def __init__(self):
        try:
            super().__init__()
        except ValidationError as e:
            if isinstance(e.raw_errors[0].exc, MissingError):
                field = e.raw_errors[0].loc_tuple()[0]
                raise EnverMissingError(
                    f"Mandatory field {field} has no default and was not found in the environment"
                ) from e
            else:
                raise

    def all(self):
        """Return dict with all variables."""
        return dict(self)

    def __getitem__(self, item: str) -> Any:
        return self.__getattribute__(item)

    def get(self, var: str) -> Any:
        """Get value of variable from environment or default from config file.

        The variable MUST be listed in the model, either with or without a default value.
        If a variable with the same name exists in the environment, it's value will be returned
        rather than the default value.

        Arguments:
            var: Name of the variable to retrieve.

        """
        return self.__getitem__(var)

    def exists(self, var: str) -> bool:
        """Check whether provided variable exists."""
        return var in self.all()
