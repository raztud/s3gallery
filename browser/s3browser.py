import logging
import ujson
import boto3
from django.conf import settings
from botocore.exceptions import ClientError

logger = logging.getLogger('gallery')


class S3BrowserExceptionNotFound(Exception):
    pass


class S3BrowserReadingError(Exception):
    pass


class S3Browser(object):

    def __init__(self):

        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.ACCESS_KEY,
            aws_secret_access_key=settings.SECRET_KEY,
            region_name=settings.REGION,
        )

    def get_list(self, prefix):
        response = self.client.list_objects_v2(
            Bucket=settings.BUCKET,
            MaxKeys=1000,
            Prefix=prefix,
            Delimiter='/',
        )

        return {
            'folders': self._get_folders(response, prefix=prefix),
            'files': self._get_files(response, prefix=prefix)
        }

    def _get_folders(self, response, prefix):
        content = response.get('CommonPrefixes', [])

        meta = self._get_index_content(prefix)

        elements = []
        for element in content:
            meta_name = element['Prefix'].replace(prefix, '')[:-1]
            name = meta.get(meta_name) or element['Prefix'].replace(prefix, '')
            elements.append({
                'full_path': element['Prefix'].replace(settings.ROOT_FULL, ''),
                'name': name
            })

        return elements

    def _get_files(self, response, prefix):
        content = response.get('Contents', [])
        elements = []
        for element in content:
            name = element['Key'].replace(prefix, '')
            if name == 'index.json':
                continue

            if name[:6] == 'thumb_':
                continue

            if element.get('Size', 0) == 0:
                continue

            full_path = element['Key'].replace(settings.ROOT_FULL, '')
            elements.append({'full_path': full_path, 'name': name})

        return elements

    def get_raw_file(self, filename, cache=True):
        try:
            head_response = self.client.head_object(Bucket=settings.BUCKET,
                                                    Key=filename)
        except ClientError:
            logger.error('File not found: {}'.format(filename))
            raise S3BrowserExceptionNotFound

        fileid = head_response['ETag'].strip('"')
        if cache:
            try:
                body = self._get_from_file(fileid)
                return body, head_response['ContentType']
            except:
                pass

        response = self.client.get_object(Bucket=settings.BUCKET, Key=filename, )

        try:
            body = response['Body'].read()
            if cache:
                self._write_cache(body, fileid)
            return body, response['ContentType']
        except Exception as ex:
            logger.error('Exception reading: {}: {}'.format(filename, ex))
            raise S3BrowserReadingError

    def _get_index_content(self, prefix):

        filename = prefix + 'index.json'
        try:
            self.client.head_object(Bucket=settings.BUCKET, Key=filename)
        except ClientError:
            logger.info("{} not found".format(filename))
            return {}

        try:
            response = self.client.get_object(Bucket=settings.BUCKET,
                                              Key=filename, )
            body = response['Body'].read()
            jsonData = ujson.loads(body.decode('utf-8'))
            return jsonData
        except:
            logger.debug('index.json could not be read')
            return {}

    @staticmethod
    def _write_cache(body, fileid):
        temp_folder = settings.TMP_FOLDER
        filename = '{}/cache_{}'.format(temp_folder, fileid)
        try:
            f = open(filename, 'wb')
            f.write(body)
            f.close()
        except:
            pass

    @staticmethod
    def _get_from_file(fileid):
        temp_folder = settings.TMP_FOLDER
        filename = '{}/cache_{}'.format(temp_folder, fileid)
        return open(filename, 'rb').read()

    def has_thumb(self, s3filepath):
        """
        Returns the ETag if file exists or False
        :param s3filepath: FULL path to s3 file.
        :return:
        :rtype: str|False
        """
        tokens = s3filepath.split('/')
        filename = tokens[-1]
        s3path = '/'.join(tokens[:-1])
        s3thumbpath = s3path + '/thumb_' + filename
        try:
            head_response = self.client.head_object(Bucket=settings.BUCKET,
                                                    Key=s3thumbpath)
        except ClientError:
            return False

        return head_response['ETag'].strip('"')
