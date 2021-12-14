import time
import unittest2 as unittest

from lib.utils import timeout, util


class UtilTest(unittest.TestCase):
    def test_get_value_from_dict(self):
        value = {"a": 123, "b": "8.9", "c": "abc"}

        self.assertEqual(
            util.get_value_from_dict(value, "a"),
            123,
            "get_value_from_dict did not return the expected result",
        )
        self.assertEqual(
            util.get_value_from_dict(value, ("b",), return_type=float),
            8.9,
            "get_value_from_dict did not return the expected result",
        )
        self.assertEqual(
            util.get_value_from_dict(
                value, "c", default_value="default", return_type=int
            ),
            "default",
            "get_value_from_dict did not return the expected result",
        )
        self.assertEqual(
            util.get_value_from_dict(value, "d", default_value="default"),
            "default",
            "get_value_from_dict did not return the expected result",
        )
        self.assertEqual(
            util.get_value_from_dict(
                value, ("unknown1", "unknown2", "b"), default_value="default"
            ),
            "8.9",
            "get_value_from_dict did not return the expected result",
        )

    def test_cached(self):
        def tester(arg1, arg2, sleep):
            time.sleep(sleep)
            return arg1 + arg2

        tester = util.cached(tester, ttl=5.0)

        tester(1, 2, 0.2)
        tester(2, 2, 0.2)
        tester(3, 2, 0.2)

        tester = timeout.call_with_timeout(tester, 0.1)
        self.assertEqual(3, tester(1, 2, 0.2))
        self.assertEqual(4, tester(2, 2, 0.2))
        self.assertEqual(5, tester(3, 2, 0.2))
        self.assertRaises(timeout.TimeoutException, tester, 1, 2, 5)
