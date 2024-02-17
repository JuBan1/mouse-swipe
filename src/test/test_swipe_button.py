import unittest
import sys
import os

from swipe_button import SwipeButton
from direction import Direction
from gesture import Gesture

class TestParser(unittest.TestCase):

    def test_backwards_compat(self):
        sb = SwipeButton("button", [Gesture([Direction.swipe_right], ['KEY_A'])])
        self.assertEquals(sb.swipe_right, ['KEY_A'])
        self.assertEquals(sb.swipe_left, [])

    def test_find_gesture(self):
        gestures = [
            Gesture([Direction.swipe_right], ['KEY_A']),
            Gesture([Direction.swipe_right, Direction.swipe_left], ['KEY_B']),
            Gesture([Direction.swipe_left], ['KEY_C']),
        ]
        sb = SwipeButton("button", gestures)
        self.assertEquals(sb.find_for_swipes(gestures[0].swipes), gestures[0])
        self.assertEquals(sb.find_for_swipes(gestures[1].swipes), gestures[1])
        self.assertEquals(sb.find_for_swipes(gestures[2].swipes), gestures[2])
        self.assertEquals(sb.find_for_swipes([Direction.swipe_down]), None)

if __name__ == '__main__':
    unittest.main()
