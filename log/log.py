import io
import os
import json
import uuid
import yaml
from log.entry import Entry
from datetime import datetime
from termcolor import colored
from helpers import file_get_extension, contents_get_hash_md5
from exceptions import *

config = yaml.safe_load(open('config.yml'))


def file_is_meta(ext):
    return ext in config['files']['meta_types']


def file_is_page(ext):
    return ext in config['files']['page_types']


class Log:

    def __init__(self):
        self.log_file_path = os.path.join(config['log']['output_dir'], config['log']['file_name'])

        if not os.path.exists(config['log']['output_dir']):
            os.makedirs(config['log']['output_dir'])

        with io.open(self.log_file_path, 'r', encoding='utf-8') as log_file:
            try:
                self.entries = []
                tmp_entries = json.load(log_file)
                for t in tmp_entries:
                    entry = Entry(filename=None, field_initializer=t)
                    self.entries.append(entry)
            except json.decoder.JSONDecodeError:
                self.entries = []

    def load_raw_entries(self, path):
        """
        Load a given directory containing meta (json) and page data (md)
        Returns a list of all found entries
        """
        if not os.path.isdir(path):
            raise LogEntriesNotADirectoryError('Given path is not a directory')

        changed_files = []

        print(colored('Finding meta and page files in...', 'yellow'), path)
        for file in os.listdir(path):
            absolute_file_path = os.path.join(path, file)

            if os.path.isfile(absolute_file_path):

                # Finding meta and page files
                ext, fn = file_get_extension(file, strip_dot=True)

                # Read raw contents
                with io.open(absolute_file_path, 'rb') as raw_file:
                    raw_contents = raw_file.read()

                f_hash = contents_get_hash_md5(raw_contents)

                f_entry = self.find(name=fn)

                if not f_entry:
                    # File is not in log yet, insert
                    if file_is_meta(ext):
                        print(colored('Found new meta file', 'green'), '[meta]', colored(file, 'magenta'))

                        entry = Entry(fn)
                        entry.hash = f_hash
                        self.insert(entry)

                    elif file_is_page(ext):
                        print('[page]', colored(file, 'blue'))

                        # TODO: Load page contents into dict
                    else:
                        # Skipping unrelated files
                        pass
                else:
                    # File is in log already, compare hashes to find any changes
                    if f_hash == f_entry.hash:
                        # Skipping file as there are no changes
                        print(colored('Skipping file due to no changes', 'magenta'), file)
                        continue
                    else:
                        # There are changes so update the entry and add the file to the change list
                        # f_entry.update()
                        # TODO: Once the page content is loaded and hashed, uncomment the entry.update() call
                        # to eventually update the entry
                        changed_files.append(fn)

        return changed_files

    def insert(self, entry, write_meta=True):
        """
        Insert a new loggable object to the log
        For every new entry a UUID is generated
        """
        if not entry.file:
            raise LogNoLoggableEntryError('Given entry is a non-loggable object')

        if [e for e in self.entries if e.file == entry.file]:
            raise LogEntryAlreadyInLogError('Given entry is already in the log')

        entry.last_modified = datetime.now()
        if not entry.version:
            entry.version = 1

        entry.uid = uuid.uuid4()
        self.entries.append(entry)

        if write_meta:
            # TODO: Write newly created meta information to the meta file
            pass

    def find(self, name, uid=None):
        """
        Returns the entry for given uid
        """
        return next(filter(lambda e: e.uid == uid, self.entries), None) if uid else next(filter(lambda e: e.file == name, self.entries), None)

    def write(self):
        """
        Write all entries (created, existing or modified) to the log file
        """
        with io.open(self.log_file_path, 'w', encoding='utf-8') as log_file:
            try:
                if log_file.writable():
                    json.dump([e.serialize() for e in self.entries], log_file, ensure_ascii=False)

            except ValueError:
                raise LogNotWriteableError('Log is not writable')