import pyautogui
import time
import keyboard
from tkinter import Tk, Label
from PIL import Image
import pytesseract
import threading
import os
import sys
import win32gui
import win32con


# TESSERACT INSTALL DIRECTORY
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

textX = 1735
textY = 260
dallX = 1945
dallY = 260
neutralclickX = 1280
neutralclickY = 715

# Calculate bottom right corner coordinates
overlay_width = 200  # Adjust the width of your overlay
overlay_height = 120  # Adjust the height of your overlay
bottom_right_x = 2560 - overlay_width
bottom_right_y = 1440 - overlay_height

# Initialize the status of each hotkey
fStatus = "Inactive"
gStatus = "Inactive"
nStatus = "Inactive"
mStatus = "Inactive"

# Variable to track whether the script is paused
script_paused = False

# Create the overlay window
overlay = Tk()
overlay.overrideredirect(True)
overlay.attributes('-topmost', True)
overlay.wm_attributes('-transparentcolor', 'white')
overlay.title("Welcome to autofarmer")

# Set the overlay position
overlay.update_idletasks()  # Make sure geometry method works correctly
overlay_width = overlay.winfo_width()
overlay_height = overlay.winfo_height()
offset_x = 200  # Adjust the offset value as needed
bottom_right_x = 2560 - overlay_width - offset_x
bottom_right_y = 1440 - overlay_height
overlay.geometry('+{}+{}'.format(bottom_right_x, bottom_right_y))

# Initialize the timers
timers = {"FarmMejos": None, "FarmNarcos": None, "FarmFlint": None, "FarmMetal": None}

# Initialize the image variable
def capture_screenshot():
    # Capture a screenshot with higher quality
    screenshot = pyautogui.screenshot()

    # Define the coordinates of the region to capture
    region_left = 85
    region_top = 1305
    region_right = 600
    region_bottom = 1335

    # Ensure the region coordinates are within the bounds of the original screenshot
    region_left = max(0, min(region_left, screenshot.width - 1))
    region_top = max(0, min(region_top, screenshot.height - 1))
    region_right = max(region_left + 1, min(region_right, screenshot.width))
    region_bottom = max(region_top + 1, min(region_bottom, screenshot.height))

    # Crop the screenshot to the specified coordinates
    region = screenshot.crop((region_left, region_top, region_right, region_bottom))

    # Save the cropped region for reference (optional)
    region.save('CroppedGlobal.png')

    return region

def update_overlay():
    # Update the text labels based on the current status
    f_label.config(text=f'FLINT CTRL+F {fStatus}')
    g_label.config(text=f'METAL CTRL+G {gStatus}')
    n_label.config(text=f'NARCOS CTRL+N {nStatus}')
    m_label.config(text=f'MEJOS CTRL+M {mStatus}')
    pause_label.config(text='PAUSE SCRIPT F8')
    kill_label.config(text='KILL SCRIPT F9')

    # You can add additional logic here to update other elements in the overlay

    # Refresh the overlay
    overlay.update()

# Function to check if a black box is detected at the specified coordinates
def check_for_black_box():
    return pyautogui.pixelMatchesColor(2290, 80, (0, 0, 0)) and pyautogui.pixelMatchesColor(2330, 110, (0, 0, 0))


# Hotkey definitions
def toggle_loop(status_var, label_name, farm_function):
    global fStatus, gStatus, nStatus, mStatus, timers, script_paused
    # If the script is paused, set the status to "Paused"
    if script_paused:
        globals()[status_var] = "Paused"
    else:
        # Toggle the loop status
        globals()[status_var] = "Inactive" if globals()[status_var] == "Active" else "Active"
        # If the status is now inactive, stop the loop
        if globals()[status_var] == "Inactive":
            if timers[label_name] is not None:
                timers[label_name]['stop'] = True
                timers[label_name]['thread'].join()
                timers[label_name] = None  # Set the timer to None after joining
        else:
            # If the timer doesn't exist or has finished, create a new one
            if timers[label_name] is None or not timers[label_name]['thread'].is_alive():
                timers[label_name] = {"thread": threading.Thread(target=farm_function), "stop": False}
                timers[label_name]["thread"].start()
            else:
                # If the timer is still active, do nothing (it's already running)
                pass

    # Update the overlay
    update_overlay()

def reload_script():
    python_exe = sys.executable
    script_path = os.path.abspath(__file__)
    os.execl(python_exe, python_exe, script_path)

    # Bring the ArkAscended window to the front after reloading
    bring_ark_window_to_front()

def bring_ark_window_to_front():
    ark_window = win32gui.FindWindow(None, 'ArkAscended')
    if ark_window:
        win32gui.ShowWindow(ark_window, win32con.SW_RESTORE)  # Restore the window if minimized
        win32gui.SetForegroundWindow(ark_window)  # Bring the window to the front

