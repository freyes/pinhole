import tempfile
import shutil
from contextlib import contextmanager


@contextmanager
def mkdtemp(*args, **kwargs):
    d = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield d
    finally:
        shutil.rmtree(d)
