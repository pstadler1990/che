import os
import yaml

config = yaml.safe_load(open('config.yml'))

input_dir = os.path.join(config['input']['input_dir'])
default_meta_type = config['files']['default_meta_type']
default_page_type = config['files']['default_page_type']