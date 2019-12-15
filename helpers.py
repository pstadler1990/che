import io
import os
import hashlib
import re
import unicodedata


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


# Taken from https://github.com/django/django/blob/master/django/utils/text.py
def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)
