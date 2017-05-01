import boto3
import logging
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def get_folders(response, prefix):
    content = response.get('CommonPrefixes', [])

    elements = []
    for element in content:
        elements.append(
            {
                'full_path': element['Prefix'].replace(settings.ROOT_FULL, ''),
                'name': element['Prefix'].replace(prefix, '')
            }
        )

    return elements


def get_files(response, prefix):
    content = response.get('Contents', [])
    elements = []
    for element in content:
        name = element['Key'].replace(prefix, '')
        full_path = element['Key'].replace(settings.ROOT_FULL, '')
        elements.append({'full_path': full_path, 'name': name})

    return elements


def get_from_file(fileid):
    temp_folder = settings.TMP_FOLDER
    filename = '{}/cache_{}'.format(temp_folder, fileid)
    return open(filename, "rb").read()


def write_file(body, fileid):
    temp_folder = settings.TMP_FOLDER
    filename = '{}/cache_{}'.format(temp_folder, fileid)
    try:
        f = open(filename, 'wb')
        f.write(body)
        f.close()
    except:
        pass


def show_file(request):
    if not request.GET.get('element', None):
        return HttpResponseNotFound()

    client = boto3.client(
        's3',
        aws_access_key_id=settings.ACCESS_KEY,
        aws_secret_access_key=settings.SECRET_KEY,
        region_name=settings.REGION,
    )

    filename = settings.ROOT_FULL + request.GET.get('element')
    try:
        head_response = client.head_object(Bucket=settings.BUCKET, Key=filename)
    except ClientError:
        return HttpResponseNotFound("File not found")

    fileid = head_response['ETag'].strip('"')
    try:
        body = get_from_file(fileid)
        return HttpResponse(body, content_type=head_response['ContentType'])
    except:
        pass

    response = client.get_object(Bucket=settings.BUCKET, Key=filename,)

    try:
        body = response['Body'].read()
        write_file(body, fileid)
        return HttpResponse(body, content_type=response['ContentType'])
    except:
        # red = Image.new('RGBA', (1, 1), (255, 0, 0, 0))
        # response = HttpResponse(content_type="image/jpeg")
        # red.save(response, "JPEG")
        response = HttpResponse('Image could not be served. Please try again later.')
        return response


def index(request):
    prefix = settings.ROOT_FULL + request.GET.get('element', '')

    client = boto3.client(
        's3',
        aws_access_key_id=settings.ACCESS_KEY,
        aws_secret_access_key=settings.SECRET_KEY,
        region_name=settings.REGION,
    )

    response = client.list_objects_v2(
        Bucket=settings.BUCKET,
        MaxKeys=1000,
        Prefix=prefix,
        Delimiter='/',
    )

    folders = get_folders(response, prefix)
    files = get_files(response, prefix)

    current_element = request.GET.get('element', 'Photo Gallery ').replace('_', ' ')[:-1]

    elements = {
        'current_element': current_element,
        'folders': folders,
        'files': files
    }

    return render(request, 'index.html', {'data': elements})
