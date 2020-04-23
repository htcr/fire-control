import threading
import time
from pynput import mouse
from pynput import keyboard
import pyautogui
import ctypes

kFireLoopInterval = 0.01
kFireIntervalCount = 12
kFireKeys = ['1', '2', '3']

activated = False
firing = False
current_fire_key = 0
waited_intervals = 0

#####

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions
def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

#####

#define DIK_1               0x02
#define DIK_2               0x03
#define DIK_3               0x04


scancode_map = {
'1': 0x02,
'2': 0x03,
'3': 0x04
}

def FireLoop():
	global firing
	global current_fire_key
	global waited_intervals
	while True:
		if firing:
			if waited_intervals == 0:
				print('Fire {}'.format(kFireKeys[current_fire_key]))
				# pyautogui.press(kFireKeys[current_fire_key])
				PressKey(scancode_map[kFireKeys[current_fire_key]])
				#ReleaseKey(scancode_map[kFireKeys[current_fire_key]])
				#current_fire_key = (current_fire_key + 1) % len(kFireKeys)
				waited_intervals += 1
			else:
				if waited_intervals == kFireIntervalCount - 1:
					waited_intervals = 0
				else:
					if waited_intervals == 1:
						ReleaseKey(scancode_map[kFireKeys[current_fire_key]])
						current_fire_key = (current_fire_key + 1) % len(kFireKeys)
					waited_intervals += 1
		else:
			if current_fire_key != 0:
				current_fire_key = 0
			if waited_intervals != 0:
				waited_intervals = 0
			for fire_key in kFireKeys:
				ReleaseKey(scancode_map[fire_key])
		time.sleep(kFireLoopInterval)

def on_click(x, y, button, pressed):
	global activated
	global firing
	if not activated:
		return
	print('on click')
	if button == mouse.Button.left:
		if pressed:
			firing = True
		else:
			firing = False

def on_press(key):
	global activated
	if hasattr(key, 'char') and key.char == 'i':
		activated = True if not activated else False

print('start key listener')
key_listener = keyboard.Listener(
    on_press=on_press)
key_listener.start()

print('start mouse listener')
listener = mouse.Listener(on_click=on_click)
listener.start()

print('start fire loop')
fire_thread = threading.Thread(target=FireLoop, name='fire_loop')
fire_thread.start()

key_listener.join()
fire_thread.join()
listener.join()