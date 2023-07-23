# Import required libraries
from PIL import ImageGrab
import time
import tkinter as tk
import pyautogui
import keyboard
from threading import Thread
import math

# Global variables
TILE_SIZE = None  # Will be calculated later based on the area dimensions
TILE_OFFSET = None  # Half of TILE_SIZE
is_running = False
black_tiles_count = 0
click_count = 0
start_time = 0
top_left_bbox = (621, 256)  # Default top-left coordinates
bottom_right_bbox = (1276, 910)  # Default bottom-right coordinates
interval_value = 0.01  # Default interval value

# Calculate the size of the tiles based on the area dimensions
def calculate_tile_size():
    global TILE_SIZE, TILE_OFFSET
    width = bottom_right_bbox[0] - top_left_bbox[0]
    height = bottom_right_bbox[1] - top_left_bbox[1]
    TILE_SIZE = max(min(width, height) // 4, 1)  # Ensure a minimum tile size of 1 pixel
    TILE_OFFSET = TILE_SIZE // 2

# Perform a mouse click at the given coordinates with the specified interval
def click(x, y):
    pyautogui.click(x=x, y=y, interval=interval_value)

# Capture the screenshot of the specified area
def get_image():
    return ImageGrab.grab(bbox=(top_left_bbox[0], top_left_bbox[1], bottom_right_bbox[0], bottom_right_bbox[1]))

# Check for black tiles in the screenshot and return their coordinates
def check_tiles(img):
    global black_tiles_count
    tiles = []
    black_tiles_count = 0
    for y in range(0, 4):
        for x in range(0, 4):
            pixel_x = TILE_OFFSET + (TILE_SIZE * x)
            pixel_y = TILE_OFFSET + (TILE_SIZE * y)
            # Check if pixel coordinates are within image dimensions
            if 0 <= pixel_x < img.width and 0 <= pixel_y < img.height:
                if img.getpixel((pixel_x, pixel_y)) == (0, 0, 0):  # Check for black tiles
                    black_tiles_count += 1
                    tiles.append((top_left_bbox[0] + pixel_x, top_left_bbox[1] + pixel_y))
    return tiles

# Update the time interval for clicking
def set_interval(val):
    global interval_value
    interval_value = 10 ** float(val)  # Convert 'val' to float before exponentiation
    interval_label.config(text=f"Interval: {interval_value:.10f} seconds")

# Perform mouse clicks on the tiles in a given list
def click_tiles(tiles):
    global is_running, click_count, start_time
    start_time = time.time()
    while tiles and is_running:
        closest_tile = None
        min_distance = float('inf')
        for tile in tiles:
            distance = get_distance(pyautogui.position(), tile)
            if distance < min_distance:
                min_distance = distance
                closest_tile = tile

        if not is_running:
            break
        try:
            click(closest_tile[0], closest_tile[1])
            click_count += 1
            update_counters()  # Update the counters after each click
            tiles.remove(closest_tile)
        except pyautogui.FailSafeException:
            print("Failsafe Exception: Mouse has moved to the corner. Stopping clicking.")
            stop_clicking()
            break
        except Exception as e:
            print(f"Error while clicking: {e}")
            break

# Calculate the Euclidean distance between two points
def get_distance(tile1, tile2):
    x1, y1 = tile1
    x2, y2 = tile2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Thread function to start clicking on tiles
def start_clicking_thread():
    global is_running
    while is_running:
        try:
            if is_running:
                tiles = check_tiles(get_image())
                if not tiles:
                    print("Error: No black tiles detected in the screenshot.")
                else:
                    click_tiles(tiles)
        except Exception as e:
            print(f"Error while taking screenshot or clicking: {e}")

# Start the clicking process
def start_clicking():
    global is_running, click_count, black_tiles_count, start_time
    if not root.winfo_exists():  # Check if the window exists before starting
        return
    if not is_running:
        click_count = 0
        black_tiles_count = 0
        start_time = time.time()
        is_running = True
        click_thread = Thread(target=start_clicking_thread)
        click_thread.start()
        status_label.config(text="Status: Running", fg="green")
        update_counters()

# Stop the clicking process
def stop_clicking():
    global is_running, click_count
    is_running = False
    click_count = 0
    status_label.config(text="Status: Stopped", fg="red")

# Set the top-left coordinates of the area
def set_top_left():
    global top_left_bbox
    top_left_bbox = pyautogui.position()
    top_left_label.config(text=f"Top-Left: {top_left_bbox}")
    calculate_tile_size()

# Set the bottom-right coordinates of the area
def set_bottom_right():
    global bottom_right_bbox
    bottom_right_bbox = pyautogui.position()
    bottom_right_label.config(text=f"Bottom-Right: {bottom_right_bbox}")
    calculate_tile_size()

# Event handler for keyboard input
def on_key(event):
    try:
        if event.name == "2":
            stop_clicking()
        elif event.name == "1":
            if root and not root.winfo_exists():  # Check if the window exists before handling keys
                return
            start_clicking()
        elif event.name == "3":
            if root and not root.winfo_exists():  # Check if the window exists before handling keys
                return
            set_top_left()
        elif event.name == "4":
            if root and not root.winfo_exists():  # Check if the window exists before handling keys
                return
            set_bottom_right()
    except RuntimeError as e:
        pass

# Event handler for the close event
def on_close():
    global is_running
    if is_running:
        stop_clicking()
    root.destroy()
    keyboard.unhook_all()

# Update the counters for click statistics
def update_counters():
    global is_running, click_count, black_tiles_count, start_time
    cps = click_count / (time.time() - start_time)
    cps_label.config(text=f"CPS: {cps:.2f}")
    black_tiles_label.config(text=f"Black Tiles Left: {black_tiles_count}")
    clicks_label.config(text=f"Total Clicks: {click_count}")
    root.update()

# Main function to create and run the GUI
def main():
    global is_running, root, interval_label, status_label

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_close)  # Add a handler for the close event
    root.title("donttapAuto")
    root.geometry("400x450")
    root.attributes('-topmost', True)

    global black_tiles_label, clicks_label, cps_label, top_left_label, bottom_right_label, interval_label

    black_tiles_label = tk.Label(root, text="Black Tiles Left: 0")
    black_tiles_label.pack()

    clicks_label = tk.Label(root, text="Total Clicks: 0")
    clicks_label.pack()

    cps_label = tk.Label(root, text="CPS: 0")
    cps_label.pack()

    top_left_label = tk.Label(root, text=f"Top-Left: {top_left_bbox}")
    top_left_label.pack()

    bottom_right_label = tk.Label(root, text=f"Bottom-Right: {bottom_right_bbox}")
    bottom_right_label.pack()

    note_label_start = tk.Label(root, text="Press the number '1' to start clicking")
    note_label_start.pack()

    note_label_stop = tk.Label(root, text="Press the number '2' to stop clicking")
    note_label_stop.pack()

    note_label_set_top = tk.Label(root, text="Press the number '3' to set top-left coordinates")
    note_label_set_top.pack()

    note_label_set_bottom = tk.Label(root, text="Press the number '4' to set bottom-right coordinates")
    note_label_set_bottom.pack()

    # Add a logarithmic slider for the time interval
    interval_slider_label = tk.Label(root, text="Time Interval (log scale)")
    interval_slider_label.pack()
    interval_slider = tk.Scale(root, from_=math.log10(0.000000001), to=0, resolution=0.01, orient=tk.HORIZONTAL, command=set_interval)
    interval_slider.set(math.log10(interval_value))
    interval_slider.pack()

    interval_label = tk.Label(root, text=f"Interval: {interval_value:.10f} seconds")
    interval_label.pack()

    status_label = tk.Label(root, text="Status: Stopped", fg="red")
    status_label.pack()

    calculate_tile_size()  # Calculate the tile size based on the area dimensions
    keyboard.on_press(on_key)

    root.mainloop()

if __name__ == "__main__":
    main()
