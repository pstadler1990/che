from writer.default import APageWriter
import html2markdown


class PageWriterMarkdown(APageWriter):
    """
    Concrete implementation of a page writer for markdown files
    Writes a given html string into a markdown file
    """
    def write(self, contents):
        return html2markdown.convert(contents)
