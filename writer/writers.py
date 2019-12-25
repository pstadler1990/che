from exceptions import WriterNoSuitableWriterError
from writer.meta_json import MetaWriterJSON
from writer.page_markdown import PageWriterMarkdown

available_writers = [
    {
        'type': 'meta',
        'ext': 'json',
        'writer': MetaWriterJSON
    },
    {
        'type': 'page',
        'ext': 'md',
        'writer': PageWriterMarkdown
    }
]


def find_writer_for_ext(ext):
    try:
        return next(filter(lambda l: ext in l['ext'], available_writers))['writer']
    except StopIteration:
        raise WriterNoSuitableWriterError('No suitable writer found for this file type')
