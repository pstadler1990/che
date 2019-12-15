import io
import os
import yaml
from termcolor import colored

import helpers
from writer.writers import find_writer_for_ext

config = yaml.safe_load(open('config.yml'))


def cli_new_page(page_name):
    """
    Generates a new page with given name using the defined default types (config.yaml)
    """
    input_dir = os.path.join(config['input']['input_dir'])
    default_meta_type = config['files']['default_meta_type']
    default_page_type = config['files']['default_page_type']

    file_names = {
        'meta': os.path.join(input_dir, page_name + os.extsep + default_meta_type),
        'page': os.path.join(input_dir, page_name + os.extsep + default_page_type),
    }

    print(colored('Creating page', 'green'), colored(page_name, 'blue'))

    # Meta
    writer_meta = find_writer_for_ext(default_meta_type)()
    boilerplate_meta = {
        'title': page_name,
        'slug': helpers.slugify(page_name),
        'template': config['templates']['default_template'],
        'visibility': 'hidden',
        'status': 'draft'
    }

    meta_converted = writer_meta.write(boilerplate_meta)
    # Write meta_converted to actual file
    with io.open(file_names['meta'], 'w') as meta_file:
        meta_file.write(meta_converted)

    # Page
    writer_page = find_writer_for_ext(default_page_type)()
    page_converted = writer_page.write("<h1>{0}</h1><p>Add your content here</p>".format(page_name))
    # Write page_converted to actual file
    with io.open(file_names['page'], 'w') as page_file:
        page_file.write(page_converted)
