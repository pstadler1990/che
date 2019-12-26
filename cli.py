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
    STORE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'store', 'log.json')

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
        # Overwrite config if existing?
        {
            'type': 'confirm',
            'name': 'overwrite_config',
            'message': 'There\'s already a configuration file - do you want to overwrite it?',
            'when': lambda a: True
        },
        # If previous answer was No, then ask for new config file name
        {
            'type': 'input',
            'name': 'overwrite_config_name',
            'message': 'New config name',
            'default': 'config2.yml',
            'validate': lambda text: os.path.exists(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), text)) is False,
            'when': lambda a: a['overwrite_config'] is False
        },
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
            'default': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates' + os.sep, )
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
        # Overwrite store if existing?
        {
            'type': 'confirm',
            'name': 'overwrite_store',
            'message': 'There\'s already a store file - do you want to overwrite it?',
            'when': lambda a: os.path.exists(a['store_path'])
        },
        # If previous answer was No, then ask for new store file name
        {
            'type': 'input',
            'name': 'overwrite_store_name',
            'message': 'New store name',
            'default': 'log2.json',
            'when': lambda a: a['overwrite_store'] is False
        },
        # Create demo files?
        {
            'type': 'confirm',
            'name': 'create_demo',
            'message': 'Do you want to create some example files (demo project)?'
        }
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

    store_output_path = STORE_PATH
    if not answers['overwrite_store'] and answers['overwrite_store_name']:
        # Change store file because of already existing default
        store_output_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), answers['store_path'], answers['overwrite_store_name'])
        filled_config['log']['file_name'] = answers['overwrite_store_name']

    config_output_path = CONFIG_PATH
    if not answers['overwrite_config'] and answers['overwrite_config_name']:
        # Change output file because of already existing default
        config_output_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), answers['overwrite_config_name'])

    with io.open(config_output_path, 'w+') as config_file:
        yaml.safe_dump(filled_config, config_file)

    with io.open(store_output_path, 'w+') as log_file:
        log_file.write('[{}]')

    # Create demo files if specified
    if answers['create_demo']:
        # TODO: Currently not possible (need to reload log / config first!)
        pass

    print(colored('Your new site has been initialized! You can now run che new page|post to add content.', 'green'))


def cli_new_page(page_name, content='Add your content here'):
    """
    Generates a new page with given name using the defined default types (config.yaml)
    """
    if log.find(page_name):
        print(colored('Page already exists, skipping', 'grey'))
        return

    slugified_page_name = helpers.slugify(page_name)

    file_names = {
        'meta': os.path.join(input_dir, slugified_page_name + os.extsep + default_meta_type),
        'page': os.path.join(input_dir, slugified_page_name + os.extsep + default_page_type),
    }

    print(colored('Creating page', 'green'), colored(slugified_page_name, 'blue'))

    # Meta
    writer_meta = find_writer_for_ext(default_meta_type)()
    boilerplate_meta = {
        'title': page_name,
        'slug': slugified_page_name,
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
    page_converted = writer_page.write("<h1>{name}</h1><p>{content}</p>".format(name=page_name, content=content))
    # Write page_converted to actual file
    with io.open(file_names['page'], 'w') as page_file:
        page_file.write(page_converted)


def cli_activate_page(page, active=True):
    if page['meta']['loaded']:
        page['meta']['loaded']['status'] = 'published' if active else 'draft'
        helpers.write_disk_meta(page['meta']['loaded'])
