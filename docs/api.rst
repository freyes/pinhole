API
===

Photo Management
----------------


.. http:get:: /api/v1/photos

   Get photos

   :query tags: filter photos by tag or list of tags
   :statuscode 200: no error
   :statuscode 401: unauthorized, authentication required
   :statuscode 404: no photos found

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/photos?tags=[foo,bar] HTTP/1.1
      Host: example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: text/javascript

      [
        {
          "uuid": "f1b9563e-1d32-11e2-ba71-ec55f9c63c9a",
          "timestamp": "2013-12-3123:59:59Z",
          "url": "http://pinhole.s3.amazonws.com/user/abcd/original.jpg",
          "tags": ["foo", "bar"],
          "exif": {"colorspace": "2",
                   "ApertureValue": "325770/65536",
                   "ColorSpace": "1",
                   "ComponentsConfiguration": "1, 2, 3, 0",
                   "Compression": "6",
                   "CustomRendered": "0",
                   "DateTime": "2012:10:24 22:08:14",
                   "DateTimeDigitized": "2012:10:24 22:08:14",
                   "DateTimeOriginal": "2012:10:24 22:08:14",
                   "ExifImageLength": "2304",
                   "ExifImageWidth": "3456",
                   "ExifOffset": "196",
                   "ExifVersion": "48, 50, 50, 49",
                   "ExposureBiasValue": "0/2"}
        }
      ]

.. http:get:: /api/v1/photo/(str:uuid)

   :statuscode 200: no error
   :statuscode 401: unauthorized, authentication required
   :statuscode 404: no photos found

   **Example request**:

   .. sourcecode:: http

      GET /api/v1/photo/f1b9563e-1d32-11e2-ba71-ec55f9c63c9a HTTP/1.1
      Host: example.com
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: text/javascript

      {
        "uuid": "f1b9563e-1d32-11e2-ba71-ec55f9c63c9a",
        "timestamp": "2013-12-3123:59:59Z",
        "url": "http://pinhole.s3.amazonws.com/user/abcd/original.jpg",
        "tags": ["foo", "bar"],
        "exif": {"colorspace": "2",
                 "ApertureValue": "325770/65536",
                 "ColorSpace": "1",
                 "ComponentsConfiguration": "1, 2, 3, 0",
                 "Compression": "6",
                 "CustomRendered": "0",
                 "DateTime": "2012:10:24 22:08:14",
                 "DateTimeDigitized": "2012:10:24 22:08:14",
                 "DateTimeOriginal": "2012:10:24 22:08:14",
                 "ExifImageLength": "2304",
                 "ExifImageWidth": "3456",
                 "ExifOffset": "196",
                 "ExifVersion": "48, 50, 50, 49",
                 "ExposureBiasValue": "0/2"}
      }

.. http:post:: /api/v1/photo

.. http:post:: /api/v1/photos

   Massive photo uploading

.. http:put:: /api/v1/photo/(str:uuid)

.. http:delete:: /api/v1/photo/(str:uuid)


Data Types
----------

+-----------+---------+-------+---------------------+
| Name      | Format  | Notes | Example             |
+===========+=========+=======+=====================+
| timestamp | ISO8601 |       | 2013-12-3123:59:59Z |
+-----------+---------+-------+---------------------+
