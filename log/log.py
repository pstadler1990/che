import io
import os
import json
import uuid
import yaml
from hooks import emit_hook, HOOK_BEFORE_LOAD, HOOK_AFTER_LOAD
from log.entry import Entry
from datetime import datetime
from termcolor import colored
from helpers import file_get_extension, contents_get_hash_md5, safe_create_dir
from loader.loaders import find_meta_loader_for_ext
from exceptions import *

config = yaml.safe_load(open('config.yml'))


def _file_is_meta(ext):
    return ext in config['files']['meta_types']


def _file_is_page(ext):
    return ext in config['files']['page_types']


class Log:
    """
    Log class for keeping files sync
    Every new supported file (meta and page) is appended to the log.
    We only store some meta information and the file's (md5) hash for file integrity checks
    """
    def __init__(self):
        self.log_file_path = os.path.join(config['log']['output_dir'], config['log']['file_name'])

        safe_create_dir(config['log']['output_dir'])

        with io.open(self.log_file_path, 'r', encoding='utf-8') as log_file:
            try:
                self.entries = []
                tmp_entries = json.load(log_file)
                for t in tmp_entries:
                    entry = Entry(filename=None, field_initializer=t)
                    self.entries.append(entry)
            except json.decoder.JSONDecodeError:
                self.entries = []

    @staticmethod
    def load_raw_entries(path):
        """
        Load a given directory containing meta (json) and page data (md)
        Returns a list of all found entries in the form:
            ...
            'file': {
                'meta': {
                    'contents': ...,
                    'hash': ...
                },
                'page': {
                    'contents': ...,
                    'hash': ...
                }
            }
            ...
        """
        if not os.path.isdir(path):
            raise LogEntriesNotADirectoryError('Given path is not a directory')

        found_files = {}

        print(colored('Finding meta and page files in...', 'yellow'), path)
        for file in os.listdir(path):
            absolute_file_path = os.path.join(path, file)

            if os.path.isfile(absolute_file_path):

                # Finding meta and page files
                ext, fn = file_get_extension(file, strip_dot=True)

                # Read raw contents
                with io.open(absolute_file_path, 'rb') as raw_file:
                    raw_contents = raw_file.read()

                if _file_is_meta(ext):
                    field = 'meta'
                elif _file_is_page(ext):
                    field = 'page'
                else:
                    # Skip unrelated files
                    # TODO: Add other cases for images, stylesheets etc. (assets)
                    continue

                f_hash = contents_get_hash_md5(raw_contents)

                if fn not in found_files:
                    found_files[fn] = {
                        'meta': {},
                        'page': {}
                    }

                found_files[fn][field]['type'] = ext
                found_files[fn][field]['contents'] = raw_contents

                # Call before_load hooks on each file before the actual loader loads the file
                emit_hook(HOOK_BEFORE_LOAD, found_files[fn][field])

                # Find suitable loaders for meta and page contents
                loader = find_meta_loader_for_ext(ext)()
                if not loader:
                    raise LoaderNoSuitableLoaderError('No suitable loader found for this type')

                found_files[fn][field]['loaded'] = loader.read(raw_contents)
                found_files[fn][field]['hash'] = f_hash

                # Call before_load hooks on each file before the actual loader loads the file
                found_files[fn][field] = emit_hook(HOOK_AFTER_LOAD, found_files[fn][field])

        return found_files, [len(e) == 2 for e in found_files]

    def convert_raw_entries(self, found_entries):
        """
        Returns a dict of changed files (including meta and page information) of changed files
        by comparing the files' hashes with the ones stored in the log
        """
        changed_files = {}
        needs_complete_rebuild = False

        for entry_pair in found_entries:

            f_entry = self.find(name=entry_pair)

            if not f_entry:
                # Entry is not in the log yet, add it
                print(colored('Added new file', 'green'), '[meta]', colored(entry_pair, 'magenta'))

                entry = Entry(entry_pair)
                entry.hash_meta = found_entries[entry_pair]['meta']['hash']
                entry.hash_file = found_entries[entry_pair]['page']['hash']
                self.insert(entry)

                # If we add a new file and build_nav is enabled, we need to rebuild every page, as we
                # include the nav to all the files
                if config['templates']['build_nav']:
                    needs_complete_rebuild = True
                    print(colored('Need to rebuild every page due to build_nav option', 'red'))
            else:
                # File is in log already, compare hashes to find any changes
                if f_entry.hash_meta == found_entries[entry_pair]['meta']['hash'] \
                        and f_entry.hash_file == found_entries[entry_pair]['page']['hash']:
                    # Skipping file as there are no changes
                    print(colored('Skipping file due to no changes', 'magenta'), entry_pair)
                    continue
                else:
                    # There are changes so update the entry and add the file to the change list
                    if f_entry.hash_meta != found_entries[entry_pair]['meta']['hash']:
                        needs_complete_rebuild = True

                    print(colored('File needs to be rebuild', 'red'), entry_pair)
                    f_entry.hash_meta = found_entries[entry_pair]['meta']['hash']
                    f_entry.hash_file = found_entries[entry_pair]['page']['hash']
                    f_entry.update()

                    changed_files[entry_pair] = found_entries[entry_pair]

        return changed_files, needs_complete_rebuild

    def insert(self, entry):
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