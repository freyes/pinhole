from pinhole.common.app import db


class BaseTest(object):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.drop_all()
