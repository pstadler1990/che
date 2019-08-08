import io
import os
import json
import uuid
import yaml
from datetime import datetime
from termcolor import colored
from helpers import file_get_extension
from exceptions import *
from loader.loaders import find_meta_loader_for_ext

config = yaml.safe_load(open('config.yml'))


def file_is_meta(ext):
    return ext in config['files']['meta_types']


def file_is_page(ext):
    return ext in config['files']['page_types']


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

    @staticmethod
    def load_raw_entries(path):
        """
        Load a given directory containing meta (json) and page data (md)
        Returns a list of all found entries
        """
        if not os.path.isdir(path):
            raise LogEntriesNotADirectoryError('Given path is not a directory')

        found_files = {
            'meta': [],
            'pages': []
        }

        print(colored('Finding meta and page files in...', 'yellow'), path)
        for file in os.listdir(path):
            absolute_file_path = os.path.join(path, file)

            if os.path.isfile(absolute_file_path):

                # Finding meta and page files
                ext = file_get_extension(absolute_file_path, strip_dot=True)

                if file_is_meta(ext):
                    print('[meta]', colored(file, 'magenta'))

                    # Check available loaders
                    loader = find_meta_loader_for_ext(ext)()
                    if not loader:
                        raise LoaderNoSuitableLoaderError('No suitable loader found for this type')

                    found_files['meta'].append(loader.read(absolute_file_path))

                elif file_is_page(ext):
                    print('[page]', colored(file, 'blue'))

                    # TODO: Load page contents into dict

                else:
                    # Skipping unrelated files
                    pass

        return found_files

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
                json.dump([e.serialize() for e in self.entries], self.log_file, ensure_ascii=False)

        except ValueError:
            raise LogNotWriteableError('Log is not writable')
        finally:
            if close:
                self.close()

    def close(self):
        """
        Close the log file
        """
        self.log_file.close()
