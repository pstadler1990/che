import io
import os
import json
import uuid
import yaml
from datetime import datetime
from exceptions import LogNoLoggableEntryError, LogEntryAlreadyInLogError

config = yaml.safe_load(open('config.yml'))


class Log:

    def __init__(self):
        path = os.path.join(config['log']['output_dir'], config['log']['file_name'])

        if not os.path.exists(config['log']['output_dir']):
            os.makedirs(config['log']['output_dir'])

        self.log_file = io.open(path, 'r+', encoding='utf-8')
        try:
            self.entries = json.load(self.log_file)
        except json.decoder.JSONDecodeError:
            self.entries = []

    def insert(self, entry, auto_meta=True):
        """
        Insert a new loggable object to the log
        For every new entry a UUID is generated
        """
        if not entry.file:
            raise LogNoLoggableEntryError('Given entry is a non-loggable object')

        if entry in self.entries or (e for e in self.entries if e.file == entry.file):
            raise LogEntryAlreadyInLogError('Given entry is already in the log')

        if auto_meta:
            entry.last_modified = datetime.now()
            if not entry.version:
                entry.version = 1
            else:
                entry.version += 1

        entry.uid = uuid.uuid4()
        self.entries.append(entry)

    def find(self, uid):
        """
        Returns the entry for given uid
        """
        return filter(lambda e: e.uid == uid, self.entries)

    def write(self, close=True):
        """
        Write all entries (created, existing or modified) to the log file
        """
        try:
            if self.log_file.writable():
                try:
                    json.dump([e.serialize() for e in self.entries], self.log_file, ensure_ascii=False)
                except TypeError:
                    # TODO: error
                    pass
        except ValueError:
            # TODO: Error
            pass
        finally:
            if close:
                self.close()

    def close(self):
        self.log_file.close()
