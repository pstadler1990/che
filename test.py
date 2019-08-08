import os
from log.entry import Entry
from log.log import Log

if __name__ == '__main__':

    log = Log()

    files = log.load_raw_entries(os.path.join('test'))

    print(files)
