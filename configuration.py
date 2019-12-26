import os
import yaml
from termcolor import colored

try:
    config = yaml.safe_load(open('config2.yml'))
    input_dir = os.path.join(config['input']['input_dir'])
    default_meta_type = config['files']['default_meta_type']
    default_page_type = config['files']['default_page_type']
except FileNotFoundError:
    print(colored('Specified configuration file not found. Please change or use', 'red'),
          colored('che init', 'green'),
          colored('to generate a new configuration', 'red'))

# Blank configuration to be copied for generating files
blank_config = {
    'project': {
        'name': ''
    },
    'log': {
        'output_dir': '',
        'file_name': 'log.json'
    },
    'files': {
        'meta_types': [],
        'page_types': [],
        'default_meta_type': '',
        'default_page_type': ''
    },
    'templates': {
        'path': '',
        'build_nav': '',
        'default_template': ''
    },
    'input': {
        'input_dir': ''
    },
    'output': {
        'file_format': 'html',
        'output_dir': '',
        'minify_html': True
    },
    'processing': {
        'use_nltk': False,
        'min_word_length': 2,
        'keyword_extraction': True,
        'summary_generation': True
    },
    'plugins': {
        'path': 'plugins'
    }
}
