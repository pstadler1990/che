import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape, BaseLoader

config = yaml.safe_load(open('config.yml'))

additional_templates = []
env = None


def get_env():
    global env
    if env is None:
        env = Environment(
            loader=FileSystemLoader(list([config['templates']['path']] + additional_templates)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    return env


def add_template_path(path):
    additional_templates.append(path)


def _load_template(template):
    return get_env().get_template(template)


def _load_template_from_string(template_str):
    return Environment(loader=BaseLoader()).from_string(template_str)


def render_template(template, **kwargs):
    """
    Returns the rendered html output for given template (path/file) and a passed page dict
    """
    if 'page' not in kwargs:
        kwargs['page'] = None
    if 'title' not in kwargs:
        kwargs['nav'] = []
    return _load_template(template).render(kwargs)


def render_template_from_string(template_str, **kwargs):
    return _load_template_from_string(template_str).render(kwargs)
