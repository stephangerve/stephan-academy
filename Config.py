import os

DRIVE_LETTER = "C:"
MAIN_DIR = DRIVE_LETTER + "\\Users\\Stephan\\OneDrive\\W"
TEMP_SS_PATH = "C:\\Users\\Stephan\\Downloads\\Old Screenshots\\Temp"
OLD_SS_PATH = "C:\\Users\\Stephan\\Downloads\\Old Screenshots"
E_PACKS_DIR = "C:\\Users\\Stephan\\OneDrive\\Exercise Packs"
TXTBK_SOURCE_PATH = "W:\\Textbooks (Local)\\Print List 2"

HOSTNAME = "localhost"
USERNAME = "root"
DATABASENAME = "ls_data"
with open("C:\\Users\\Stephan\\Downloads\\db.txt") as file:
    PASSWORD = file.read()
    file.close()

