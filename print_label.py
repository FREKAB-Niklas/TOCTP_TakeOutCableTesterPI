import os

# ZPL code for a simple label
zpl = """
^XA
^FO50,50
^A0N50,50
^FDHello, World!^FS
^XZ
"""

# Save ZPL to a temporary file
with open("/tmp/label.zpl", "w") as f:
    f.write(zpl)

# Send the ZPL file to the printer using the CUPS printer name
os.system("lp -d GK420d /tmp/label.zpl")
