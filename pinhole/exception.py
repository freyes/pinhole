class PinholeException(Exception):
    pass


class TimeOutError(PinholeException):
    pass


class PinholeFileNotFound(PinholeException):
    pass


class PinholeBucketNotFound(PinholeException):
    pass


class PinholeKeyNotFound(PinholeException):
    pass
