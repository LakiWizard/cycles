
import sys
from cx_Freeze import setup, Executable


base = None
# if on win, dont show console
if sys.platform == "win32":
    base = "Win32GUI"

# include the font file
to_include = ["DejaVuSansMono.ttf"]

options = {
    "build_exe": {
        "include_files": to_include
        }
}

setup(name="Cycles",
      version="1.0",
      executables=[Executable("cycles.py", base=base)],
      options=options
      )
