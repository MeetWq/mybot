import os

dir_path = os.path.split(os.path.realpath(__file__))[0]


def welcome_file_path():
    return os.path.join(dir_path, 'welcome.png')
