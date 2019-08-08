from loader.meta_json import MetaLoaderJSON

available_loaders = [
    {
        'ext': ['js', 'json'],
        'loader': MetaLoaderJSON
    }
]


def find_meta_loader_for_ext(ext):
    return list(filter(lambda l: ext in l['ext'], available_loaders))[0]['loader']
