from pinhole.common.app import db


class BaseTest(object):
    def setUp(self):
        try:
            db.drop_all()
        except:
            pass
        db.create_all()

    def tearDown(self):
        db.drop_all()
