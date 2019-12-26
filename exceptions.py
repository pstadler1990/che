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


class BuildNoBuildFilesError(Exception):
    pass


class WriterNoSuitableWriterError(Exception):
    pass


class ConfigNotFoundError(Exception):
    pass
