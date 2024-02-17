import unittest

from config_parser import parse_config
from direction import Direction
import configparser

class TestParser(unittest.TestCase):

    def test_config_parser(self):
        cfg = make_config(
            """
            [BTN_RIGHT]
            swipe_left = KEY_LEFTCTRL + KEY_LEFTALT + KEY_RIGHT
            swipe_left, swipe_right = KEY_RIGHT
            """
        )
        out = parse_config(cfg)
        self.assertEqual(len(out), 1)

        swipeButton = out[0]
        self.assertEqual(swipeButton.button, "BTN_RIGHT")

        self.assertEqual(len(swipeButton.gestures), 2)
        left_gesture = swipeButton.gestures[0]
        left_right_gesture = swipeButton.gestures[1]

        self.assertEqual(left_gesture.swipes, [Direction.swipe_left])
        self.assertEqual(left_gesture.commands, "KEY_LEFTCTRL + KEY_LEFTALT + KEY_RIGHT")

        self.assertEqual(left_right_gesture.swipes, [Direction.swipe_left, Direction.swipe_right])
        self.assertEqual(left_right_gesture.commands, "KEY_RIGHT")

    def test_dont_parse_gestures_if_scroll_is_set(self):
        cfg = make_config(
            """
            [BTN_RIGHT]
            swipe_left = KEY_LEFTCTRL
            scroll = True
            """
        )
        out = parse_config(cfg)
        self.assertEqual(len(out), 1)

        swipeButton = out[0]
        self.assertEqual(swipeButton.scroll, True)
        self.assertEqual(swipeButton.button, "BTN_RIGHT")
        self.assertEqual(len(swipeButton.gestures), 0)

    def test_wrong_keys_are_ignored(self):
        cfg = make_config(
            """
            [BTN_RIGHT]
            swipe_left = KEY_LEFTCTRL
            swipe_around = KEY_LEFTCTRL
            """
        )
        out = parse_config(cfg)
        self.assertEqual(len(out), 1)
        
        swipeButton = out[0]
        self.assertEqual(swipeButton.button, "BTN_RIGHT")
        self.assertEqual(len(swipeButton.gestures), 1)


def make_config(input):
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read_string(input)
    return config

if __name__ == '__main__':
    unittest.main()
