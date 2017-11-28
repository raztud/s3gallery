import logging
import boto3
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound

import csv
from botocore.exceptions import ClientError

logger = logging.getLogger('gallery')


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

