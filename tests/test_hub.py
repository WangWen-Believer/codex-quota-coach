import unittest

from quota_coach.hub import is_authorized


class HubAuthorizationTest(unittest.TestCase):
    def test_allows_requests_when_token_is_not_configured(self):
        self.assertTrue(is_authorized({}, None))

    def test_accepts_bearer_token(self):
        self.assertTrue(is_authorized({"Authorization": "Bearer secret"}, "secret"))

    def test_accepts_x_quota_token(self):
        self.assertTrue(is_authorized({"X-Quota-Token": "secret"}, "secret"))

    def test_rejects_missing_or_wrong_token(self):
        self.assertFalse(is_authorized({}, "secret"))
        self.assertFalse(is_authorized({"Authorization": "Bearer wrong"}, "secret"))


if __name__ == "__main__":
    unittest.main()
