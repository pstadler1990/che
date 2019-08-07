from log.entry import Entry
from log.log import Log

if __name__ == '__main__':

    log = Log()

    test_entry1 = Entry('about_us')

    log.insert(test_entry1)

    log.write()
