import time
import tkinter as tk
from tkinter import font
from tkinter import messagebox
from PIL import Image, ImageTk
import pandas as pd
import os
from datetime import datetime, timedelta
import openpyxl
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image as OpenpyxlImage
import configparser
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import PatternFill
import threading
from adafruit_mcp230xx.mcp23017 import MCP23017
import board
import busio
from digitalio import Direction, Pull

print("run_article.py is starting...")

# Initialize main window
root = tk.Tk()
root.title("Testing Interface")
root.geometry("1920x1080")
root.attributes('-fullscreen', True)

center_display_label = tk.Label(root, text="", font=("Helvetica", 32))
center_display_label.pack(pady=20)

pin_labels = [tk.Label(root, text=f"{i+1}: {chr(65+i)}", font=("Helvetica", 16)) for i in range(8)]
for label in pin_labels:
    label.pack(anchor='w')

# Initialize I2C bus and MCP23017
i2c = busio.I2C(board.SCL, board.SDA)
mcp1 = MCP23017(i2c, address=0x20)
mcp2 = MCP23017(i2c, address=0x22)

# List of MCP23017 pins to test (both chips)
mcp_pins = [(mcp1, i) for i in range(16)] + [(mcp2, i) for i in range(16)]
for mcp, pin in mcp_pins:
    mcp_pin = mcp.get_pin(pin)
    mcp_pin.direction = Direction.INPUT
    mcp_pin.pull = Pull.UP


config = configparser.ConfigParser()
config.read('article_config.txt')

filename = config['DEFAULT']['filename']
pins = config['DEFAULT']['pins'].split(',')

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the image file inside the PI folder
logo_path = os.path.join(script_dir, "Logo.png")

# Variable Information
amount_of_cycles_done = 0
elapsed_time_current_cycle = 0
elapsed_time_previous_cycle = 0
total_elapsed_time = 0
downtime = 0
skipped_tests = 0
current_pin_index = 0
is_running = False


#Custom fonts
header_font = font.Font(family="Helvetica", size=24, weight="bold")
center_font = font.Font(family="Helvetica", size=124, weight="bold")
body_font = font.Font(family="Helvetica", size=16)

def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02}"

def seconds_to_hms(seconds):
    # Converts seconds to HH:MM:SS format
    return str(timedelta(seconds=seconds))

def str_to_timedelta(time_str):
    if isinstance(time_str, timedelta):
        return time_str
    try:
        time_obj = datetime.strptime(time_str, "%H:%M:%S")
        return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second)
    except ValueError:
        return timedelta(seconds=0)

