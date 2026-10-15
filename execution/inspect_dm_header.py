import zipfile
import ctypes
import os

with zipfile.ZipFile(r"c:\Users\Nilvan\Documents\07 - PROJETOS\01 - PROJETOS POWER BI\PROJETO 16 - Painel Comercial\PROJETO 16 - Painel Comercial.pbix") as z:
    dm = z.read("DataModel")

print("Header (first 128 bytes):", dm[:128])

# ABF format:
# Often has header text: "This backup was created using XPress9 compression.\0" (in UTF-16LE)
# followed by compression blocks or chunks.
# Let's inspect where the null terminator or magic bytes are.
header_end = dm.find(b"\x00\x00\x00")
print("header_end index:", header_end)
if header_end != -1:
    print("Bytes after header:", dm[header_end:header_end+64].hex())
