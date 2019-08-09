from base64 import encodebytes
from datetime import datetime
from exceptions import LogEntryNotInLogError


class Entry:

    def __init__(self, filename, field_initializer=None):
        if field_initializer:
            self.file = field_initializer['file']
            self.uid = field_initializer['uid']
            self.version = field_initializer['version']
            self.last_modified = field_initializer['last_modified']
            self.hash = field_initializer['hash']
        else:
            self.file = filename
            self.uid = None
            self.version = None
            self.last_modified = None
            self.hash = None

    def serialize(self):
        """
        Serializes into a JSON-able format
        """
        return {
            'file': self.file,
            'uid': str(self.uid),
            'version': self.version,
            'last_modified': str(self.last_modified),
            'hash': self.hash
        }

    def update(self):
        """
        Update an already existing log entry
        """
        # TODO: Modify update method as its pretty useless atm!
        if not (self.version and self.last_modified):
            raise LogEntryNotInLogError('Entry may not be in log yet')

        self.version += 1
        self.last_modified = datetime.now()