def mcp_pin_to_gui_pin(mcp, pin):
    mapping = {
        (0x20, 0): '1: A',  # MCP 0x20 pin A0 to GUI pin 1: A
        (0x20, 1): '2: B',  # MCP 0x20 pin A1 to GUI pin 2: B
        (0x20, 2): '3: C',  # MCP 0x20 pin A2 to GUI pin 3: C
        (0x20, 3): '4: D',  # MCP 0x20 pin A3 to GUI pin 4: D
        (0x20, 4): '5: E',  # MCP 0x20 pin A4 to GUI pin 5: E
        (0x20, 5): '6: F',  # MCP 0x20 pin A5 to GUI pin 6: F
        (0x20, 6): '7: G',  # MCP 0x20 pin A6 to GUI pin 7: G
        (0x20, 7): '8: H',  # MCP 0x20 pin A7 to GUI pin 8: H
        (0x20, 8): '16: S', # MCP 0x20 pin B0 to GUI pin 16: S
        (0x20, 9): '15: R', # MCP 0x20 pin B1 to GUI pin 15: R
        (0x20, 10): '14: P',# MCP 0x20 pin B2 to GUI pin 14: P
        (0x20, 11): '13: N',# MCP 0x20 pin B3 to GUI pin 13: N
        (0x20, 12): '12: M',# MCP 0x20 pin B4 to GUI pin 12: M
        (0x20, 13): '11: L',# MCP 0x20 pin B5 to GUI pin 11: L
        (0x20, 14): '10: K',# MCP 0x20 pin B6 to GUI pin 10: K
        (0x20, 15): '9: J', # MCP 0x20 pin B7 to GUI pin 9: J
        (0x22, 0): '17: T', # MCP 0x22 pin A0 to GUI pin 17: T
        (0x22, 1): '18: U', # MCP 0x22 pin A1 to GUI pin 18: U
        (0x22, 2): '19: V', # MCP 0x22 pin A2 to GUI pin 19: V
        (0x22, 3): '20: W', # MCP 0x22 pin A3 to GUI pin 20: W
        (0x22, 4): '21: X', # MCP 0x22 pin A4 to GUI pin 21: X
        (0x22, 5): '22: Y', # MCP 0x22 pin A5 to GUI pin 22: Y
        (0x22, 6): '23: Z', # MCP 0x22 pin A6 to GUI pin 23: Z
        (0x22, 7): '24: a', # MCP 0x22 pin A7 to GUI pin 24: a
        (0x22, 8): '25: b', # MCP 0x22 pin B0 to GUI pin 25: b
        (0x22, 9): '26: c', # MCP 0x22 pin B1 to GUI pin 26: c
        (0x22, 10): '27: d',# MCP 0x22 pin B2 to GUI pin 27: d
        (0x22, 11): '28: e',# MCP 0x22 pin B3 to GUI pin 28: e
        (0x22, 12): '29: f',# MCP 0x22 pin B4 to GUI pin 29: f
        (0x22, 13): '30: g',# MCP 0x22 pin B5 to GUI pin 30: g
        (0x22, 14): '31: h',# MCP 0x22 pin B6 to GUI pin 31: h
        (0x22, 15): '32: j',# MCP 0x22 pin B7 to GUI pin 32: j
    }
    return mapping.get((mcp, pin), None)



def read_mcp_probes():
    for mcp_chip, pin in mcp_pins:
        mcp_address = mcp_chip._device.device_address  # Updated to use _device
        mcp_pin = mcp_chip.get_pin(pin)
        if not mcp_pin.value:  # LOW indicates probed
            print(f"Detected LOW signal: MCP={hex(mcp_address)}, PIN={pin}")  # Updated logging
            return mcp_address, pin, True
    return None, None, False




def on_pin_probe(gui_pin_label, current_pin_index):
    global current_pin_label
    expected_label = f"{current_pin_index + 1}: {current_pin_label}"
    if gui_pin_label == expected_label:
        pin_labels[current_pin_index].config(bg='green')
        current_pin_index += 1
        if current_pin_index < len(pin_labels):
            next_pin_label = pin_labels[current_pin_index]
            current_pin_label = next_pin_label.cget('text').split(': ')[1]
            update_current_pin_display(current_pin_index, current_pin_label)
        else:
            complete_cycle()
    else:
        print(f"Pin mismatch: expected {expected_label}, but got {gui_pin_label}")

def update_current_pin_display(current_pin_index, current_pin_label):
    # Update the center display
    center_display_label.config(text=f"{current_pin_index + 1}: {current_pin_label}", bg='yellow')

    # Update the left panel background color
    for i, label in enumerate(pin_labels):
        if i == current_pin_index:
            label.config(bg='yellow')
        else:
            label.config(bg='SystemButtonFace')


def monitor_pins():
    print("Starting pin monitoring...")  # Initial log to confirm thread start
    while True:
        mcp, pin, probe_value = read_mcp_probes()
        if probe_value:
            gui_pin_label = mcp_pin_to_gui_pin(mcp, pin)
            if gui_pin_label is not None:
                print(f"Probing detected: MCP={hex(mcp)}, PIN={pin}, GUI_PIN={gui_pin_label}")  # Detailed log
                root.after(0, lambda: on_pin_probe(gui_pin_label))
            else:
                print(f"No mapping found for MCP={hex(mcp)}, PIN={pin}")  # Log for missing mapping
        time.sleep(0.1)






