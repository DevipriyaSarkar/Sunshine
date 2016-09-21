import cx_Freeze
import sys

base = None

if sys.platform == 'win32':
    base = "Win32GUI"

executables = [cx_Freeze.Executable("weather.py", base=base, icon="sun.ico")]

cx_Freeze.setup(
    name="Sunshine",
    options={"build_exe": {"packages": ["Tkinter", "PIL"], "include_files": ["keys.py", "sun.ico", "sun.png",
                                                                             "next.png", "prev.png",
                                                                             "city.list.json"]}},
    version="0.01",
    description="Simple weather GUI application",
    executables=executables
)
