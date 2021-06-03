# enver

Enver is a simple config / environment helper.

[![Test And Lint](https://github.com/danhje/enver/actions/workflows/python-test.yml/badge.svg)](https://github.com/danhje/enver/actions/workflows/python-test.yml)
[![codecov](https://codecov.io/gh/danhje/enver/branch/master/graph/badge.svg)](https://codecov.io/gh/danhje/enver)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/danhje/enver?include_prereleases)
![PyPI](https://img.shields.io/pypi/v/enver)

Collect all your config values and environment values in a single location, so new contributors knows what variables must be
  set, and don't have to go searching for `os.environ` or `os.getenv` scattered throughout the code.

Features:
- Automatic validation of environment variables.
- Automatic casting to desired data type using Pydantic.
- Optional default values.
- Fails fast if a variable has no value (either default or override).
- Allows lookup using dot notation, e.g. `env.DB_PASSWORD`, as well as subscript (`env['DB_PASSWORD']`) or the `get()` method `env.get('DB_PASSWORD')`.

## Installation

```
pip install enver
```

## Usage

Create a class that inherits from Enver, with config variables as class attributes. Putting this class in a separate config.py file might be a good idea, but not necessary.


```python
# config.py

from enver import Enver
from typing import Optional, List, Dict

class Config(Enver):
    MY_DB_HOST: str = "127.0.0.1"
    MY_DB_USER: str = "user"
    MY_DB_PASSWORD: str  # No default value, will be supplied as environment value.
    THIS_VAL_MIGHT_NOT_EXIST_IN_ENV: Optional[str]
    PI: float  # Read from env and converted to float, if possible.
    ENABLE_LOGGING: bool = True
    LOCATIONS: List[str] = ["/opt", "/etc"]
    MAPPING: Dict[str, float]
```

If environment values with the same name as any of the attributes exist, those will be used, overriding any defaults. Values will be converted to the specified type. If conversion is not possible, an exception is thrown.

Here's how to use the values:

```python
# service.py

from .config import Config

env = Config()

user = env.MY_DB_USER
password = env.MY_DB_PASSWORD

if env.exists('FEATURE_1'):
  feature_1()

all_values = env.all()
```

The `Enver` class and any derived classes are singletons, meaning it they always return the same instance:

```python
env1 = Config()
env2 = Config()
assert env1 is env2
```

Which means this is fine:

````python
user = Config().MY_DB_USER
password = Config().MY_DB_PASSWORD
````

## Development

Dependencies for the project are managed with poetry.
To install all dependencies run:

```shell
poetry install
```

To install pre-commit and set up its git hooks:
```
pip install pre-commit
pre-commit install
```
Now pre-commit will run automatically on every commit.
