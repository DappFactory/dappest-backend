# -*- coding: utf-8 -*-
from random import randint
from uuid import uuid4
from base64 import b64decode
from eth_account.messages import defunct_hash_message
from web3.auto import w3


def round_down_datetime(datetime, unit='minute'):
    """
    Round datetime down for a unit of time.
    """
    if unit == 'day':
        return datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    elif unit == 'hour':
        return datetime.replace(minute=0, second=0, microsecond=0)
    elif unit == 'minute':
        return datetime.replace(second=0, microsecond=0)


def round_float(num, places=2):
    """
    Round float number to specified number of decimal places.
    :param num:
    :param places:
    :return:
    """
    f = '%.{}f'.format(places)

    return float(f % num)


def validate_request(request, required_fields):
    """
    Validate required fields in request.
    :return:
    """
    return all(1 if request.get(f) is not None else 0 for f in required_fields)


def validate_image(base64_string, max_size=10000000):
    """
    Validate base64 encoded string of an image.
    Default max size is 10 MB.
    :return:
    """
    return (len(base64_string) * 3 / 4) <= max_size


def valdate_image_type(base64_string, file_extension):
    """
    Validate image file type.
    :param base64_string:
    :param file_extension:
    :return:
    """
    if file_extension not in ['png', 'jpg', 'jpeg', 'tiff', 'gif', 'bmp']:
        return '{} file format not supported.'.format(file_extension)

    if base64_string and not validate_image(base64_string):
        return 'Uploaded image exceeds max file limit (10MB).'

    return None


def upload_image_to_s3(s3_client, bucket, base64_string, file_type, path=''):
    """
    Upload base64 encoded image to S3.
    :param s3_client:
    :param bucket:
    :param base64_string:
    :param file_type:
    :param path:
    :return:
    """
    if file_type == 'jpg':
        file_type = 'jpeg'

    formatted_path = path if path == '' else '{path}/'.format(path=path)
    image_name = '{path}{image_name}.{file_type}'.format(path=formatted_path, image_name=uuid4().hex, file_type=file_type)
    content_type = 'image/{}'.format(file_type)

    s3_client.put_object(Bucket=bucket, Key=image_name, Body=b64decode(base64_string), ContentType=content_type)

    return image_name


def move_s3(s3_client, bucket, old_key, new_key):
    """
    Move single file in the same bucket from old_key to new_key.
    :param s3_client:
    :param bucket:
    :param old_key:
    :param new_key:
    :return:
    """
    old_source = {'Bucket': bucket,
                  'Key': old_key}

    s3_client.copy_object(Bucket=bucket, CopySource=old_source, Key=new_key)
    s3_client.delete_object(Bucket=bucket, Key=old_key)

    return new_key


def move_recursive_s3(s3_client, bucket, old_prefix, new_prefix):
    """
    Recursively move files in the same bucket from old_prefix to new_prefix.
    :param s3_client:
    :param bucket:
    :param old_prefix:
    :param new_prefix:
    :return:
    """
    new_keys = []
    for obj in s3_client.list_objects_v2(Bucket=bucket, Prefix=old_prefix).get('Contents'):
        old_key = obj.get('Key')
        new_key = move_s3(s3_client, bucket, old_key, old_key.replace(old_prefix, new_prefix))
        new_keys.append(new_key)

    return new_keys


def verify_eth_signed_message(public_address, message, signature):
    """
    Verify signed message via ethereum private key.
    :param public_address:
    :param message:
    :param signature:
    :return:
    """
    message_hash = defunct_hash_message(text=message)
    return public_address == w3.eth.account.recoverHash(message_hash, signature=signature)


def generate_nonce():
    """
    Generate nonce.
    :return:
    """
    return str(randint(0, 100000000))


def verify_eth_address(address):
    """
    Verify the ethereum address.
    :param address:
    :return:
    """
    return w3.isChecksumAddress(address)
