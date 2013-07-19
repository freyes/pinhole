from webtest import TestApp
from pinhole.common.app import db, app


class BaseTest(object):
    def setUp(self):
        try:
            db.drop_all()
        except:
            pass

        db.create_all()
        self.app = TestApp(app)

    def tearDown(self):
        db.drop_all()
