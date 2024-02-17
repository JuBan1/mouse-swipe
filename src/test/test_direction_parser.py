import unittest

from direction_parser import parse_directions
from direction import Direction

class TestParser(unittest.TestCase):

    def test_direction_parser(self):
        self.assertEqual(parse_directions("swipe_left"), [Direction.swipe_left])
        self.assertEqual(parse_directions("swipe_left,swipe_right"), [Direction.swipe_left, Direction.swipe_right])
        self.assertEqual(parse_directions("swipe_left,     swipe_right"), [Direction.swipe_left, Direction.swipe_right])
        self.assertEqual(parse_directions("swipe_left, swipe_right, swipe_left"), [Direction.swipe_left, Direction.swipe_right, Direction.swipe_left])

        self.assertRaises(KeyError, parse_directions, "swipe_around")
        self.assertRaises(KeyError, parse_directions, "swipe_left swipe_around")
        self.assertRaises(KeyError, parse_directions, "")
        self.assertRaises(ValueError, parse_directions, "swipe_left, swipe_left") # consecutive swipes aren't okay

if __name__ == '__main__':
    unittest.main()
