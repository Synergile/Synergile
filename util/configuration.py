import os
from util import ensure_path
from typing import Tuple


class MissingTokenOrPrefix(ValueError):
    pass


class NoConfigError(FileNotFoundError):
    pass


def configuration() -> Tuple[str, str]:
    if os.getcwd() != ensure_path.send_path():
        os.chdir(ensure_path.send_path())
    token = ""
    prefix = ""
    try:
        with open("../config.config") as config:
            cfg = config.read()
    except FileNotFoundError as exc:
        raise NoConfigError(exc) from exc
    else:
        sep = cfg.split("\n")
        configs = {}
        try:
            configs[sep[0].split(":")[0]] = sep[0].split(":")[1]
            configs[sep[1].split(":")[0]] = sep[1].split(":")[1]
        except IndexError as exc:
            raise MissingTokenOrPrefix("Couldn't find the token and prefix in the config") from exc
        else:
            try:
                token = configs["token"]
                prefix = configs["prefix"]
            except KeyError as exc:
                raise MissingTokenOrPrefix("Couldn't find the token and prefix in config") from exc
            else:
                return token, prefix
