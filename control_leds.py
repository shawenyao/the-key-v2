import hid
import struct
import time
import asyncio
from winrt.windows.ui.notifications.management import UserNotificationListener
from winrt.windows.ui.notifications import NotificationKinds

# hid device path
# use hid.enumerate() to figure out
PATH = b'\\\\?\\HID#VID_FEED&PID_6070&MI_01#7&36c4d81a&0&0000#{4d1e55b2-f16f-11cf-88cb-001111000030}'

# constants
CMD_VIA_LIGHTING_SET_VALUE = 0x07
VIALRGB_SET_MODE = 0x41
QMK_RGBLIGHT_BRIGHTNESS = 0x80
QMK_RGBLIGHT_EFFECT = 0x81
QMK_RGBLIGHT_COLOR = 0x83
MSG_LEN = 32

# helper functions
def change_rgb_mode(mode):
    msg = struct.pack(">BBB", CMD_VIA_LIGHTING_SET_VALUE, QMK_RGBLIGHT_EFFECT, mode)
    return(msg)

def format_msg(msg):
    msg += b"\x00" * (MSG_LEN - len(msg))
    return(msg)

def send_msg(dev, msg):
    dev.write(b"\x00" + msg)

def change_notification_mode(on):
    if on:
        mode = 14
    else:
        mode = 2
    
    dev = hid.Device(path=PATH)
    msg = format_msg(change_rgb_mode(mode))
    send_msg(dev, msg)
    dev.close()

async def control_leds():
    # turn off notification mode
    notification_mode = False
    change_notification_mode(on=notification_mode)

    while True:
        time.sleep(1)
            
        listener = UserNotificationListener.get_current()
        notifications = await listener.get_notifications_async(NotificationKinds.TOAST)

        # if there is any notification and the LED is not in notification mode
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