def kill_script():
    global overlay
    overlay.destroy()
    sys.exit()

def toggle_pause():
    global script_paused
    script_paused = not script_paused
    update_overlay()

    if script_paused:
        # If the script is paused, stop all active loops
        for label_name, status_var, _ in [('FarmMejos', 'mStatus', farm_mejos),
                                          ('FarmNarcos', 'nStatus', farm_narcos),
                                          ('FarmFlint', 'fStatus', farm_flint),
                                          ('FarmMetal', 'gStatus', farm_metal)]:
            if globals()[status_var] == "Active":
                timers[label_name]['stop'] = True
                timers[label_name]['thread'].join()
                timers[label_name] = None
    else:
        # If the script is unpaused, resume the loops
        for label_name, status_var, farm_function in [('FarmMejos', 'mStatus', farm_mejos),
                                                     ('FarmNarcos', 'nStatus', farm_narcos),
                                                     ('FarmFlint', 'fStatus', farm_flint),
                                                     ('FarmMetal', 'gStatus', farm_metal)]:
            if globals()[status_var] == "Active":
                timers[label_name] = {"thread": threading.Thread(target=farm_function), "stop": False}
                timers[label_name]["thread"].start()

# GUI Elements
welcome_label = Label(overlay, text="ARK AUTOFARMER")
welcome_label.pack()
f_label = Label(overlay, text=f'FLINT CTRL+F {fStatus}')
f_label.pack()
g_label = Label(overlay, text=f'METAL CTRL+G {gStatus}')
g_label.pack()
n_label = Label(overlay, text=f'NARCOS CTRL+N {nStatus}')
n_label.pack()
m_label = Label(overlay, text=f'MEJOS CTRL+M {mStatus}')
m_label.pack()
reload_label = Label(overlay, text='RELOAD SCRIPT F5')
reload_label.pack()
pause_label = Label(overlay, text='PAUSE SCRIPT F8')
pause_label.pack()
kill_label = Label(overlay, text='KILL SCRIPT F9')
kill_label.pack()

# Set a flag to indicate when the overlay needs to be refreshed
overlay_needs_refresh = False

# Set a timer to unfocus after a short delay
def unfocus_overlay():
    overlay.attributes('-topmost', 0)
    overlay.after(10, restore_focus)

# Restore focus to the overlay
def restore_focus():
    overlay.attributes('-topmost', 1)

# Function to mark the overlay for refresh
def mark_overlay_for_refresh():
    global overlay_needs_refresh
    overlay_needs_refresh = True

# Set a timer to refresh overlay
def refresh_overlay():
    if overlay_needs_refresh:
        update_overlay()
        overlay_needs_refresh = False
    overlay.after(500, refresh_overlay)

keyboard.add_hotkey('ctrl+m', lambda: toggle_loop('mStatus', 'FarmMejos', farm_mejos))
keyboard.add_hotkey('ctrl+n', lambda: toggle_loop('nStatus', 'FarmNarcos', farm_narcos))
keyboard.add_hotkey('ctrl+f', lambda: toggle_loop('fStatus', 'FarmFlint', farm_flint))
keyboard.add_hotkey('ctrl+g', lambda: toggle_loop('gStatus', 'FarmMetal', farm_metal))
keyboard.add_hotkey('f5', reload_script)
keyboard.add_hotkey('f8', toggle_pause)
keyboard.add_hotkey('f9', kill_script)

# Farm Mejos
def farm_mejos():
    global mStatus, script_paused
    while mStatus == "Active" and not script_paused:
        # Infinite harvesting action until black box is detected
        while not check_for_black_box():
            # Hold down the "W" key during the click loop
            keyboard.press('w')

            pyautogui.click(button='right')
            time.sleep(0.15)

            # Release the "W" key after clicking
            keyboard.release('w')

            if mStatus == "Inactive" or script_paused:
                break

        # Check if the loop should continue
        if mStatus != "Active" or script_paused:
            break

        # Drop action
        pyautogui.press('f')
        pyautogui.click(textX, textY)
        pyautogui.press('a')
        time.sleep(0.15)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.15)
        pyautogui.click(textX, textY)
        pyautogui.press('w')
        time.sleep(0.15)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.15)
        pyautogui.click(textX, textY)
        pyautogui.press('t')
        time.sleep(0.15)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.15)
        pyautogui.click(textX, textY)
        pyautogui.press('v')
        time.sleep(0.15)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.15)
        pyautogui.press('f')

