import io
from copy import deepcopy

from PyInquirer import prompt
from termcolor import colored
import helpers
from configuration import *
from loader import loaders
from log import log
from writer import writers
from writer.writers import find_writer_for_ext


def cli_init():
    """
    Initializes a brand new website or blog project
    by generating all required files, such as the log and the config
    """
    CONFIG_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config_test.yml')

    available_meta = []
    available_page = []

    # Convert available loaders
    meta_loaders = [k['ext'] for k in filter(lambda e: e['type'] == 'meta', loaders.available_loaders)]
    page_loaders = [k['ext'] for k in filter(lambda e: e['type'] == 'page', loaders.available_loaders)]
    meta_writers = [k['ext'] for k in filter(lambda e: e['type'] == 'meta', writers.available_writers)]
    page_writers = [k['ext'] for k in filter(lambda e: e['type'] == 'page', writers.available_writers)]

    # Intersect loaders and writers
    che_meta = list(set(meta_loaders) & set(meta_writers))
    che_page = list(set(page_loaders) & set(page_writers))

    for meta in che_meta:
        available_meta.append({'name': meta})

    for page in che_page:
        available_page.append({'name': page})

    questions = [
        # Project name
        {
            'type': 'input',
            'name': 'project_name',
            'message': 'Project name (the name of the final website and / or blog)',
            'validate': lambda text: len(text) > 0
        },
        # File types for pages / meta (list, checkbox) ? Based on available readers / writers
        {
            'type': 'checkbox',
            'name': 'supported_meta',
            'message': 'Select wanted file type support for META data',
            'choices': available_meta
        },
        {
            'type': 'checkbox',
            'name': 'supported_page',
            'message': 'Select wanted file type support for PAGE data',
            'choices': available_page
        },
        # Template path
        {
            'type': 'input',
            'name': 'template_path',
            'message': 'Template path',
            'validate': lambda text: os.path.isabs(text),
            'default': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates' + os.sep,)
        },
        # default template
        {
            'type': 'input',
            'name': 'default_template',
            'message': 'Default template (i.e. default.html)',
            'validate': lambda text: len(text) > 0 and str(text).find('.') > 0,
            'default': 'default.html'
        },
        # Use page navigation
        {
            'type': 'confirm',
            'name': 'build_navigation',
            'message': 'Build navigation from files?',
        },
        # Input dir for raw files (page and meta)
        {
            'type': 'input',
            'name': 'input_path',
            'message': 'Path for input files (meta and page files)',
            'validate': lambda text: os.path.isabs(text),
            'default': os.path.join(os.path.dirname(os.path.realpath(__file__)) + os.sep)
        },
        # Output dir
        {
            'type': 'input',
            'name': 'output_path',
            'message': 'Path for output of generated html files',
            'validate': lambda text: os.path.isabs(text),
            'default': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dist' + os.sep)
        },
        # Plugin path
        {
            'type': 'input',
            'name': 'plugin_path',
            'message': 'Path for plugins',
            'validate': lambda text: os.path.isabs(text),
            'default': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'plugins' + os.sep)
        },
        # Store path
        {
            'type': 'input',
            'name': 'store_path',
            'message': 'Path for the local store database (store)',
            'validate': lambda text: os.path.isabs(text),
            'default': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'store' + os.sep)
        },
    ]
    answers = prompt(questions)

    # Copy the answers into a new configuration file
    filled_config = deepcopy(blank_config)
    filled_config['project']['name'] = answers['project_name']
    filled_config['files']['meta_types'] = answers['supported_meta']
    filled_config['files']['page_types'] = answers['supported_page']
    filled_config['files']['default_meta_type'] = answers['supported_meta'][0]
    filled_config['files']['default_page_type'] = answers['supported_page'][0]
    filled_config['templates']['path'] = answers['template_path']
    filled_config['templates']['default_template'] = answers['default_template']
    filled_config['templates']['build_nav'] = answers['build_navigation']
    filled_config['input']['input_dir'] = answers['input_path']
    filled_config['output']['output_dir'] = answers['output_path']
    filled_config['plugins']['path'] = answers['plugin_path']
    filled_config['log']['output_dir'] = answers['store_path']

    with io.open(CONFIG_PATH, 'w+') as config_file:
        yaml.safe_dump(filled_config, config_file)


def cli_new_page(page_name):
    """
    Generates a new page with given name using the defined default types (config.yaml)
    """
    if log.find(page_name):
        print(colored('Page already exists, skipping', 'grey'))
        return

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


def cli_activate_page(page, active=True):
    if page['meta']['loaded']:
        page['meta']['loaded']['status'] = 'published' if active else 'draft'
        helpers.write_disk_meta(page['meta']['loaded'])