# Start monitoring pins in a separate thread
thread = threading.Thread(target=monitor_pins)
thread.daemon = True
thread.start()

def calculate_average(ws):
    total_time = timedelta()
    total_count = 0
    for row in range(6, ws.max_row + 1):
        total_time += str_to_timedelta(ws[f'E{row}'].value)
        total_count += ws[f'C{row}'].value

    if total_count > 0:
        average_time = total_time / total_count
    else:
        average_time = timedelta()
    return average_time

def confirm_last_probe():
    global current_pin_index
    if current_pin_index == len(pins) - 1:
        print(f"All pins probed, checking all probed status in 500ms")
        root.after(500, check_all_probed)

def check_all_probed():
    all_probed = all(label.cget("bg") == "#32CD32" for label in left_panel_labels)
    print(f"Check all probed: {all_probed}")
    for i, label in enumerate(left_panel_labels):
        print(f"Pin {i+1} background color: {label.cget('bg')}")
    if all_probed:
        complete_cycle()
    else:
        confirm_complete_cycle()



def complete_probe():
    global current_pin_index
    if current_pin_index < len(pins) - 1:
        left_panel_labels[current_pin_index].config(bg="#32CD32")
        print(f"Pin {pins[current_pin_index]} probed successfully, setting to green")
        current_pin_index += 1
        current_wire_label.config(text=pins[current_pin_index], bg="yellow")
        left_panel_labels[current_pin_index].config(bg="yellow")
        print(f"Next pin to probe: {pins[current_pin_index]}")
    else:
        left_panel_labels[current_pin_index].config(bg="#32CD32")
        print(f"Last pin probed: {pins[current_pin_index]}. Confirming last probe in 500ms")
        root.after(500, confirm_last_probe)

def complete_cycle():
    global current_pin_label
    # Logic for completing the cycle
    print("Cycle completed successfully.")
    for label in pin_labels:
        label.config(bg='SystemButtonFace')  # Reset all to default color
    current_pin_index = 0
    current_pin_label = pin_labels[current_pin_index].cget('text').split(': ')[1]
    update_current_pin_display(current_pin_index, current_pin_label)

def confirm_complete_cycle():
    print("Opening confirmation window for incomplete cycle.")
    confirm_window = tk.Toplevel(root)
    confirm_window.title("Bekräfta")
    confirm_window.geometry("1920x1080")
    confirm_window.attributes('-fullscreen', True)

    message_label = tk.Label(confirm_window, text="Du försöker färdigställa utan att alla punkter är testade, är du säker att du vill fortsätta?\nBekräfta genom att skriva OK", font=body_font)
    message_label.pack(pady=10)

    entry = tk.Entry(confirm_window, font=body_font)
    entry.pack(pady=10)

    def on_confirm():
        if entry.get().strip().upper() == "OK":
            confirm_window.destroy()
            complete_cycle()
        else:
            tk.messagebox.showerror("Fel", "Felaktig bekräftelse")

    confirm_button = tk.Button(confirm_window, text="Bekräfta", font=body_font, command=on_confirm)
    confirm_button.pack(pady=10)

    # On-screen keyboard
    keyboard_frame = tk.Frame(confirm_window, bg="blue")
    keyboard_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    def insert_char(char):
        entry.insert(tk.END, char)

    keys = [
        'QWERTYUIOP',
        'ASDFGHJKL',
        'ZXCVBNM'
    ]

    key_padx = 5  # Padding for keys
    key_pady = 5

    for i, key_row in enumerate(keys):
        row_frame = tk.Frame(keyboard_frame, bg="blue")
        row_frame.grid(row=i, column=0, columnspan=3, pady=key_pady, padx=key_padx)
        for char in key_row:
            button = tk.Button(row_frame, text=char, font=body_font, width=6, height=4, command=lambda c=char: insert_char(c))
            button.pack(side=tk.LEFT, padx=key_padx, pady=key_pady)

    space_button = tk.Button(keyboard_frame, text="SPACE", font=body_font, width=20, height=2, command=lambda: insert_char(" "))
    space_button.grid(row=3, column=0, columnspan=3, pady=key_pady)

    # Arrange numpad keys in the keyboard window
    numpad_keys = [
        '789',
        '456',
        '123',
        '0+-'
    ]

    numpad_frame = tk.Frame(keyboard_frame, bg="blue")
    numpad_frame.grid(row=0, column=4, rowspan=4, padx=key_padx, pady=key_pady)

    for i, key_row in enumerate(numpad_keys):
        row_frame = tk.Frame(numpad_frame, bg="blue")
        row_frame.pack(pady=key_pady)
        for char in key_row:
            button = tk.Button(row_frame, text=char, font=body_font, width=8, height=5, command=lambda c=char: insert_char(c))
            button.pack(side=tk.LEFT, padx=key_padx, pady=key_pady)

    close_button = tk.Button(keyboard_frame, text="X", font=body_font, width=10, height=5, command=confirm_window.destroy, bg="red")
    close_button.grid(row=5, column=4, columnspan=3, pady=key_pady)





