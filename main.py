import ctypes
import time
import threading
import win32gui
import win32con
import win32api
import dearpygui.dearpygui as dpg
import cv2
import numpy as np
import pyautogui
import configparser
#from EditThemePlugin import EditThemePlugin
 
 
 
dpg.create_context()
 
# Vars
click_through = False
fov_radius = 25  # Default FOV radius
aimbot_speed = 5  # Default aimbot speed
scale_factor = 1.5  # Default scale factor
aim_height_offset = 0  # Default height offset for aiming
circle = None  # FOV circle
 
#window margins
class MARGINS(ctypes.Structure):
    _fields_ = [("cxLeftWidth", ctypes.c_int),
                ("cxRightWidth", ctypes.c_int),
                ("cyTopHeight", ctypes.c_int),
                ("cyBottomHeight", ctypes.c_int)]
 
#viewport
dpg.create_viewport(title='overlay', always_on_top=True, decorated=False, clear_color=[0.0, 0.0, 0.0, 0.0])
dpg.set_viewport_always_top(True)
dpg.create_context()
dpg.setup_dearpygui()
dpg.add_viewport_drawlist(front=False, tag="Viewport_back")
 
# Callback for FOV
def show_fov(sender, app_data, user_data):
    global circle, fov_radius
    fov_radius = dpg.get_value(slider1)
    if dpg.get_value(check1):
        if circle is not None:
            dpg.delete_item(circle)
        circle = dpg.draw_circle((960, 540), fov_radius, color=(255, 255, 0, 255), parent="Viewport_back")
    else:
        if circle is not None:
            dpg.delete_item(circle)
            circle = None
 
# Function to detect color within FOV area
def detect_color(speed, radius):
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
 
    # Define the center and FOV area
    screen_center_x, screen_center_y = pyautogui.size()
    screen_center_x //= 2
    screen_center_y //= 2
 
    fov_x1 = int(max(0, screen_center_x - radius))
    fov_y1 = int(max(0, screen_center_y - radius))
    fov_x2 = int(min(screen_center_x + radius, screenshot.shape[1]))
    fov_y2 = int(min(screen_center_y + radius, screenshot.shape[0]))
 
    fov_area = screenshot[fov_y1:fov_y2, fov_x1:fov_x2]
 
    # lower and upper bounds for red color
    lower_red = np.array([84, 84, 255]) - speed  # Lower bound 
    upper_red = np.array([84, 84, 255]) + speed  # Upper bound 
    mask = cv2.inRange(fov_area, lower_red, upper_red)
    mask = cv2.blur(mask, (5, 5))  # Apply slight blurring
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        # Get the bounding rectangle of the contour
        x, y, w, h = cv2.boundingRect(max_contour)
        # Calculate center 
        x_center = x + w // 2 + fov_x1
        y_center = y + h // 2 + fov_y1
        return x_center, y_center
    return None, None
 
# Direct Input Injection
def direct_input_move(x_diff, y_diff):
    global scale_factor
    x_diff *= scale_factor
    y_diff *= scale_factor
 
    # mouse movement
    MOUSEEVENTF_MOVE = 0x0001
    # Structure for mouse input
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long),
                    ("dy", ctypes.c_long),
                    ("mouseData", ctypes.c_ulong),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
    # structure
    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong),
                    ("mi", MOUSEINPUT)]
    #mouse input structure
    mi = MOUSEINPUT(int(x_diff), int(y_diff), 0, MOUSEEVENTF_MOVE, 0, None)
    # Create input structure
    inp = INPUT(0, mi)
    # Send input
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
 
# Aimbot 
def aimbot():
    global fov_radius, aimbot_speed, aim_height_offset
    while True:
        if win32api.GetAsyncKeyState(win32con.VK_XBUTTON1) < 0:
            x, y = detect_color(aimbot_speed, fov_radius)
            if x is not None and y is not None:
                screen_width, screen_height = pyautogui.size()
                x_diff = x - screen_width // 2
                y_diff = y - screen_height // 2 + aim_height_offset
 
                
                direct_input_move(x_diff, y_diff)
 
            time.sleep(0.01)  # sleep time for smoother movement
 
#  thread 
aimbot_thread = threading.Thread(target=aimbot)
aimbot_thread.daemon = True
aimbot_thread.start()
 
# update aimbot speed
def update_speed(sender, app_data, user_data):
    global aimbot_speed
    aimbot_speed = app_data
 
# update scale factor
def update_scale_factor(sender, app_data, user_data):
    global scale_factor
    scale_factor = app_data
 
#  update aiming height offset
def update_aim_height_offset(sender, app_data, user_data):
    global aim_height_offset
    aim_height_offset = app_data
	
 
# Gui window setup
with dpg.window(label="test", width=200, height=400):
    check1 = dpg.add_checkbox(label="Show Fov", callback=show_fov)
    slider1 = dpg.add_slider_float(label="Fov", min_value=25, max_value=150, default_value=25, callback=show_fov)
    slider2 = dpg.add_slider_float(label="Aimbot Speed", min_value=1, max_value=20, default_value=5, callback=update_speed)
    slider3 = dpg.add_slider_float(label="Scale Factor", min_value=1, max_value=5, default_value=1.5, callback=update_scale_factor)
    slider4 = dpg.add_slider_float(label="Aim Height Offset", min_value=-100, max_value=100, default_value=0, callback=update_aim_height_offset)
    dpg.add_text("button")
    dpg.add_button(tag="nothing", label="does literally nothing")
 
#trying to add color to menu making it grey with green sliders
    
 
# Gui viewport
dpg.show_viewport()
dpg.toggle_viewport_fullscreen()
 
# window properties
hwnd = win32gui.FindWindow(None, "overlay")
margins = MARGINS(-1, -1, -1, -1)
ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, margins)
 
count2 = 0
 
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()
    if win32api.GetAsyncKeyState(ord('Q')):  # Check for Q key press
        count2 += 1
    while win32api.GetAsyncKeyState(ord('Q')):
        pass
    if count2 == 1:
        click_through = True
    if count2 == 2:
        click_through = False
    if count2 == 3:
        count2 -= 2
    if click_through:
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
    else:
        win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 0)
 
# Destroy Gui context
dpg.destroy_context()