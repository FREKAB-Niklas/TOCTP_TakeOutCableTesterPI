import os

# Define the ZPL template with placeholders
zpl_template = """
^XA
^FO50,50^A0N,100,100^FD{PART_NUMBER}^FS
^FO50,180^A0N,50,50^FD{DESCRIPTION_LINE_1}^FS
^FO50,240^A0N,50,50^FD{DESCRIPTION_LINE_2}^FS
^FO50,320^A0N,60,60^FDWeek^FS
^FO200,320^A0N,60,60^FDREV^FS
^FO400,320^A0N,60,60^FDSerial^FS
^FO50,400^A0N,80,80^FD{WEEK}^FS
^FO250,400^A0N,80,80^FD{REV}^FS
^FO450,400^A0N,80,80^FD{SERIAL}^FS
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
with open("/tmp/label.zpl", "w") as f:
    f.write(zpl_code)

# Send the ZPL file to the printer
os.system("lp -d GK420d /tmp/label.zpl")
