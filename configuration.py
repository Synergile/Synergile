import os
import ensure_path
def configuration():
    if os.getcwd() != ensure_path.send_path():
        os.chdir(ensure_path.send_path())
    cfgInDir = False
    foundPrefix = False
    for i in os.listdir():
        if i == "config.config":
            cfgInDir = True
            with open('config.config', 'r') as config:
                for line in config:
                    splitline = line.split(':')
                    if splitline[0].lower() == "prefix":
                        prefix = splitline[1]
                        foundPrefix = True
                        break
                        
    if not cfgInDir:
        raise LookupError("Couldn't find config.config")
    if not foundPrefix:
        print("Couldn't find a prefix")
        raise LookupError("Tried to find 'prefix' in config.config, failed to do so")
    with open('config.config', 'r') as f:
        foundToken = False
        for i in f:
            splitted = i.split(':')
            if splitted[0].lower() == "token":
                token = splitted[1]
                foundToken = True
                break
        if foundToken and foundPrefix:
            return token, prefix
        else:
            raise LookupError("Couldn't find the token, can't start the bot LOL")