def update_timer():
    global elapsed_time_current_cycle, downtime
    if is_running:
        elapsed_time_current_cycle += 1
    else:
        downtime += 1
    time_info_label.config(text=f"Tid\nNu: {format_time(elapsed_time_current_cycle)}\nFörra: {format_time(elapsed_time_previous_cycle)}\nTotal: {format_time(total_elapsed_time + elapsed_time_current_cycle)}\nStälltid: {format_time(downtime)}")
    root.after(1000, update_timer)  # Update every second (1000 milliseconds)

def reset_test():
    response = messagebox.askyesno("Reset", "Är du säker att du vill reseta?")
    if response:
        global current_pin_index, elapsed_time_current_cycle, total_elapsed_time, downtime, is_running
        total_elapsed_time += elapsed_time_current_cycle
        elapsed_time_current_cycle = 0
        current_pin_index = 0
        downtime = 0
        is_running = False
        for label in left_panel_labels:
            label.config(bg="light gray")
        left_panel_labels[current_pin_index].config(bg="yellow")
        current_wire_label.config(text=pins[current_pin_index], bg="yellow")
        time_info_label.config(text=f"Tid\nNu: {format_time(elapsed_time_current_cycle)}\nFörra: {format_time(elapsed_time_previous_cycle)}\nTotal: {format_time(total_elapsed_time)}\nStälltid: {format_time(downtime)}")
        
        # Reset all MCP23017 pins
        for mcp, pin in mcp_pins:
            mcp_pin = mcp.get_pin(pin)
            mcp_pin.direction = Direction.INPUT
            mcp_pin.pull = Pull.UP
        print("Reset complete and MCP23017 pins reset")  # Add logging for debugging




def toggle_timer():
    global is_running
    is_running = not is_running
    if is_running:
        current_wire_label.config(bg="yellow", text=pins[current_pin_index])
    else:
        current_wire_label.config(bg="orange", text="Pausad")

def on_pin_click(idx):
    global current_pin_index
    if idx > current_pin_index:
        # Check if the jump skips any pins in the current cycle
        for i in range(current_pin_index + 1, idx + 1):
            if left_panel_labels[i].cget("bg") != "#32CD32":  # Not green
                response = messagebox.askyesno("Hoppa över", "Du hoppar över flera punkter, är du säker att du vill fortsätta?")
                if not response:
                    return
                break
    # Preserve the green status if the pin was already tested
    current_color = left_panel_labels[current_pin_index].cget("bg")
    if current_color != "#32CD32":
        left_panel_labels[current_pin_index].config(bg="SystemButtonFace")
    
    current_pin_index = idx
    left_panel_labels[current_pin_index].config(bg="yellow")
    current_wire_label.config(text=pins[current_pin_index], bg="yellow")
    if not is_running:
        current_wire_label.config(bg="#32CD32", text="Starta")

