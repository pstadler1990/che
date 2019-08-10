import os
from termcolor import colored
from log.log import Log
from builder.build import Builder

if __name__ == '__main__':

    log = Log()

    files, ok = log.load_raw_entries(os.path.join('test'))
    # TODO: path to the files should be a command line argument with default in config

    # this would return false for ok if any file is not a pair (= missing either a meta or a page file)
    print('File integrity: ', colored('OK ', 'green') if ok else colored('Error!', 'red'))

    print(files)

    log.convert_raw_entries(files)

    builder = Builder(files)
    builder.prepare()

    log.write()
