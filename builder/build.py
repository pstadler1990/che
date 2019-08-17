import io
import os
import yaml
from exceptions import BuildNoBuildFilesError, LoaderNoSuitableLoaderError
from loader.loaders import find_meta_loader_for_ext
from nlp import nlp_process
from builder.template import render_template
from termcolor import colored
from helpers import safe_create_dir


config = yaml.safe_load(open('config.yml'))


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
        if build_files is None:
            raise BuildNoBuildFilesError('No build files given')
        self.files = build_files
        self.contents = {}

    def prepare(self):
        """
        Takes all [meta] and [page] entries from the log-convert process (changed_files)
        and uses a suitable loader from /loader for [meta] and [page] to load into a dict (meta) and html (page)
        """
        self.contents = {}
        for entry_pair in self.files:
            self.contents[entry_pair] = {}
            # Find suitable loaders for meta and page contents
            for entry in self.files[entry_pair]:
                loader = find_meta_loader_for_ext(self.files[entry_pair][entry]['type'])()
                if not loader:
                    raise LoaderNoSuitableLoaderError('No suitable loader found for this type')

                self.contents[entry_pair][entry] = loader.read(self.files[entry_pair][entry]['contents'])

        print('Preparation finished')

    def process_text_auto(self):
        """
        Automatically process the page's text
        This method can:
            - Extract keywords by enabling the extract_keywords option
            - Generate a summary by enabling the summary option
        """
        for entry_pair in self.contents:
            keywords, summary = nlp_process(self.contents[entry_pair]['page'])
            print(keywords, summary)

    def build(self):
        """
        Render output using the Jinja template engine
        """
        for page in self.contents:
            page_obj = self.contents[page]

            output_html = render_template(page_obj['meta']['template'], {
                'title': page_obj['meta']['title'],
                'content': page_obj['page']
            })

            print(colored('Generated output file', 'green'), page)

            output_path = os.path.join(config['output']['output_dir'], '{0}.{1}'.format(page, config['output']['file_format']))

            safe_create_dir(output_path)
            with io.open(output_path, 'w+', encoding='utf-8') as output_file:
                output_file.write(output_html)
