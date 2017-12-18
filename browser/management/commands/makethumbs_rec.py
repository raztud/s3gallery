import os
import mimetypes
from pprint import pprint
import boto3
from botocore.exceptions import ClientError
from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand
from browser.s3browser import S3Browser, S3BrowserExceptionNotFound, \
    S3BrowserReadingError


class Command(BaseCommand):
    help = 'Make thumbs'
    bucket = None
    client = None
    MAX_ENTRIES = 1000

    def add_arguments(self, parser):
        parser.add_argument('--bucket', type=str, dest='bucket',
                            default=settings.BUCKET, required=True,
                            help='The AWS bucket')
        parser.add_argument('--start', type=str, dest='start', required=True,
                            help='The AWS start path. Eg: path/to/folder/')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bucket: {}'.format(
            options['bucket'])))
        self.stdout.write(self.style.SUCCESS('Start path: {}'.format(
            options['start'])))
        self.bucket = options['bucket']

        self.client = boto3.client('s3',
                                   aws_access_key_id=settings.ACCESS_KEY,
                                   aws_secret_access_key=settings.SECRET_KEY,
                                   region_name=settings.REGION, )

        folders = self.get_items(options['start'])
        pprint(folders)
        for folder in folders:
            print('python manage.py makethumbs --bucket utgal --start="{}"'.format(folder))
        # if not len(items['files']):
        #     self.stdout.write(self.style.ERROR('No file found in path'))
        #     return

        # self.make_thumbs(items['files'])

    def get_items(self, start, folders=None):
        if folders is None:
            folders = []

        kwargs = {
            'Bucket': self.bucket,
            'MaxKeys': Command.MAX_ENTRIES,
            'Delimiter': '/',
            'Prefix': start,
        }

        if start != '/':
            # the folder must end in / and should not start with /
            # eg: path/to/folder/
            if start[0] == '/':
                start = start[1:]
            if start[-1] != '/':
                start += '/'

            kwargs['Prefix'] = start

        response = self.client.list_objects_v2(**kwargs)

        prefixes = self.get_folders(response)

        if len(prefixes):
            folders += prefixes
            for d in prefixes:
                self.get_items(d, folders=folders)

        return folders

    def get_folders(self, response):
        folders = []
        for data in response.get('CommonPrefixes', []):
            folders.append(data['Prefix'])

        return folders

    # def get_files(self, response):
    #     content = response.get('Contents', [])
    #     elements = []
    #     for element in content:
    #         if not element['Key']:
    #             continue
    #         elements.append(element['Key'])
    #
    #     return elements