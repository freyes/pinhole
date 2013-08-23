from __future__ import absolute_import
import os
import hashlib
from os import path
from tempfile import NamedTemporaryFile
from nose.tools import (assert_equal, assert_false, assert_is_not, assert_true,
                        assert_raises, assert_is_instance)
from boto.s3.bucket import Bucket
from boto.s3.key import Key
from pinhole.exception import (PinholeBucketNotFound, PinholeKeyNotFound,
                               PinholeFileNotFound)
from pinhole.common.app import app
from .. import s3


class TestGetImage(object):
    def setUp(self):
        self.uri = "s3://%s/fua/upload.jpg" % app.config["PHOTO_BUCKET"]

    def tearDown(self):
        try:
            (bucket, key) = s3.parse_s3_uri(self.uri)
            key.delete()
        except (PinholeBucketNotFound, PinholeKeyNotFound):
            pass

        try:
            cache_fpath = s3.get_cache_fpath(self.uri)
            os.remove(cache_fpath)
        except:
            pass

    def test_missing_image(self):
        assert_raises(PinholeFileNotFound, s3.get_image,
                      self.uri, use_cache=False)

    def test_from_cache(self):
        with NamedTemporaryFile() as f:
            f.write("meh")
            f.flush()
            s3.upload_image(f.name, self.uri)

        cache_fpath = s3.get_cache_fpath(self.uri)

        with open(cache_fpath, "wb") as f:
            f.write("meh")
            f.flush()

        f = s3.get_image(self.uri, use_cache=True)
        assert_is_not(f, None)
        assert_equal(f.read(), "meh")
        f.close()

    def test_miss_cache(self):
        with NamedTemporaryFile() as f:
            f.write("meh")
            f.flush()
            s3.upload_image(f.name, self.uri)

        f = s3.get_image(self.uri, use_cache=True)
        assert_is_not(f, None)
        assert_equal(f.read(), "meh")
        f.close()


class TestUploadImage(object):
    def setUp(self):
        self.local_fp = NamedTemporaryFile(suffix=".jpg")
        self.local_path = self.local_fp.name

        self.local_fp.write("abcde")
        self.local_fp.flush()
        self.local_fp.seek(0)

        self.num_bytes = len(self.local_fp.read())
        self.local_fp.seek(0)

        self.dst_uri = "s3://%s/fua/upload.jpg" % app.config["PHOTO_BUCKET"]

    def tearDown(self):
        self.local_fp.close()

        try:
            (bucket, key) = s3.parse_s3_uri(self.dst_uri)
            key.delete()
        except (PinholeBucketNotFound, PinholeKeyNotFound):
            pass

    def test_from_path(self):
        assert_equal(s3.upload_image(self.local_path, self.dst_uri),
                     self.num_bytes)

    def test_from_missing_path(self):
        assert_raises(ValueError, s3.upload_image, "asd", "as")


class TestParseS3Uri(object):
    def setUp(self):
        self.uri = "s3://%s/fooooo.jpg" % app.config["PHOTO_BUCKET"]

    def tearDown(self):
        try:
            s3conn = s3.S3Adapter()
            bucket = s3conn.lookup(app.config["PHOTO_BUCKET"])
            key = bucket.lookup("fooooo.jpg")
            key.delete()
        except Exception, ex:
            print ex

    def test_missing_key(self):
        uri = "s3://%s/fos.jpg" % app.config["PHOTO_BUCKET"]
        assert_raises(PinholeKeyNotFound, s3.parse_s3_uri,
                      uri, create_key=False)

    def test_missing_bucket(self):
        assert_raises(PinholeBucketNotFound, s3.parse_s3_uri, "s3://sdfnsdf")

    def test_create_key(self):
        self.uri = "s3://%s/fooooo.jpg" % app.config["PHOTO_BUCKET"]
        (bucket, key) = s3.parse_s3_uri(self.uri, create_key=True)

        assert_is_instance(bucket, Bucket)
        assert_is_instance(key, Key)
        assert_equal(key.key, "fooooo.jpg")


class TestIsValid(object):
    def setUp(self):
        self.missing_object_uri = "s3://%s/fua/a.jpg" \
                                  % app.config["PHOTO_BUCKET"]

        self.s3conn = s3.S3Adapter()

        bucket = self.s3conn.get_bucket(app.config["PHOTO_BUCKET"])
        assert_is_not(bucket, None)
        self.key = Key(bucket)
        self.key.key = "a/b/c.jpg"
        self.key.set_contents_from_string("abcd")

        self.object_uri = "s3://%s/a/b/c.jpg" \
                          % app.config["PHOTO_BUCKET"]

    def tearDown(self):
        try:
            self.key.delete()
        except Exception, ex:
            print ex

        try:
            os.remove(s3.get_cache_fpath(self.object_uri))
        except:
            pass

    def test_missing_object(self):
        assert_false(s3.is_valid(self.missing_object_uri))

    def test_not_in_cache(self):
        assert_false(s3.is_valid(self.object_uri))

    def test_in_cache(self):
        with open(s3.get_cache_fpath(self.object_uri), "wb") as f:
            f.write("abcd")
            f.flush()
            assert_true(s3.is_valid(self.object_uri))


class TestGetCacheFpath(object):
    def test_ok(self):
        uri = "s3://foo/mesh/grr.jpg"
        m = hashlib.md5()
        m.update(uri)
        fname = m.hexdigest()
        result = s3.get_cache_fpath(uri)

        assert_equal(result, path.join(s3.CACHE_DIR, fname + ".jpg"))
