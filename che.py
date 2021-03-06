import argparse
import os
import time
from termcolor import colored
import cli
from builder.build import Builder
from exceptions import ConfigNotFoundError

try:
    from configuration import config
    config_found = True
except ImportError:
    config_found = False
from hooks import add_subscriber, HOOK_BEFORE_LOAD, HOOK_AFTER_LOAD
from log import log
from plugin import PluginHandler

# Create all supported command line options and commands
argparser = argparse.ArgumentParser()
subparser = argparser.add_subparsers(dest='command')
argparser.add_argument('--force_rebuild', help='Force rebuild of all files, despite of any changes', action='store_true')
parser_new = subparser.add_parser('new')
parser_init = subparser.add_parser('init')
parser_activate = subparser.add_parser('activate')
parser_deactivate = subparser.add_parser('deactivate')
parser_new.add_argument('page', nargs='+', help='Generate a new page with the specified name')
parser_activate.add_argument('page', nargs='+', help='Activate specified page')
parser_deactivate.add_argument('page', nargs='+', help='Deactivate specified page')

installed_plugins = []


if __name__ == '__main__':
    # Read command line options
    args = argparser.parse_args()
    build_time_start = time.time()

    # Activate plugins and emit hooks
    try:
        plugin_handler = PluginHandler(config['plugins']['path'])
        plugin_handler.install_plugins()

        add_subscriber(plugin_handler, HOOK_BEFORE_LOAD, HOOK_AFTER_LOAD)

        # Preload the files
        files, ok = log.load_raw_entries(os.path.join(config['input']['input_dir']))
        if not ok:
            # print(colored('BUILD ERROR', 'red'), 'Build time: {0}'.format(time.time() - build_time_start))
            # exit()
            pass
    except NameError:
        # No config found, allow only a few base commands like init
        if not args.command or args.command != 'init':
            raise ConfigNotFoundError('No config given. Please use che init to create a new website')

    # CLI: Create file(s) or structures
    if args.command == 'init':
        cli.cli_init()
        exit()
    elif args.command == 'new':
        if args.page:
            try:
                cli.cli_new_page(args.page[1])
            except IndexError:
                print(colored('Failed to generate new page, please provide name!', 'red'))
        exit()
    elif args.command in ['activate', 'deactivate']:
        if args.page:
            try:
                entry = files[args.page[0]]
                active = args.command == 'activate'
                cli.cli_activate_page(entry, active)
                print(colored('Page status of "{page}" has changed.'.format(page=args.page[0]), 'grey'))
            except KeyError:
                print(colored('Could not activate / find page', 'red'), args.page[0])
        exit()

    changed_files, needs_rebuild_from_files = log.convert_raw_entries(files)

    # this would return false for ok if any file is not a pair (= missing either a meta or a page file)
    print('File integrity: ', colored('OK ', 'green') if ok else colored('Error!', 'red'))

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
