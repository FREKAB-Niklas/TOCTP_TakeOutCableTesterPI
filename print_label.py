import os

# Adjusted ZPL template with improved positioning
zpl_template = """
^XA
^FO50,30^A0N,100,100^FD{PART_NUMBER}^FS  ; Part Number, made larger
^FO50,150^A0N,40,40^FD{DESCRIPTION_LINE_1}^FS  ; Description Line 1, adjusted position
^FO50,200^A0N,40,40^FD{DESCRIPTION_LINE_2}^FS  ; Description Line 2, adjusted position
^FO50,250^A0N,50,50^FDWeek^FS              ; "Week" label, adjusted position
^FO250,250^A0N,50,50^FDREV^FS              ; "REV" label, adjusted position
^FO450,250^A0N,50,50^FDSerial^FS           ; "Serial" label, adjusted position
^FO50,320^A0N,70,70^FD{WEEK}^FS            ; Week number, adjusted position and size
^FO250,320^A0N,70,70^FD{REV}^FS            ; Revision, adjusted position and size
^FO450,320^A0N,70,70^FD{SERIAL}^FS         ; Serial number, adjusted position and size
^XZ
"""

# Variables to be replaced
part_number = "21 - 33001922"
description_line_1 = "Imaging cable with"
description_line_2 = "21 take - outs, 5m spacing"
week = "2435"
rev = "A"
serial = "00001"

# Replace placeholders with actual values
zpl_code = zpl_template.format(
    PART_NUMBER=part_number,
    DESCRIPTION_LINE_1=description_line_1,
    DESCRIPTION_LINE_2=description_line_2,
    WEEK=week,
    REV=rev,
    SERIAL=serial
)

# Write the ZPL to a temporary file
zpl_file_path = "/tmp/label.zpl"
with open(zpl_file_path, "w") as f:
    f.write(zpl_code)

# Send the ZPL file to the printer in raw mode
os.system(f"lp -d GK420d -o raw {zpl_file_path}")