# Farm Narcos
def farm_narcos():
    global nStatus, script_paused
    while nStatus == "Active" and not script_paused:
        # Infinite harvesting action until black box is detected
        while not check_for_black_box():
            # Hold down the "W" key during the click loop
            keyboard.press('w')

            pyautogui.rightClick()
            time.sleep(0.15)

            # Release the "W" key after clicking
            keyboard.release('w')

            if nStatus == "Inactive" or script_paused:
                break

        # Check if the loop should continue
        if nStatus != "Active" or script_paused:
            break

        # Drop action
        pyautogui.press('f')
        pyautogui.click(textX, textY)
        pyautogui.press('m')
        time.sleep(0.15)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.15)
        pyautogui.click(textX, textY)
        pyautogui.write('cia')
        time.sleep(0.15)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.15)
        pyautogui.click(textX, textY)
        pyautogui.press('v')
        time.sleep(0.15)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.15)
        pyautogui.click(textX, textY)
        pyautogui.write('az')
        time.sleep(0.15)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.15)
        pyautogui.click(textX, textY)
        pyautogui.press('w')
        time.sleep(0.15)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.15)
        pyautogui.click(textX, textY)
        pyautogui.press('t')
        time.sleep(0.15)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.15)
        pyautogui.press('f')

# Farm Flint
def farm_flint():
    global fStatus, script_paused
    while fStatus == "Active" and not script_paused:
        # Infinite harvesting action until black box is detected
        while not check_for_black_box():
            pyautogui.click()
            time.sleep(0.15)
            if fStatus == "Inactive" or script_paused:
                break

        # Check if the loop should continue
        if fStatus != "Active" or script_paused:
            break

        # Drop action
        pyautogui.press('f')
        pyautogui.click(textX, textY)
        pyautogui.press('e')
        time.sleep(0.15)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.15)
        pyautogui.click(textX, textY)
        pyautogui.write('th')
        time.sleep(0.3)
        pyautogui.click(dallX, dallY)
        pyautogui.click(neutralclickX, neutralclickY)
        time.sleep(0.3)
        pyautogui.press('f')

# Farm Metal
def farm_metal():
    last_chat_state = ""  # Variable to store the last state of the chat
    current_chat_state = ""

    while gStatus == "Active" and not script_paused:
        # Harvest action
        for _ in range(5):
            pyautogui.click()
            time.sleep(0.15)
            if gStatus == "Inactive" or script_paused:
                break

        # Check if the loop should continue
        if gStatus != "Active" or script_paused:
            break

        # Drop and additional actions
        # Capture and crop screenshot
        im = capture_screenshot()

        # Save the cropped region for reference (optional)
        im.save('CroppedGlobal.png')

        # Save converted image/variable
        im.save('CroppedGlobalNew.png')
        file = "CroppedGlobalNew.png"

        # Convert image to text
        rawText = pytesseract.image_to_string(file)
        current_chat_state = rawText.replace('\n', '').upper()

        # Print the content of the image to the console for debugging purpose
        # print("Chat Content:", current_chat_state)

        # Check if the word "DROP" is present in the chat state
        if "DROP" in current_chat_state:
            # Perform drop actions
            pyautogui.press('f')
            pyautogui.click(textX, textY)
            pyautogui.write('th')
            time.sleep(0.15)
            pyautogui.click(dallX, dallY)
            pyautogui.click(neutralclickX, neutralclickY)
            time.sleep(0.15)
            pyautogui.click(textX, textY)
            pyautogui.write('s')
            time.sleep(0.15)
            pyautogui.click(dallX, dallY)
            pyautogui.click(neutralclickX, neutralclickY)
            time.sleep(0.15)
            pyautogui.click(textX, textY)
            pyautogui.write('b')
            time.sleep(0.15)
            pyautogui.click(dallX, dallY)
            pyautogui.click(neutralclickX, neutralclickY)
            time.sleep(0.15)
            pyautogui.click(textX, textY)
            pyautogui.press('w')
            time.sleep(0.15)
            pyautogui.click(dallX, dallY)
            pyautogui.press('f')
            time.sleep(0.15)

            # Perform additional actions
            keyboard.press_and_release('enter')  # Hit the ENTER key

            # Check for the word "TRIBE" in the specified coordinates
            tribe_present = False
            for _ in range(10):  # Retry up to 10 times
                time.sleep(0.5)
                tribe_region = pyautogui.screenshot(region=(60, 1345, 140, 1390))
                tribe_text = pytesseract.image_to_string(tribe_region).replace('\n', '').upper()
                if "TRIBE" in tribe_text:
                    tribe_present = True
                    break
                else:
                    keyboard.press_and_release('tab')  # Hit the TAB key for retry

            if tribe_present:
                # Input a single dot (.)
                pyautogui.write('.')
                time.sleep(0.15)
                # Hit the ENTER key using keyboard module
                keyboard.press_and_release('enter')

        # Update the last chat state
        last_chat_state = current_chat_state


# Start the GUI loop
overlay.after(10, unfocus_overlay)
overlay.after(1, bring_ark_window_to_front)  # Add this line to bring ArkAscended window to front initially
overlay.mainloop()