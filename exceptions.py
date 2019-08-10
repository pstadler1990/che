class LogNoLoggableEntryError(Exception):
    pass


class LogEntryAlreadyInLogError(Exception):
    pass


class LogNotWriteableError(Exception):
    pass


class LogEntryNotInLogError(Exception):
    pass


class LogEntriesNotADirectoryError(Exception):
    pass


class LoaderWrongFileError(Exception):
    pass


class LoaderNoSuitableLoaderError(Exception):
    pass
