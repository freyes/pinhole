from datetime import datetime
from sqlalchemy.types import CHAR
import sqlalchemy.types as types


class RationalType(types.TypeDecorator):
    """
    Representation of EXIF Rational data type
    """
    impl = types.Unicode

    def __init__(self):
        super(RationalType, self).__init__(100)

    def process_bind_param(self, value, dialect):
        if not value:
            return None

        return "|".join([str(x) for x in value])

    def process_result_value(self, value, dialect):
        if not value:
            return None

        t = tuple()
        for v in value.split("|"):
            t += (int(v), )

        return t


class DateTime(types.TypeDecorator):
    impl = CHAR
    FORMAT = "%Y-%m-%d %H:%M:%S"

    def load_dialect_impl(self, dialect):
        if dialect.name == "sqlite":
            return dialect.type_descriptor(CHAR(25))
        else:
            return dialect.type_descriptor(types.DateTime())

    def process_bind_param(self, value, dialect):
        if not value:
            return value

        if dialect.name == "sqlite":
            if isinstance(value, datetime):
                return value.strftime(self.FORMAT)
            else:
                return value
        else:
            return value

    def process_result_value(self, value, dialect):
        if not value:
            return value

        if dialect.name == "sqlite":
            return datetime.strptime(value, self.FORMAT)
        else:
            return value
