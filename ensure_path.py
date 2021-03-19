import os


def send_path():
    file_path = __file__
    split_file_path = file_path.split(os.path.sep)
    to_pop_in_path = len(split_file_path) - 1
    split_file_path.pop(to_pop_in_path)
    psep = os.path.sep
    finish_path = psep.join(split_file_path)
    return finish_path
