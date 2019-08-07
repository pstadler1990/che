import uuid
from datetime import datetime


class Log:

    def __init__(self):
        self.entries = []
        pass

    def insert(self, entry, auto_meta=True):
        """
        Insert a new loggable object to the log
        For every new entry a UUID is generated
        """
        if not entry.file:
            # TODO: log error: this is not a loggable entry
            return

        if entry in self.entries or (e for e in self.entries if e.file == entry.file):
            # TODO: log error: entry already in log, use update()-method
            return

        if auto_meta:
            entry.last_modified = datetime.now()
            if not entry.version:
                entry.version = 1
            entry.version += 1

        entry.uid = uuid.uuid4()
        self.entries.append(entry)

    def find(self, uid):
        """
        Returns the entry for given uid
        """
        return filter(lambda e: e.uid == uid, self.entries)