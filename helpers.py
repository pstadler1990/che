import os


def file_get_extension(file, strip_dot=False):
    _, ext = os.path.splitext(file)
    return ext if not strip_dot else ext.replace('.', '')

