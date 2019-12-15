import json

from writer.default import AMetaWriter


class MetaWriterJSON(AMetaWriter):
    """
    Concrete implementation of a meta writer for JSON files
    Writes a given dict into a json file
    """
    def write(self, contents):
        return json.dumps(contents)
