import os
import mimetypes
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

        folders = self.get_folders(options['start'])
        for folder in folders:
            items = self.get_items(folder)
            if not len(items['files']):
                self.stdout.write(self.style.WARNING('No file found in {}'.format(folder)))
                continue

            self.make_thumbs(items['files'])

    def get_folders(self, start, folders=None):
        if folders is None:
            folders = [start,]

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

        prefixes = Command.extract_prefixes(response)

        if len(prefixes):
            folders += prefixes
            for d in prefixes:
                self.get_folders(d, folders=folders)

        return folders

    @staticmethod
    def extract_prefixes(response):
        folders = []
        for data in response.get('CommonPrefixes', []):
            folders.append(data['Prefix'])

        return folders

    def make_thumbs(self, files):
        for f in files:
            if self.has_thumb(f):
                self.stdout.write(self.style.WARNING(
                    'Thumb for {} already exists'.format(f))
                )
                continue

            if Command.is_thumb(f):
                self.stdout.write(self.style.WARNING('{} is thumb'.format(f)))
                continue

            if f[-1] == '/':
                continue

            temporary_file = self.download_tmp_file(f)
            thumb_path = self.make_thumb(temporary_file)

            if thumb_path is None:
                continue

            thumb_name = thumb_path.split('/')[-1]
            s3path = '/'.join(f.split('/')[:-1]) + '/' + thumb_name

            self.upload_thumb(thumb_path, s3path)
            Command.clean_files([temporary_file, thumb_path])

    @staticmethod
    def is_thumb(s3filepath):
        tokens = s3filepath.split('/')
        filename = tokens[-1]
        if filename[:6] == 'thumb_':
            return True
        return False

    def has_thumb(self, s3filepath):
        tokens = s3filepath.split('/')
        filename = tokens[-1]
        s3path = '/'.join(tokens[:-1])
        s3thumbpath = s3path + '/thumb_' + filename
        try:
            self.client.head_object(Bucket=settings.BUCKET,
                                    Key=s3thumbpath)
        except ClientError:
            return False

        return True

    @staticmethod
    def clean_files(filelist):
        for filename in filelist:
            try:
                os.remove(filename)
            except OSError:
                pass

    def upload_thumb(self, thumb_path, s3path):

        self.stdout.write(
            self.style.SUCCESS('Upload {} to {} {}'.format(thumb_path,
                                                           self.bucket,
                                                           s3path)))

        extra = {
            'ACL': 'public-read',
        }

        mimetype = mimetypes.guess_type(thumb_path)[0]
        if mimetype:
            extra['ContentType'] = mimetype

        try:
            self.client.upload_file(thumb_path,
                                    self.bucket,
                                    s3path,
                                    ExtraArgs=extra)
        except:
            self.stdout.write(
                self.style.ERROR('Could not upload {} to {} {}'.
                                 format(thumb_path,
                                        self.bucket,
                                        s3path))
            )

    def make_thumb(self, file_path):
        file_tokens = file_path.split('/')
        filename = file_tokens[-1]
        folder = '/'.join(file_tokens[:-1])
        try:
            im = Image.open(file_path)
        except IOError:
            self.stdout.write(self.style.ERROR(
                'Could not open original image {}'.format(file_path)))
            return None

        width = im.size[0]
        height = im.size[1]
        aspect = width / float(height)

        ideal_width = 200
        ideal_height = 200

        ideal_aspect = ideal_width / float(ideal_height)

        if aspect > ideal_aspect:
            # Then crop the left and right edges:
            new_width = int(ideal_aspect * height)
            offset = (width - new_width) / 2
            resize = (offset, 0, width - offset, height)
        else:
            # ... crop the top and bottom:
            new_height = int(width / ideal_aspect)
            offset = (height - new_height) / 2
            resize = (0, offset, width, height - offset)

        try:
            thumb = im.crop(resize).resize((ideal_width, ideal_height),
                                           Image.ANTIALIAS)
            thumb_path = folder + '/thumb_' + filename
            thumb.save(thumb_path, "JPEG")
        except IOError:
            self.stdout.write(self.style.ERROR('Could not generate thumbnail'))
            return None

        return thumb_path

    def download_tmp_file(self, s3path):
        s3browser = S3Browser()
        try:
            body, content_type = s3browser.get_raw_file(s3path, cache=False)

            fname = s3path.split('/')[-1]
            filename = '/tmp/{}'.format(fname)
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
