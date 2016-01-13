import os
import glob
import json
from django.core.management.base import BaseCommand

import requests

from langusta_client import app_settings
from langusta_client.exceptions import NoPoFilesFound

from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            "-H", "--host", action="store", type="string", dest="host"
        ),
        make_option(
            "-W", "--auth-token", action="store", type="string", dest="token"
        ),
        make_option(
            "-P", "--project-token", action="store", type="string", dest="project"
        ),
        make_option(
            "-D", "--dry-run", action="store_true", dest="dry_run", default=False
        ),
        make_option(
            "-t", "--tag", action="store", type="string", dest="tag", default='master'
        ),
    )

    def handle(self, *args, **options):
        self.debug = bool(options.get('dry_run'))
        self.env_tag = options.get('tag', '')
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
                     'Could not find any .po files in %r' % (source_folder)
                )
        print 'Translations found:\n', '\n'.join(files)

        for _filePath in files:
            filePath, domain = os.path.split(_filePath)
            language = filePath.split('/')[-2]
            print 'Uploading, language: {}, domain: {}'.format(language,
                                                               domain)

            content = open(_filePath, 'r').read()
            data = {
                'project_slug': app_settings.LANGUSTA['PROJECT_SLUG'],
                'content': content,
                'tags': [self.env_tag],
                'domain': domain,
                'language': language
            }

            headers = {
                'content-type': 'application/json',
                'Authorization': 'Token {}'.format(app_settings.LANGUSTA['AUTH_TOKEN'])
            }

            if not self.debug:
                response = requests.post(
                    self.url,
                    data=json.dumps(data), headers=headers
                )
                response.raise_for_status()
