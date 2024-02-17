import unittest

from direction import Direction
from swipe_recognizer import SwipeRecognizer

class TestParser(unittest.TestCase):

    def test_large_steps(self):
        self.assertEqual(swipe(10, 0), [Direction.swipe_right])
        self.assertEqual(swipe(0, 10), [Direction.swipe_down])
        self.assertEqual(swipe(-10, 0), [Direction.swipe_left])
        self.assertEqual(swipe(0, -10), [Direction.swipe_up])
        self.assertEqual(swipe(10, 0, -10, 0), [Direction.swipe_right, Direction.swipe_left])

    def test_accuracy(self):
        # accuracy is X degrees +/- in either direction of the optimal value.
        self.assertEqual(swipe(5, -2), [])
        self.assertEqual(swipe(5, -1), [Direction.swipe_right])
        self.assertEqual(swipe(5, 0), [Direction.swipe_right])
        self.assertEqual(swipe(5, 1), [Direction.swipe_right])
        self.assertEqual(swipe(5, 2), [])
        self.assertEqual(swipe(5, 3), [])
        self.assertEqual(swipe(5, 4), [Direction.swipe_down_right])
        self.assertEqual(swipe(5, 5), [Direction.swipe_down_right])

        # swiping down is interesting because it's right at 0 degrees, meaning
        # the number wraps aroundat that point.
        self.assertEqual(swipe(-2, 5), [])
        self.assertEqual(swipe(-1, 5), [Direction.swipe_down])
        self.assertEqual(swipe(0, 5), [Direction.swipe_down])
        self.assertEqual(swipe(1, 5), [Direction.swipe_down])
        self.assertEqual(swipe(2, 5), [])

    def test_granularity(self):
        self.assertEqual(swipe(3, 0), [])
        self.assertEqual(swipe(3, 0, 3, 0), [Direction.swipe_right])
        self.assertEqual(swipe(3, 0, -3, 0), [])
        self.assertEqual(swipe(3, 0, -3, 0, -3, 0, -3, 0), [Direction.swipe_left])

    def test_swipe_conflation(self):
        self.assertEqual(swipe(5, 0, 5, 0), [Direction.swipe_right])

# "moves the mouse" a little bit in some direction. Supply pairs of x,y coordinates.
# Returns the list of swipe directions recognized
def swipe(*coords):
    listt = list(zip(coords[::2],coords[1::2]))
    pairs = [[x,y] for x,y in listt]

    sr = SwipeRecognizer()
    for pair in pairs:
        print("Swipe x={}, y={}".format(pair[0], pair[1]))
        sr.update(pair[0], pair[1])
    return sr.swipes()

if __name__ == '__main__':
    unittest.main()
