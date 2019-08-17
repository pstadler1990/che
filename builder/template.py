import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

config = yaml.safe_load(open('config.yml'))


env = Environment(
    loader=FileSystemLoader(config['templates']['path']),
    autoescape=select_autoescape(['html', 'xml'])
)


def _load_template(template):
    return env.get_template(template)


def render_template(template, var_dict):
    """
    Returns the rendered html output for given template (path/file) and a passed page dict
    """
    return _load_template(template).render(page=var_dict)
