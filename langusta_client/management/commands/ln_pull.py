import os
from optparse import make_option

import requests
from django.core.management.base import BaseCommand
from django.conf import settings

from langusta_client import app_settings

DOMAINS = ['django.po', 'djangojs.po']


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            "-D", "--dry-run", action="store_true",
            dest="dry_run", default=False
        ),
        make_option(
            "-o", "--output", action="store", type="string", dest="output"
        ),
    )

    def handle(self, *args, **options):
        self.debug = bool(options.get('dry_run'))
        self.output_dir = options.get('output')
        if not self.output_dir:
            self.output_dir = settings.LOCALE_PATHS[0]

        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        elif not os.path.isdir(self.output_dir):
            raise OSError("{} is a file".format(self.output_dir))

        self.download_translation_files()

    def _url(self, lang, domain):
        return "{}/api/export/{}/{}/{}/{}/".format(
            app_settings.LANGUSTA['HOST'],
            app_settings.LANGUSTA['PROJECT_SLUG'],
            app_settings.LANGUSTA['PROJECT_TOKEN'],
            lang,
            domain,
        )

    def _download_file(self, lang, domain):
        po_file_dir = os.path.join(self.output_dir, lang, 'LC_MESSAGES')
        if not os.path.exists(po_file_dir):
            os.makedirs(po_file_dir)
        po_file_path = os.path.join(po_file_dir, domain)

        po_file_url = self._url(lang, domain)
        headers = {
            'Accept': 'text/po',
            'Authorization': 'Token {}'.format(app_settings.LANGUSTA['AUTH_TOKEN'])
        }
        po_response = requests.get(po_file_url, headers=headers)
        if po_response.status_code == 404:
            return
        po_response.raise_for_status()

        if self.debug:
            print(po_file_path)
            return

        with open(po_file_path, 'w') as po_fh:
            po_fh.write(po_response.text.encode("UTF-8"))
            print('Saved {}'.format(po_file_path))

    def download_translation_files(self):
        for lang in app_settings.LANGUSTA['LANGUAGES']:
            for domain in DOMAINS:
                self._download_file(lang, domain)
