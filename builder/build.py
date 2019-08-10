from exceptions import BuildNoBuildFilesError, LoaderNoSuitableLoaderError
from loader.loaders import find_meta_loader_for_ext


class Builder:
    """
    Build process:

    1. Take all [meta] and [page] entries from the log-convert process (changed_files)
    2. Use a suitable loader from /loader for [meta] and [page] to load into a dict (meta) and html (page)
    3. Use nltk to add meta information to the html page (keywords, description, etc)
    4. Load Jinja env and replace variables (title, content, etc) with meta and page information
    5. Create dist/ folder (if none yet)
    6. For images / css / etc. create a suitable folder for each asset type
    7.
    8. Test link and asset integrity (collect each link / asset (like img src, a hrefs etc) for 200 ok or errors

    Missing:
    - Menu / nav generation
    - Sitemap generation
    - robots.txt generation
    - Template partials (header, footer, etc)
    """
    def __init__(self, build_files):
        if not build_files:
            raise BuildNoBuildFilesError('No build files given')
        self.files = build_files

    def prepare(self):
        """
        Takes all [meta] and [page] entries from the log-convert process (changed_files)
        and uses a suitable loader from /loader for [meta] and [page] to load into a dict (meta) and html (page)
        """
        for entry_pair in self.files:
            # Find suitable loaders for meta and page contents
            contents = {}
            for entry in self.files[entry_pair]:
                loader = find_meta_loader_for_ext(self.files[entry_pair][entry]['type'])()
                if not loader:
                    raise LoaderNoSuitableLoaderError('No suitable loader found for this type')

                contents[entry] = loader.read(self.files[entry_pair][entry]['contents'])

        print('Preparation finished')
