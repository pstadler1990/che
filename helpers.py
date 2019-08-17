import io
import os
import hashlib
import errno


def file_get_extension(file, strip_dot=False):
    """
    Returns extension (w/ or w/o dot, specified by strip_dot)
    and the filename without the extension as tuple
    """
    filename, ext = os.path.splitext(file)
    return (ext, filename) if not strip_dot else (ext.replace('.', ''), filename)


def file_get_hash_md5(file, block_size=2**16):
    md5 = hashlib.md5()
    with io.open(file, 'r', encoding='utf-8') as file:
        while True:
            d_chunk = file.read(block_size)
            if not d_chunk:
                break
            md5.update(d_chunk)
    return md5.digest()


def contents_get_hash_md5(contents):
    md5 = hashlib.md5()
    md5.update(contents)
    return md5.hexdigest()


def safe_create_dir(file):
    dir_name = os.path.dirname(file)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
