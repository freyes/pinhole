from webtest import TestApp
from pinhole.common.app import db, application


class BaseTest(object):
    def setUp(self):
        db.create_all()
        self.app = TestApp(application())

    def tearDown(self):
        db.drop_all()
