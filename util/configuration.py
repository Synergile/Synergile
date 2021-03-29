import os
from util import ensure_path
from typing import Tuple


class MissingTokenOrPrefix(ValueError):
    pass


class NoConfigError(FileNotFoundError):
    pass


class InvalidPrefixOrToken(ValueError):
    pass


def configuration() -> Tuple[str, str]:
    if os.getcwd() != ensure_path.send_path():
        os.chdir(ensure_path.send_path())
    token = ""
    prefix = ""
    try:
        with open("config.config") as config:
            cfg = config.read()
    except FileNotFoundError as exc:
        raise NoConfigError(exc) from exc
    else:
        sep = cfg.split("\n")
        configs = {}
        try:
            configs[sep[0].split(":")[0].strip(" ")] = sep[0].split(":")[1].strip(" ")
            configs[sep[1].split(":")[0].strip(" ")] = sep[1].split(":")[1].strip(" ")
        except IndexError as exc:
            raise MissingTokenOrPrefix("Couldn't find the token and prefix in the config") from exc
        else:
            try:
                token = configs["token"]
                prefix = configs["prefix"]
                assert token != "" and prefix != ""
            except KeyError as exc:
                raise MissingTokenOrPrefix("Couldn't find the token and prefix in config") from exc
            except AssertionError as exc:
                raise InvalidPrefixOrToken("The prefix or token was invalid, the token and prefix must not be empty/whitespace") from exc
            else:
                return token, prefix
