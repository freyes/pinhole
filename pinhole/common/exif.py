from datetime import datetime

DATETIME_FMT = "%Y:%m:%d %H:%M:%S"


def transform_datetime(raw_value, fail_silently=True):
    try:
        return datetime.strptime(raw_value, DATETIME_FMT)
    except Exception as ex:
        if not fail_silently:
            raise ex
        else:
            return None


exif_transform = {"DateTime": transform_datetime,
                  "DateTimeDigitized": transform_datetime,
                  "DateTimeOriginal": transform_datetime}
