from smoketest import SmokeTest
from .models import User


class DBConnectivity(SmokeTest):
    def test_retrieve(self):
        cnt = User.objects.all().count()
        self.assertTrue(cnt > 0)
