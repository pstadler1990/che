import hashlib
import io
import os
import re
import unicodedata

from configuration import config
from writer.writers import find_writer_for_ext

input_dir = os.path.join(config['input']['input_dir'])
default_meta_type = config['files']['default_meta_type']
default_page_type = config['files']['default_page_type']


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


def write_disk_meta(meta_dict):
    """
    Write meta_converted to actual file
    """
    outfile_path = os.path.join(input_dir, meta_dict['slug'] + '.{type}'.format(type=default_meta_type))

    writer_meta = find_writer_for_ext(default_meta_type)()
    meta_converted = writer_meta.write(meta_dict)

    with io.open(outfile_path, 'w') as meta_file:
        meta_file.write(meta_converted)