def time_string_to_seconds(time_str):
    if isinstance(time_str, int):
        return time_str
    time_obj = datetime.strptime(time_str, "%H:%M:%S")
    return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second).total_seconds()

def calculate_totals(data):
    total_cycles = sum(data['Antal'])
    total_time = sum([str_to_timedelta(time_str).total_seconds() for time_str in data['Total Cykeltid (HH:MM:SS)']])
    return total_cycles, total_time

def calculate_average_time(total_time, total_cycles):
    if total_cycles > 0:
        average_time = timedelta(seconds=total_time / total_cycles)
    else:
        average_time = timedelta(seconds=0)
    return average_time


def save_log(filename, data):
    # Convert the data dictionary to a DataFrame
    df = pd.DataFrame(data)

    # Create a new workbook and add a worksheet
    wb = openpyxl.Workbook()
    ws = wb.active

    # Add the image to the worksheet
    img = Image(logo_path)
    img.anchor = 'A1'
    ws.add_image(img)


    # Add column headers for the log data
    column_headers = ["Batchdatum", "Antal", "Antal skippad test", "Total Cykeltid (HH:MM:SS)",
                      "Total Ställtid (HH:MM:SS)", "Total Stycktid (HH:MM:SS)", "Cykeltid (HH:MM:SS)",
                      "Stycktid (HH:MM:SS)", "Styck Ställtid (HH:MM:SS)"]
    
    for col_num, header in enumerate(column_headers, 1):
        col_letter = openpyxl.utils.get_column_letter(col_num)
        ws[f'{col_letter}6'] = header
        ws[f'{col_letter}6'].alignment = Alignment(horizontal="center")
        ws[f'{col_letter}6'].font = openpyxl.styles.Font(bold=True)

    # Add the data rows to the worksheet starting from row 7
    for row_num, row_data in df.iterrows():
        for col_num, (col_name, value) in enumerate(row_data.items(), 1):
            col_letter = openpyxl.utils.get_column_letter(col_num)
            ws[f'{col_letter}{row_num + 7}'] = value

    # Save the workbook
    wb.save(filename)


def create_new_log_file(filename, data):
    df = pd.DataFrame(data)

    # Extract the relevant part of the filename
    base_filename = os.path.basename(filename)
    article_number = base_filename.split('_')[0]

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, startrow=4, startcol=1)

        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Add the image and set its position and size
        img = OpenpyxlImage(logo_path)
        img.anchor = 'A1'
        img.width = 340  # Set the width to fit into A1:B3
        img.height = 80  # Set the height to fit into A1:B3
        worksheet.add_image(img)

        # Add headers
        headers = ["Artikelnummer", "AVG. Stycktid", "Senaste Stycktid"]
        values = [article_number, "00:00:00", df.iloc[0]['Cykeltid (HH:MM:SS)']]  # Initialize with the first entry's Cykeltid
        for col_num, (header, value) in enumerate(zip(headers, values), 2):
            worksheet.cell(row=1, column=col_num * 2).value = header
            worksheet.cell(row=2, column=col_num * 2).value = value
            worksheet.cell(row=1, column=col_num * 2).font = Font(bold=True)
            worksheet.cell(row=2, column=col_num * 2).alignment = Alignment(horizontal="center")

        worksheet.column_dimensions['A'].width = 5
        worksheet.column_dimensions['B'].width = 25
        worksheet.column_dimensions['C'].width = 25
        worksheet.column_dimensions['D'].width = 25
        worksheet.column_dimensions['E'].width = 25
        worksheet.column_dimensions['F'].width = 25
        worksheet.column_dimensions['G'].width = 25
        worksheet.column_dimensions['H'].width = 25
        worksheet.column_dimensions['I'].width = 25
        worksheet.column_dimensions['J'].width = 25
        worksheet.column_dimensions['K'].width = 25

        # Calculate total cycles and total time
        total_cycles, total_time = calculate_totals(data)

        # Calculate average cycle time
        avg_cycle_time = calculate_average_time(total_time, total_cycles)

        # Add headers for total calculations
        worksheet['G1'] = "Total Tid"
        worksheet['G3'] = "Total Antal"

        # Make headers bold
        worksheet['G1'].font = Font(bold=True)
        worksheet['G3'].font = Font(bold=True)

        # Update calculated values in the worksheet
        worksheet['G4'] = total_cycles
        worksheet['G2'] = seconds_to_hms(total_time)
        worksheet['F2'] = str(avg_cycle_time)

    print(f"Created new log file: {filename}")

