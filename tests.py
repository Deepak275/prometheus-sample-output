from unittest import TestCase
from app import check_url, uptime_check, parse_arguments


class TestUpTimeCheck(TestCase):

    up_url = "https://httpstat.us/200"

    down_url = "https://httpstat.us/503"
    timeout_url = "http://www.google.com:81"

    def test_parse_arguments(self):
        """
        """
        self.assertEqual(parse_arguments([]), 1, "Expect default delay to be 1 second.")

        self.assertEqual(parse_arguments(["5"]), 5, "User specified 5-second delay.")

    def assert_response_time(self, response_time):
        """Asserts if the response time is between 0 and 10 seconds.
        """
        # Response time should be between 0-10 seconds
        self.assertGreater(response_time, 0, "Response time should be greater than 0.")
        self.assertLess(response_time, 10000, "Response time should be less than 10,000")

    def test_check_url(self):
        """Tests the check_url function
        """
        # Check a URL that is UP
        status, response_time  = check_url(self.up_url)
        self.assertEqual(status, 1, "check_url() should return status 1 when URL is up.")
        self.assert_response_time(response_time)

        # Check a URL that is down
        status, response_time  = check_url(self.down_url)
        self.assertEqual(status, 0, "check_url() should return status 0 when URL is down.")
        self.assert_response_time(response_time)

        # Check a URL that trigger timeout
        status, response_time = check_url(self.timeout_url)
        self.assertEqual(status, 0, "check_url() should return 0 when timeout.")
        self.assertGreater(response_time, 10000)

    def test_uptime_check(self):
        url_status = uptime_check()
        self.assertEqual(len(url_status), 2, "uptime_check() should check 2 URLs.")
        self.assertIn(self.up_url, url_status)
        self.assertIn(self.down_url, url_status)
        self.assertEqual(url_status[self.up_url], 1)
        self.assertEqual(url_status[self.down_url], 0)
