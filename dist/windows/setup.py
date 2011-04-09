from cx_Freeze import setup, Executable
 
import sys
include_files = [("LICENSE.txt","LICENSE.txt"),("template.db","template.db"),("tracks.cute.small.png","tracks.cute.small.png"),("icon.png","icon.png"),("icons","icons")]
includes = []
excludes = []
packages = []
path = []
 
Target_1 = Executable(
    # what to build
    script = "tracks.py",
    base = 'Win32GUI',
    icon = "icon.ico",
) 
 
 
setup(
        name = "tracks",
        version = "2011.1",
        description = "tracks.cute, personal task manager",
        options = {"build_exe": {"includes": includes,"include_files": include_files, "excludes": excludes,"packages": packages, "path": path, "optimize":2}},
        executables = [Target_1])
