import json
from loader.default import AMetaLoader


class MetaLoaderJSON(AMetaLoader):
    """
    Concrete implementation of a meta loader for JSON files
    Reads a given json file into a dict
    """
    def read(self, contents):
        return json.loads(contents)
