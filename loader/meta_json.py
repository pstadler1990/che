import io
import json
from exceptions import LoaderWrongFileError
from loader.default import AMetaLoader
from helpers import file_get_extension


class MetaLoaderJSON(AMetaLoader):
    """
    Concrete implementation of a meta loader for JSON files
    Reads a given json file into a dict
    """
    def read(self, file):
        if file_get_extension(file, strip_dot=True) not in ['js', 'json']:
            raise LoaderWrongFileError('Given file is not a valid json file')

        with io.open(file, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
