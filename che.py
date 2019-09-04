import os
import time
import yaml
import argparse
from log.log import Log
from termcolor import colored
from builder.build import Builder
from plugin import PluginHandler
from hooks import add_subscriber, HOOK_BEFORE_LOAD, HOOK_AFTER_LOAD

config = yaml.safe_load(open('config.yml'))

argparser = argparse.ArgumentParser()
argparser.add_argument('--force_rebuild', help='Force rebuild of all files, despite of any changes', action='store_true')

installed_plugins = []

if __name__ == '__main__':
    # Read command line options
    args = argparser.parse_args()

    build_time_start = time.time()

    plugin_handler = PluginHandler(config['plugins']['path'])
    plugin_handler.install_plugins()

    log = Log()

    add_subscriber(plugin_handler, HOOK_BEFORE_LOAD, HOOK_AFTER_LOAD)

    files, ok = log.load_raw_entries(os.path.join('test'))
    # TODO: path to the files should be a command line argument with default in config

    # this would return false for ok if any file is not a pair (= missing either a meta or a page file)
    print('File integrity: ', colored('OK ', 'green') if ok else colored('Error!', 'red'))

    if not ok:
        print(colored('BUILD ERROR', 'red'), 'Build time: {0}'.format(time.time() - build_time_start))
        exit()

    changed_files, needs_rebuild_from_files = log.convert_raw_entries(files)

    # Force rebuild either by files or by command line option --force-rebuild
    needs_rebuild = args.force_rebuild or needs_rebuild_from_files

    builder = Builder(changed_files if not needs_rebuild else files)
    builder.prepare()
    builder.process_text_auto()

    if config['templates']['build_nav'] and needs_rebuild:
        builder.build_nav(files, use_absolute_links=False)

    # Render html to Jinja template
    builder.build(minify_html=config['output']['minify_html'])

    # Update log file after the successful build
    log.write()

    print(colored('BUILD SUCCESSFUL', 'green', 'on_grey'), ' -> Build time: {0}'.format(time.time() - build_time_start))
