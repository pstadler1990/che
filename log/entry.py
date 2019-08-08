from datetime import datetime
from exceptions import LogEntryNotInLogError


class Entry:

    def __init__(self, file):
        if not file:
            # TODO: Error, no file given
            return
        self.file = file
        self.uid = None
        self.version = None
        self.last_modified = None

    def serialize(self):
        """
        Serializes into a JSON-able format
        """
        return {
            'file': self.file,
            'uid': str(self.uid),
            'version': self.version,
            'last_modified': str(self.last_modified)
        }

    def update(self):
        """
        Update an already existing log entry
        """
        if not (self.version and self.last_modified):
            raise LogEntryNotInLogError('Entry may not be in log yet')

        self.version += 1
        self.last_modified = datetime.now()
