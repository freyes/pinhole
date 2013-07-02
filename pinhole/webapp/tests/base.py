from selwsgi import WebDriverApp
from nose.plugins.attrib import attr
from pinhole.common.app import db, application


@attr("selenium")
class BaseTestSelenium(object):
    def setUp(self):
        db.create_all()
        self.app = WebDriverApp(application())

    def tearDown(self):
        self.app.close()
        db.drop_all()
