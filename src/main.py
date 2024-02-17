#!/usr/bin/python3

import asyncio, copy, logging, sys
from evdev import InputDevice, ecodes, list_devices
from systemd.journal import JournalHandler
from virtual_device import create_virtual_device, remove_virtual_device
import configparser

from mouse import Mouse
from config_parser import parse_config
from swipe_recognizer import SwipeRecognizer

config_file_location = "/etc/mouse-swipe.conf"


def get_mouses():
    logger.info("Searching for mouses..")

    global number_of_devices

    input_devices = [InputDevice(path) for path in list_devices()]
    number_of_devices = len(input_devices)
    mouses.clear()

    for input_device in input_devices:
        if input_device.name == "mouse-swipe-virtual-device":
            continue

        try:
            keys = input_device.capabilities(verbose=True)[("EV_KEY", 1)]
        except:
            continue

        if ("BTN_RIGHT", 273) in keys:
            logger.info("Mouse found: " + input_device.name)
            mouse = Mouse(input_device.name)
            mouse.input_device = input_device
            mouse.swipe_buttons = copy.deepcopy(config_swipe_buttons)
            mouse.input_device.grab()
            mouses.append(mouse)
            tasks.append(asyncio.create_task(task_handle_mouse_events(mouse)))

def ungrab_mouses():
    for mouse in mouses:
        try:
            if mouse.input_device:
                mouse.input_device.ungrab()
        except:
            pass

def emulate_event(type, code, value):
    virtual_device.write(type, code, value)
    virtual_device.syn()

def emulate_key_press(keys):
    for key in keys:
        virtual_device.write(ecodes.EV_KEY, ecodes.ecodes[key], 1)
        virtual_device.syn()

    for key in reversed(keys):
        virtual_device.write(ecodes.EV_KEY, ecodes.ecodes[key], 0)
        virtual_device.syn()


async def task_handle_mouse_events(mouse):
    sr = SwipeRecognizer()

    async for event in mouse.input_device.async_read_loop():
        should_forward = True

        if event.type == ecodes.EV_REL:
            for swipe_button in mouse.swipe_buttons:
                if swipe_button.pressed:
                    if swipe_button.freeze:
                        should_forward = False

                    if event.code == ecodes.REL_X:
                        swipe_button.deltaX += event.value
                        sr.update(event.value, 0)

                        if swipe_button.scroll and abs(swipe_button.deltaX) > 5:
                            emulate_event(ecodes.EV_REL, ecodes.REL_HWHEEL, 1 if swipe_button.deltaX > 0 else -1)
                            swipe_button.deltaX = 0
                    else:
                        swipe_button.deltaY += event.value
                        sr.update(0, event.value)

                        if swipe_button.scroll and abs(swipe_button.deltaY) > 5:
                            emulate_event(ecodes.EV_REL, ecodes.REL_WHEEL, -1 if swipe_button.deltaY > 0 else 1)
                            swipe_button.deltaY = 0
        elif event.type == ecodes.EV_KEY:
            for swipe_button in mouse.swipe_buttons:
                if event.code == ecodes.ecodes[swipe_button.button]:
                    should_forward = False
                    swipe_button.pressed = event.value

                    absDeltaX = abs(swipe_button.deltaX)
                    absDeltaY = abs(swipe_button.deltaY)

                    if not(swipe_button.pressed):
                        if len(sr.swipes()) == 0:
                            emulate_key_press(swipe_button.click)
                            print("Gesture finished. No swipes.")
                        else:
                            gesture = swipe_button.find_for_swipes(sr.swipes())
                            print("Finished with gestures={} due to swipes={}".format(gesture, sr.swipes()))
                            if gesture != None:
                                emulate_key_press(gesture.commands)

                        sr = SwipeRecognizer()
                        swipe_button.deltaX = 0
                        swipe_button.deltaY = 0
            
        if should_forward:
            emulate_event(event.type, event.code, event.value)

async def task_detect_new_devices():
    while True:
        await asyncio.sleep(5)
        if len(list_devices()) > number_of_devices:
            # Cancel this task to trigger the cancelling of all tasks on gather
            tasks[0].cancel()
  
def cancel_tasks():
    for task in tasks:
        try:
            if not(task.done()) and not(task.cancelled()):
                task.cancel()
        except:
            pass

    for task in tasks:
        try:
            task.result()
        except:
            pass

async def run_tasks():
    try:            
        tasks.clear()
        tasks.append(asyncio.create_task(task_detect_new_devices()))
        get_mouses()
        await asyncio.gather(*tasks)
    except:
        pass
    finally:
        ungrab_mouses()
        cancel_tasks()

if __name__ == "__main__":
    mouses, tasks = [], []

    try:
        logger = logging.getLogger('mouse-swipe')
        logger.addHandler(JournalHandler())
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.INFO)
    except BaseException as e:
        print(e)
        quit()
        


    try:
        virtual_device = create_virtual_device()

        config = configparser.ConfigParser()
        config.read(config_file_location)
        config_swipe_buttons = parse_config(config)
    except Exception as e:
        logger.info(e)
        quit()

    while True:
        try:
            print("Run..")
            asyncio.run(run_tasks())
        except:
            print("Exiting..")
            break

    remove_virtual_device(virtual_device)
