import mistune
from loader.default import APageLoader


class PageLoaderMarkdown(APageLoader):
    """
    Concrete implementation of a page loader for markdown files
    Reads a given markdown file into html
    """
    def read(self, contents):
        return mistune.markdown(contents.decode('utf-8'))
