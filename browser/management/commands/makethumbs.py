import boto3
from uuid import uuid1
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from browser.s3browser import S3Browser, S3BrowserExceptionNotFound, \
    S3BrowserReadingError


class Command(BaseCommand):
    help = 'Make thumbs'
    bucket = None
    client = None
    MAX_ENTRIES = 1000

    def add_arguments(self, parser):
        parser.add_argument('--bucket', type=str, dest='bucket', default=settings.BUCKET, required=True, help='The AWS bucket')
        parser.add_argument('--start', type=str, dest='start', required=True, help='The AWS start path. Eg: path/to/folder/')

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

        items = self.get_items(options['start'])
        # print(items)
        if not len(items['files']):
            self.stdout.write(self.style.ERROR('No file found in path'))
            return

        self.make_thumbs(items['files'])

    def make_thumbs(self, files):
        for f in files:
            temporary_file = self.download_tmp_file(f)


    def download_tmp_file(self, s3path):
        print(s3path)
        s3browser = S3Browser()
        try:
            body, content_type = s3browser.get_raw_file(s3path, cache=False)

            fname = s3path.split('/')[-1]
            filename = '/tmp/s3gall_{}_{}'.format(str(uuid1()), fname)
            try:
                f = open(filename, 'wb')
                f.write(body)
                f.close()
            except:
                self.stdout.write(self.style.ERROR(
                    'Could not write temporary file {}'.format(filename)))
                return None

            return filename

        except S3BrowserExceptionNotFound:
            self.stdout.write(self.style.ERROR('file not found in '
                                               'S3: {}'.format(s3path)))
            return None
        except S3BrowserReadingError:
            self.stdout.write(
                self.style.ERROR('file not read from S3: {}'.format(s3path)))
            return None



    def get_items(self, start):
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

        print(kwargs)
        response = self.client.list_objects_v2(**kwargs)

        files = self.get_files(response)

        return {'files': files}

    def get_files(self, response):
        content = response.get('Contents', [])
        elements = []
        for element in content:
            if not element['Key']:
                continue
            elements.append(element['Key'])

        return elements
