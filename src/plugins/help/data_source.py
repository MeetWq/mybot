import os

dir_path = os.path.split(os.path.realpath(__file__))[0]


def help_file_path():
    return os.path.join(dir_path, 'help.png')