def update_log(filename, data):
    try:
        wb = openpyxl.load_workbook(filename)
        ws = wb.active

        next_row = ws.max_row + 1
        for idx, (key, value) in enumerate(data.items(), start=1):
            if idx == 1:  # Format Batchdatum as 'yy-mm-dd hh:mm'
                value[0] = datetime.now().strftime('%y-%m-%d %H:%M')
            ws.cell(row=next_row, column=idx + 1, value=value[0])

        # Ensure the first entry's Batchdatum is formatted correctly
        if next_row == 7 and ws.cell(row=7, column=2).value == "240802":
            ws.cell(row=7, column=2).value = datetime.now().strftime('%y-%m-%d %H:%M')

        # Update the total calculation formulas
        last_row = next_row
        current_total_time = str_to_timedelta(ws['G2'].value) if ws['G2'].value else timedelta()
        current_total_count = ws['G4'].value if ws['G4'].value else 0

        new_time = str_to_timedelta(ws[f'E{next_row}'].value)
        new_count = ws[f'C{next_row}'].value

        ws['G2'] = current_total_time + new_time
        ws['G4'] = current_total_count + new_count

        # Update the Senaste Stycktid with the latest entry's Cykeltid (HH:MM:SS)
        ws['H2'] = ws.cell(row=next_row, column=8).value

        # Calculate the average in Python
        total_time = sum([str_to_timedelta(ws[f'E{row}'].value) for row in range(6, last_row + 1)], timedelta())
        total_count = sum([ws[f'C{row}'].value for row in range(6, last_row + 1)])
        f2_value = total_time / total_count if total_count > 0 else timedelta()
        h2_value = str_to_timedelta(ws['H2'].value)

        print(f"H2 Value: {h2_value}, F2 Value: {f2_value}")  # Debug output

        # Update the average value in F2
        ws['F2'] = str(f2_value)

        # Apply conditional formatting based on the recalculated average
        if h2_value < f2_value:
            ws['H2'].fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")
        else:
            ws['H2'].fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

        # Save the workbook after updating the background color
        wb.save(filename)
    except FileNotFoundError:
        create_new_log_file(filename, data)




# Function to finish the batch
def finish_batch():
    global amount_of_cycles_done, total_elapsed_time, downtime, skipped_tests

    batch_date = datetime.now().strftime('%y-%m-%d %H:%M')
    total_cycles = amount_of_cycles_done
    total_cycle_time = total_elapsed_time + downtime
    total_downtime = downtime
    total_work_time = total_elapsed_time
    avg_cycle_time = total_cycle_time // total_cycles if total_cycles > 0 else 0
    avg_work_time = total_work_time // total_cycles if total_cycles > 0 else 0
    avg_downtime = total_downtime // total_cycles if total_cycles > 0 else 0

    data = {
        "Batchdatum": [batch_date],
        "Antal": [total_cycles],
        "Antal skippad test": [skipped_tests],
        "Total Cykeltid (HH:MM:SS)": [seconds_to_hms(total_cycle_time)],
        "Total Ställtid (HH:MM:SS)": [seconds_to_hms(total_downtime)],
        "Total Stycktid (HH:MM:SS)": [seconds_to_hms(total_work_time)],
        "Cykeltid (HH:MM:SS)": [seconds_to_hms(avg_cycle_time)],
        "Stycktid (HH:MM:SS)": [seconds_to_hms(avg_work_time)],
        "Styck Ställtid (HH:MM:SS)": [seconds_to_hms(avg_downtime)]
    }
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the 'Artiklar' directory inside the PI folder
    log_filepath = os.path.join(script_dir, "Artiklar", f"{filename}_log.xlsx")

    # Call the update_log function with the constructed path
    update_log(log_filepath, data)


    # Reset batch variables
    amount_of_cycles_done = 0
    elapsed_time_current_cycle = 0
    total_elapsed_time = 0
    downtime = 0
    skipped_tests = 0

    # Update the labels
    completed_label.config(text=f"Färdiga: {amount_of_cycles_done}st")
    skipped_label.config(text=f"Antal Avvikande: {skipped_tests}st")




