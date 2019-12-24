import io
import os

import htmlmin
from termcolor import colored

from builder.template import render_template
from configuration import config
from exceptions import BuildNoBuildFilesError
from helpers import safe_create_dir
from nlp import nlp_process


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
        self.nav_entries = []

    def prepare(self):
        """
        Takes all [meta] and [page] entries from the log-convert process (changed_files)
        and uses a suitable loader from /loader for [meta] and [page] to load into a dict (meta) and html (page)
        """
        # Filter out all entries that are not in published state (i.e. draft)
        self.contents = {k: v for k, v in self.files.items() if v['meta']['loaded']['status'] == 'published'}

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

    def build_nav(self, all_files, use_absolute_links=True):
        """
        Generates an internal representation of the website's navigation of all passed files
        Call this method before build() to include a nav within the website
        """
        print(colored('Building navigation', 'grey'))

        self.nav_entries = []
        for entry_pair in all_files:
            page_obj = all_files[entry_pair]

            self.nav_entries.append({
                'title': page_obj['meta']['loaded']['title'],
                'url': '{0}{1}.{2}'.format('/' if use_absolute_links else '', page_obj['meta']['loaded']['slug'], config['output']['file_format'])
            })

    def build(self, minify_html=True):
        """
        Render output using the Jinja template engine
        """
        for page in self.contents:
            page_obj = self.contents[page]

            output_html = render_template(page_obj['meta']['loaded']['template'], page={
                'title': page_obj['meta']['loaded']['title'],
                'content': page_obj['page']['loaded']
            }, nav=self.nav_entries)

            print(colored('Generated output file', 'green'), page_obj['meta']['loaded']['slug'])

            output_path = os.path.join(config['output']['output_dir'], '{0}.{1}'.format(page_obj['meta']['loaded']['slug'], config['output']['file_format']))

            if minify_html:
                output_html = htmlmin.minify(output_html, remove_comments=True, remove_empty_space=True)

            safe_create_dir(output_path)
            with io.open(output_path, 'w+', encoding='utf-8') as output_file:
                output_file.write(output_html)
