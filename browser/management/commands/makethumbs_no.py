import boto3

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

"""
python manage.py makethumbs --bucket=utgal --start=g3/21645e22db975037a385a03701f2683c/

def makeThumb(filename):
    if doesNotExistsTumb(filename):
        getFileLocaly()
        makeThum()
        uploadThum()

def checkFiles(start)
    foreach element in list:
        if isImageFile(element):
            makeThumb(element)
        elif isFolder(element):
            checkFiles(element)

"""


class Command(BaseCommand):
    help = 'Make thumbs'
    bucket = None
    client = None
    MAX_ENTRIES = 1000

    def add_arguments(self, parser):
        parser.add_argument('--bucket', type=str, dest='bucket', default=settings.BUCKET, required=True, help='The AWS bucket')
        parser.add_argument('--start', type=str, dest='start', required=False, help='The AWS start path')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Bucket: {}'.format(options['bucket'])))
        self.stdout.write(self.style.SUCCESS('Start path: {}'.format(options['start'])))

        if options['start'] and options['start'][-1] != '/':
            options['start'] += '/'

        self.init_aws(options)

        self.check_files(options['start'])

    def init_aws(self, options):
        self.bucket = options['bucket']

        self.client = boto3.client('s3',
            aws_access_key_id=settings.ACCESS_KEY,
            aws_secret_access_key=settings.SECRET_KEY,
            region_name=settings.REGION,
        )

    def check_files(self, start=None):
        elements = self.get_folder_elements(start)

        for filename_el in elements['files']:
            self.make_thumb(filename_el)

        # for folder in elements['folder']:
        #     self.check_files(folder['full_path'])

        #
        # for element in elements:
        #     if self.is_image_file(element):
        #         self.make_thumb(element)
        #     elif self.is_folder(element):
        #         self.check_files(element)

    def make_thumb(self, filename):
        print(filename)

        # if self.does_not_exist_thumb(aws_folder, filename):
        #     local_path = self.download_file(filename)
        #     local_path_thumb = self.make_thum(local_path)
        #     self.upload_file(aws_folder, local_path_thumb)

    def get_folder_elements(self, folder=None):

        kwargs = {
            'Bucket': self.bucket,
            'MaxKeys': Command.MAX_ENTRIES,
            'Delimiter': '/'
        }

        if folder:
            kwargs['Prefix'] = folder

        response = self.client.list_objects_v2(**kwargs)
        print(response['CommonPrefixes'])

        folders = self.get_folders(response, folder)
        files = self.get_files(response, folder)

        return {'folders': folders, 'files': files}

    def get_files(self, response, prefix):
        content = response.get('Contents', [])
        elements = []
        for element in content:
            name = element['Key'].replace(prefix, '')
            if not name:
                continue
            full_path = element['Key'].replace(settings.ROOT_FULL, '')
            elements.append({'full_path': full_path, 'name': name})

        return elements

    def get_folders(self, response, prefix):
        content = response.get('CommonPrefixes', [])


        elements = []
        for element in content:
            meta_name = element['Prefix'].replace(prefix, '')[:-1]
            name = element['Prefix'].replace(prefix, '')
            elements.append(
                {
                    'full_path': element['Prefix'].replace(settings.ROOT_FULL, ''),
                    'name': name
                }
            )

        return elements

    def is_image_file(self, element):
        return True

    def download_file(self, filename):
        pass

    def make_thum(self, filename):
        pass

    def upload_file(self, aws_folder, local_path):
        return True

    def does_not_exist_thumb(self, aws_folder, filename):
        return True

    def is_folder(self, filename):
        pass