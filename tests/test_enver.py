import os
from pathlib import Path
from typing import Optional

import pytest

import enver as enver_package
from enver import Enver, EnverMissingError

_here = Path(__file__).parent


class Config(Enver):
    MY_DB_HOST: str = "127.0.0.1"
    MY_DB_USER: str = "user"
    MY_DB_PASS: str
    ANOTHER_SECRET: str = None
    OPTIONAL: Optional[str]
    CAST_TO_FLOAT: float
    BOOL_VALUE: bool = True
    LIST_VALUE: list = [1, 2, 3]
    OVERRIDE_THIS_FLOAT: float = 3.14


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown():
    old_environ = os.environ.copy()
    temp_env_vars = {
        "MY_DB_PASS": "whatever",
        "THIS_OTHER_PASSWORD": "querty",
        "OVERRIDE_THIS_FLOAT": "3.14159265359",
        "CAST_TO_FLOAT": "1.5",
    }
    os.environ.update(temp_env_vars)
    yield
    os.environ.clear()
    os.environ.update(old_environ)


@pytest.fixture()
def missing_env():
    old_environ = os.environ.copy()
    del os.environ["MY_DB_PASS"]
    del os.environ["OVERRIDE_THIS_FLOAT"]
    yield
    os.environ.clear()
    os.environ.update(old_environ)


@pytest.fixture(scope="session")
def env():
    return Config()


def test_singleton():
    a = Config()
    b = Config()
    assert a is b


def test_fields(env):
    keys_ref = {
        "ANOTHER_SECRET",
        "MY_DB_HOST",
        "MY_DB_PASS",
        "MY_DB_USER",
        "BOOL_VALUE",
        "CAST_TO_FLOAT",
        "LIST_VALUE",
        "OPTIONAL",
        "OVERRIDE_THIS_FLOAT",
    }
    assert set(env.dict().keys()) == keys_ref


def test_all(env):
    all_vars = env.all()
    assert all_vars.keys() == env.dict().keys()
    assert all_vars["MY_DB_PASS"] == env.MY_DB_PASS


def test_no_variables():
    class EmptyConfig(Enver):
        pass

    env = EmptyConfig()
    assert env.all() == dict()


def test_init_with_missing_env():
    class DesiredConfig(Enver):
        DOES_NOT_EXIST_IN_ENV: str

    with pytest.raises(EnverMissingError):
        DesiredConfig()


def test_all_accessing_methods(env):
    assert env.MY_DB_USER == env["MY_DB_USER"] == env.get("MY_DB_USER") == "user"


def test_get_var_with_default(env):
    assert env.MY_DB_USER == "user"


def test_get_var_without_default(env):
    assert env.MY_DB_PASS == "whatever"


def test_none_default(env):
    assert env.ANOTHER_SECRET is None


def test_exists(env):
    assert env.exists("MY_DB_HOST")
    assert not env.exists("DOES_NOT_EXIST")


def test_data_type_casting(env):
    assert isinstance(env.CAST_TO_FLOAT, float)


def test_nonexistant_variable(env):
    with pytest.raises(AttributeError):
        env.DOES_NOT_EXIST
    with pytest.raises(AttributeError):
        env["DOES_NOT_EXIST"]
    with pytest.raises(AttributeError):
        env.get("DOES_NOT_EXIST")


def test_existing_environment_variable_not_in_config(env):
    with pytest.raises(AttributeError):
        env.THIS_OTHER_PASSWORD
    with pytest.raises(AttributeError):
        env["THIS_OTHER_PASSWORD"]
    with pytest.raises(AttributeError):
        env.get("THIS_OTHER_PASSWORD")


def test_package_has_docstring():
    assert enver_package.__doc__ is not None


def test_module_has_docstring():
    assert enver_package._enver.__doc__ is not None


def test_all_top_level_public_interfaces_have_docstrings():
    interfaces = [
        getattr(enver_package, attribute_name)
        for attribute_name in dir(enver_package)
        if attribute_name == attribute_name.lstrip("_")
    ]
    for interface in interfaces:
        assert interface.__doc__ is not None, f"{interface} has no docstring."


def test_all_callable_public_interfaces_have_docstrings():
    interfaces = [
        getattr(enver_package, attribute_name)
        for attribute_name in dir(enver_package)
        if attribute_name == attribute_name.lstrip("_")
    ]
    for interface in interfaces:
        subinterfaces = [
            getattr(interface, attribute_name)
            for attribute_name in interface.__dict__  # Not using dir() since we don't want derived
            if attribute_name == attribute_name.lstrip("_")
        ]
        callables = [interface for interface in subinterfaces if callable(interface)]
        for c in callables:
            assert c.__doc__ is not None, f"{c} has no docstring."