# Header Section
header_frame = tk.Frame(root)
header_frame.pack(side=tk.TOP, fill=tk.X)


# Open and resize the image
image = Image.open(logo_path)
scale_percent = 50  # percent of original size
width, height = image.size
new_width = int(width * scale_percent / 100)
new_height = int(height * scale_percent / 100)
resized_image = image.resize((new_width, new_height), Image.LANCZOS)
logo_image = ImageTk.PhotoImage(resized_image)

logo_label = tk.Label(header_frame, image=logo_image)
logo_label.pack(side=tk.LEFT, padx=10, pady=10)
logo_label.bind("<Button-1>", lambda e: root.destroy())  # Temporary function to close the app


article_label = tk.Label(header_frame, text=f"Artikelnummer: {filename}", font=body_font)
article_label.pack(side=tk.LEFT, padx=10, pady=10)

completed_label = tk.Label(header_frame, text=f"Färdiga: {amount_of_cycles_done}st", font=body_font, bg="#32CD32", fg="Black")
completed_label.pack(side=tk.RIGHT, padx=10, pady=10)

skipped_label = tk.Label(header_frame, text=f"Antal Avvikande: {skipped_tests}st", font=body_font, bg="red", fg="Black")
skipped_label.pack(side=tk.RIGHT, padx=10, pady=10)

# Left Panel
left_panel = tk.Frame(root)
left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=0)

left_panel_labels = []
for i, pin in enumerate(pins):
    label = tk.Label(left_panel, text=pin, font=body_font, justify=tk.LEFT, width=8, height=2)
    label.bind("<Button-1>", lambda e, idx=i: on_pin_click(idx))
    left_panel_labels.append(label)
    row = i % 16
    col = i // 16
    label.grid(row=row, column=col, sticky='w')


# Right Panel
right_panel = tk.Frame(root)
right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=50)


time_info_label = tk.Label(right_panel, text=f"Tid\nNu: {format_time(elapsed_time_current_cycle)}\nFörra: {format_time(elapsed_time_previous_cycle)}\nTotal: {format_time(total_elapsed_time)}\nStälltid: {format_time(downtime)}", font=body_font, justify=tk.LEFT)
time_info_label.pack()

# Central Display
central_frame = tk.Frame(root)
central_frame.pack(expand=True, padx=0)

current_wire_label = tk.Label(central_frame, text="Starta", font=center_font, bg="#32CD32", width=6, height=3)
current_wire_label.pack(pady=20)
current_wire_label.bind("<Button-1>", lambda e: toggle_timer())

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

# Button Frame
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)



# Update the diagnose button to finish batch
reset_button = tk.Button(button_frame, text="Reset", font=("Helvetica", 24), bg="#9900AB", fg="black", command=reset_test, width=20, height=50)
reset_button.pack(side=tk.LEFT, padx=20, pady=10)

finish_batch_button = tk.Button(button_frame, text="Finish Batch", font=("Helvetica", 24), bg="#0A60C5", fg="black", command=finish_batch, width=20, height=50)
finish_batch_button.pack(side=tk.RIGHT, padx=5, pady=10)




# Start the timer
root.after(1000, update_timer)  # Start the timer after the first second

# Initialize the first pin
left_panel_labels[current_pin_index].config(bg="yellow")

# Run the main loop
root.mainloop()
