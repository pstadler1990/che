from exceptions import LoaderNoSuitableLoaderError
from loader.meta_json import MetaLoaderJSON
from loader.page_markdown import PageLoaderMarkdown

available_loaders = [
    {
        'type': 'meta',
        'ext': ['js', 'json'],
        'loader': MetaLoaderJSON
    },
    {
        'type': 'page',
        'ext': ['md'],
        'loader': PageLoaderMarkdown
    }
]


def find_loader_for_ext(ext):
    try:
        return next(filter(lambda l: ext in l['ext'], available_loaders))['loader']
    except StopIteration:
        raise LoaderNoSuitableLoaderError('No suitable loader found for this file type')
