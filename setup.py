import sys
from cx_Freeze import setup, Executable

path = ['app'] + sys.path
includefiles = ['basepics\\','debug\\','pics\\','memory.ini','runefarming.ini','runefarming.log','runefarming_fodders.ini','runefarming_stats.csv']
includes = []
excludes = ['Tkinter','Tk','Tcl']


build_exe_options = {
'path': path,
'include_files': includefiles,
'includes': includes,
'excludes': excludes
#'icon': 'resources\icons\clock.ico'
}

exe=Executable(
     script="runefarming.py",
     base = None #base = "Win32Gui" In order to hide the cmd window
     )

setup(
    name = "swauto" , 
    version = "0.1",
    description = "SW auto farmer", 
    options = {'build_exe': build_exe_options},
    executables = [exe]
    )
