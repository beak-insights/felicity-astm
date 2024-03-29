import os
import sys
import distutils.dir_util


def is_linux():
    return sys.platform == 'linux' or sys.platform.startswith('linux') or os.name == 'posix'


def is_windows():
    return sys.platform == 'win32' or sys.platform.startswith('win') or os.name == 'nt'


def create_dir(file_path):
    distutils.dir_util.mkpath(str(file_path))


def register_file(file_path):
    if not file_path.is_file():
        with open(file_path, "w") as f:
            f.write("")
        f.close()


def file_setup(log_file_path, log_file):
    if log_file_path.is_dir():
        register_file(log_file)
    else:
        create_dir(log_file_path)
        register_file(log_file)


def has_special_char(order_id):
    special_chars = list("~`!@#$%^&*()+=[]{}\\|;:'\",.<>/?")
    for char in order_id:
        if char in special_chars and char != "-":
            return True
    return False
