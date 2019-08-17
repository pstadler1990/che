import os
import time
from termcolor import colored
from log.log import Log
from builder.build import Builder

if __name__ == '__main__':

    build_time_start = time.time()

    log = Log()

    files, ok = log.load_raw_entries(os.path.join('test'))
    # TODO: path to the files should be a command line argument with default in config

    # this would return false for ok if any file is not a pair (= missing either a meta or a page file)
    print('File integrity: ', colored('OK ', 'green') if ok else colored('Error!', 'red'))

    changed_files, needs_rebuild = log.convert_raw_entries(files)

    builder = Builder(changed_files if not needs_rebuild else files)
    builder.prepare()
    builder.process_text_auto()

    if changed_files:
        builder.build_nav(files, use_absolute_links=False)

    # Render html to Jinja template
    builder.build()

    # Update log file after the successful build
    log.write()

    print(colored('BUILD SUCCESSFUL', 'green'), 'Build time: {0}'.format(time.time() - build_time_start))


