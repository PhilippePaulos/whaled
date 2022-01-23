from datetime import datetime
from unittest import TestCase

from dex_trades import ScanScrapper


class ScanScrapperTest(TestCase):

    def test_parse_time_ago(self):
        time_checks = {
            "1 sec ago": "2012-10-03 10:03:59",
            "30 secs ago": "2012-10-03 10:03:30",
            "1 min ago": "2012-10-03 10:03:00",
            "4 mins ago": "2012-10-03 10:00:00",
            "2 hrs ago": "2012-10-03 08:04:00",
            "1 hr ago": "2012-10-03 09:04:00",
            "1 hr 4 mins ago": "2012-10-03 09:00:00",
            "1 hr 1 min ago": "2012-10-03 09:03:00",
            "2 hrs 1 min ago": "2012-10-03 08:03:00",
            "2 hrs 4 mins ago": "2012-10-03 08:00:00",
            "1 day 1 min ago": "2012-10-02 10:03:00",
            "1 day 4 mins ago": "2012-10-02 10:00:00",
            "2 days 1 min ago": "2012-10-01 10:03:00",
            "2 days 4 mins ago": "2012-10-01 10:00:00",
            "1 day 1 hr ago": "2012-10-02 09:04:00",
            "1 day 2 hrs ago": "2012-10-02 08:04:00",
        }
        date = datetime.fromisoformat("2012-10-03 10:04:00")
        for time_ago_str, expected_date in time_checks.items():
            time = ScanScrapper.parse_time_ago(date, time_ago_str)
            self.assertTrue(time.__str__() == expected_date)
