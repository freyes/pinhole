import re
import tempfile
import shutil
from contextlib import contextmanager


RE_FIRST_CAP = re.compile('(.)([A-Z][a-z]+)')
RE_ALL_CAP = re.compile('([a-z0-9])([A-Z])')


@contextmanager
def mkdtemp(*args, **kwargs):
    d = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield d
    finally:
        shutil.rmtree(d)


def convert(name):
    s1 = RE_FIRST_CAP.sub(r'\1_\2', name)
    return RE_ALL_CAP.sub(r'\1_\2', s1).lower()
