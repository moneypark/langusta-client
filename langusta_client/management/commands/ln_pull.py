import os

import requests
from django.core.management.base import BaseCommand
from django.conf import settings

from langusta_client import app_settings

DOMAINS = ['django.po', 'djangojs.po', ]
DEFAULT_TIMEOUT = 600


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            "-D", "--dry-run", action="store_true",
            dest="dry_run", default=False
        )
        parser.add_argument(
            "-o", "--output", action="store", type=str, dest="output"
        )
        parser.add_argument(
            "-to", "--timeout", action="store", dest="timeout", default=DEFAULT_TIMEOUT,
        )

    def handle(self, *args, **options):
        self.debug = bool(options.get('dry_run'))
        self.timeout = options.get('timeout')
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
            domain
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
        po_response = requests.get(po_file_url, headers=headers, timeout=self.timeout or DEFAULT_TIMEOUT)
        if po_response.status_code == 404:
            return
        po_response.raise_for_status()

        if self.debug:
            print(po_file_path)
            return

        with open(po_file_path, 'w') as po_fh:
            po_fh.write(po_response.text)
            print('Saved {}'.format(po_file_path))

    def download_translation_files(self):
        for lang in app_settings.LANGUSTA['LANGUAGES']:
            for domain in DOMAINS:
                self._download_file(lang, domain)
