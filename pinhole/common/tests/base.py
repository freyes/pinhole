from webtest import TestApp
from pinhole.common.app import db, app


class BaseTest(object):
    def setUp(self):
        try:
            db.session.rollback()
        except Exception as ex:
            print ex
        try:
            db.drop_all()
        except Exception as ex:
            print ex

        db.create_all()
        self.app = TestApp(app)

    def tearDown(self):
        try:
            db.drop_all()
        except Exception as ex:
            print ex
