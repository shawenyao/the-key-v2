import hid
import struct
import time
import asyncio
from datetime import date
from winrt.windows.ui.notifications.management import UserNotificationListener
from winrt.windows.ui.notifications import NotificationKinds

# HID device path
# use hid.enumerate() to figure out
PATH = b'\\\\?\\HID#VID_FEED&PID_6070&MI_01#7&36c4d81a&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}'

# constants
CMD_VIA_LIGHTING_SET_VALUE = 0x07
VIALRGB_SET_MODE = 0x41
QMK_RGBLIGHT_BRIGHTNESS = 0x80
QMK_RGBLIGHT_EFFECT = 0x81
QMK_RGBLIGHT_COLOR = 0x83
MSG_LEN = 32
# default color depending on day of the week
COLOR_BY_DAY_OF_WEEK = {
    0: [0, 255], # red
    1: [30, 255], # yellow
    2: [80, 255], # green
    3: [140, 255], # light blue
    4: [170, 255], # blue
    5: [220, 255], # purple
    6: [0, 0] # white
}

# helper functions
def change_rgb_mode(mode):
    msg = struct.pack(">BBB", CMD_VIA_LIGHTING_SET_VALUE, QMK_RGBLIGHT_EFFECT, mode)
    return(msg)

def change_rgb_color(h, s):
    msg = struct.pack(">BBBB", CMD_VIA_LIGHTING_SET_VALUE, QMK_RGBLIGHT_COLOR, h, s)
    return(msg)

def format_msg(msg):
    msg += b"\x00" * (MSG_LEN - len(msg))
    return(msg)

def send_msg(msg):
    msg_long = format_msg(msg)
    dev = hid.Device(path=PATH)
    dev.write(b"\x00" + msg_long)
    dev.close()

def change_notification_mode(on):
    if on:
        mode = 14 # Rainbow Swirl
    else:
        mode = 2 # Breathing
    send_msg(change_rgb_mode(mode))

def change_color_by_day_of_week(day_of_week):
    h = COLOR_BY_DAY_OF_WEEK[day_of_week][0]
    s = COLOR_BY_DAY_OF_WEEK[day_of_week][1]
    send_msg(change_rgb_color(h=h, s=s))

async def control_leds():
    # turn off notification mode
    notification_mode = False
    change_notification_mode(on=notification_mode)
    # set default color based on day of the week (0 to 6)
    change_color_by_day_of_week(date.today().weekday())

    while True:
        # check status update every 1 second
        time.sleep(1)
        
        # ask Windows about the system notifications
        listener = UserNotificationListener.get_current()
        notifications = await listener.get_notifications_async(NotificationKinds.TOAST)

        # if there is at least one notification and the LED is not in notification mode
        if len(notifications) >= 1 and notification_mode == False:
            # turn on notification mode
            notification_mode = True
            change_notification_mode(on=notification_mode)            
        # if there isn't any notification and the LED is in notification mode
        elif len(notifications) == 0 and notification_mode == True:
            # turn off notification mode
            notification_mode = False
            change_notification_mode(on=notification_mode)

if __name__ == '__main__':
    asyncio.run(control_leds())
