from __future__ import absolute_import
import os
import hashlib
from os import path
from tempfile import mkdtemp
from urlparse import urlparse
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from pinhole.exception import (PinholeFileNotFound, PinholeBucketNotFound,
                               PinholeKeyNotFound)

__all__ = ["S3Adapter", "CACHE_DIR", "get_image", "upload_image", "is_valid",
           "get_cache_fpath"]
CACHE_DIR = os.environ.get("PINHOLE_CACHE_DIR",
                           mkdtemp("-cache", "pinhole-"))
if not path.isdir(CACHE_DIR):
    if not path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    else:
        raise ValueError("%s is not a directory" % CACHE_DIR)


class S3Adapter(S3Connection):
    def __init__(self, access_key=None, secret_key=None):
        from pinhole.common.app import app

        if not access_key:
            access_key = app.config["AWS_ACCESS_KEY"]

        if not secret_key:
            secret_key = app.config["AWS_SECRET_KEY"]

        S3Connection.__init__(self, access_key, secret_key)


def get_image(uri, dst=None, access_key=None, secret_key=None, use_cache=True):
    """
    Return a fp to the downloaded image

    :param uri: uri the object (s3://foo/bar.jpg)
    :type uri: str
    :param dst: where to save the image, it can a file pointer ready to write
                or a path, if there is already a file located there will be
                truncated.
    :type dst: fp or str
    :param access_key: AWS access key, if it's not provided it will be taken
                       from the app config
    :type access_key: str
    :param secret_key: AWS secret key, if it's not provided it will be taken
                       from the app config
    :type secret_key: str
    :param use_cache: if it's True, then try to get the image from the cache
                      directory first
    :returns: a file object open at the beginning of the file
    """
    if use_cache:
        valid = is_valid(uri)
        if valid:
            return open(valid, "rb+")

    try:
        (bucket, key) = parse_s3_uri(uri, create_key=False)
    except (PinholeKeyNotFound, PinholeBucketNotFound):
        raise PinholeFileNotFound(uri)

    cache_fpath = get_cache_fpath(uri)

    # TODO: implement max_cache_size
    fp = open(cache_fpath, "wb+")
    key.get_contents_to_file(fp)
    fp.flush()
    fp.seek(0)
    return fp


def parse_s3_uri(uri, access_key=None, secret_key=None, create_key=True):
    """
    Parses the s3 uri to get the bucket and key

    :param uri: the uri to parse
    :type uri: str
    :param access_key: AWS access key, if it's not provided it will be taken
                       from the app config
    :type access_key: str
    :param secret_key: AWS secret key, if it's not provided it will be taken
                       from the app config
    :type secret_key: str
    :param create_key: if True and the key isn't found, the it's created,
                      otherwise raises ValueError
    :returns: a tuple with the bucket and key objects
    """
    parsed = urlparse(uri)
    s3conn = S3Adapter(access_key, secret_key)
    bucket = s3conn.lookup(parsed.hostname)

    if not bucket:
        raise PinholeBucketNotFound("bucket %s not found" % parsed.hostname)

    key_name = parsed.path.lstrip("/")
    key = bucket.lookup(key_name)
    if not key:
        if create_key:
            key = Key(bucket)
            key.key = key_name
        else:
            raise PinholeKeyNotFound("key %s not found in bucket %s"
                                     % (key_name, parsed.hostname))

    return (bucket, key)


def upload_image(src, dst, access_key=None, secret_key=None):
    """
    Upload a file to S3

    :param src: the source, it can be a file like object or a path to a file in
                the file system.
    :type src: fp or str
    :param dst: a uri where to save the content of `src`
                (i.e. s3://foo/bar.jpg")
    :type dst: str
    :param access_key: AWS access key, if it's not provided it will be taken
                       from the app config
    :type access_key: str
    :param secret_key: AWS secret key, if it's not provided it will be taken
                       from the app config
    :type secret_key: str
    :returns: number of bytes uploaded
    """
    # TODO: leave a copy of the file in cache
    close = False
    if hasattr(src, "read") and callable(src.read):
        fp = src
    else:
        if path.isfile(src):
            fp = open(src, "rb")
            close = True
        else:
            raise ValueError("%s is not a file" % src)

    (bucket, key) = parse_s3_uri(dst, create_key=True)

    num_bytes = key.set_contents_from_file(fp)

    if close:
        fp.close()

    return num_bytes


def is_valid(uri, access_key=None, secret_key=None):
    """
    Check if the file pointed out by uri is available in the cache dir.

    :param access_key: AWS access key, if it's not provided it will be taken
                       from the app config
    :type access_key: str
    :param secret_key: AWS secret key, if it's not provided it will be taken
                       from the app config
    :type secret_key: str
    :returns: True if object pointed out by uri was found in the cache and
              is valid
    """
    cache_fpath = get_cache_fpath(uri)
    if not path.isfile(cache_fpath):
        return False

    # the file exists, now let's check the content
    m = hashlib.md5()
    with open(cache_fpath, "rb") as f:
        m.update(f.read())

    cached_md5 = m.hexdigest()

    parsed = urlparse(uri)
    s3conn = S3Adapter()
    if not parsed.hostname:
        return False

    bucket = s3conn.get_bucket(parsed.hostname)
    if not bucket:
        return False

    key = bucket.get_key(parsed.path.lstrip("/"))
    if not key:
        return False

    if key.etag.strip('"') == cached_md5:
        return cache_fpath
    else:
        return False


def get_cache_fpath(uri):
    m = hashlib.md5()
    m.update(uri)
    fname = m.hexdigest()

    parsed = urlparse(uri)
    (root, ext) = path.splitext(parsed.path)
    cache_fpath = path.join(CACHE_DIR, fname + ext)
    return cache_fpath
