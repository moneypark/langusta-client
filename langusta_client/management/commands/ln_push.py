import os
import glob
import json

import requests
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from langusta_client import app_settings
from langusta_client.exceptions import NoPoFilesFound


IMPORT_ID_LENGTH = 40
DEFAULT_TIMEOUT = 600


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "-H", "--host", action="store", type=str, dest="host"
        )
        parser.add_argument(
            "-W", "--auth-token", action="store", type=str, dest="token"
        )
        parser.add_argument(
            "-P", "--project-token", action="store", type=str, dest="project"
        )
        parser.add_argument(
            "-D", "--dry-run", action="store_true", dest="dry_run", default=False
        )
        parser.add_argument(
            "-t", "--tag", action="store", type=str, dest="tag", default='master'
        )
        parser.add_argument(
            "-A", "--actualize", action="store_true", dest="actualize", default=False
        )
        parser.add_argument(
            "-ar", "--append-references", action="store_true", dest='append_references', default=False,
        )
        parser.add_argument(
            "-O", "--overwrite", action="store_true", dest='overwrite', default=False,
        )
        parser.add_argument(
            "-dr", "--drop-references", action="store_true", dest='drop_references_for_missing', default=False,
        )
        parser.add_argument(
            "-to", "--timeout", action="store", dest="timeout", default=DEFAULT_TIMEOUT,
        )

    def handle(self, *args, **options):
        self.debug = bool(options.get('dry_run'))
        self.env_tag = options.get('tag', '')
        self.actualize = options.get('actualize')
        self.append_references = options.get('append_references')
        self.overwrite = options.get('overwrite')
        self.drop_references_for_missing = options.get('drop_references_for_missing')
        self.timeout = options.get('timeout')
        self.upload_translation_file()

    @property
    def url(self):
        return "{}/api/import/{}/{}/".format(
            app_settings.LANGUSTA['HOST'],
            app_settings.LANGUSTA['PROJECT_SLUG'],
            app_settings.LANGUSTA['PROJECT_TOKEN']

        )

    def upload_translation_file(self):
        files = []
        for lang in app_settings.LANGUSTA['LANGUAGES']:
            source_folder = os.path.join(
                app_settings.LANGUSTA['SOURCE_PATH'], lang, 'LC_MESSAGES'
            )
            files += [filepath for filepath in glob.glob(source_folder + '/*.po')]
            if not files:
                raise NoPoFilesFound(
                     'Could not find any .po files in %r' % (source_folder,)
                )
        print('Translations found:\n', '\n'.join(files))

        # Used to group all translations as one import event
        langusta_import_id = get_random_string(IMPORT_ID_LENGTH)

        for _filePath in files:
            filePath, domain = os.path.split(_filePath)
            language = filePath.split('/')[-2]
            print('Uploading, language: {}, domain: {}'.format(language,
                                                               domain))

            content = open(_filePath, 'r').read()
            data = {
                'project_slug': app_settings.LANGUSTA['PROJECT_SLUG'],
                'content': content,
                'tags': [self.env_tag],
                'domain': domain,
                'language': language,
                'import_id': langusta_import_id,
                'actualize': self.actualize,
                'append_references': self.append_references,
                'overwrite': self.overwrite,
                'drop_references_for_missing': self.drop_references_for_missing,
            }

            headers = {
                'content-type': 'application/json',
                'Authorization': 'Token {}'.format(app_settings.LANGUSTA['AUTH_TOKEN'])
            }

            if not self.debug:
                response = requests.post(
                    self.url,
                    data=json.dumps(data),
                    headers=headers,
                    timeout=self.timeout or DEFAULT_TIMEOUT
                )
                try:
                    response.raise_for_status()
                except IOError:
                    if response.headers.get('content-type') == 'application/json':
                        print(response.json())
                    raise
