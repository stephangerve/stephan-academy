import os

DRIVE_LETTER = "C:"
ONEDRIVE_DIR = DRIVE_LETTER + "\\Users\\Stephan\\OneDrive"
MAIN_DIR = os.path.join(ONEDRIVE_DIR, "W")
E_PACKS_DIR = os.path.join(ONEDRIVE_DIR, "Exercise Packs")
FLASHCARDS_DIR = os.path.join(ONEDRIVE_DIR, "Flashcards")
OLD_SS_PATH = "C:\\Users\\Stephan\\Downloads\\Old Screenshots"
#TEMP_SS_PATH = os.path.join(OLD_SS_PATH, "Temp")
TEMP_FC_PATH = os.path.join(OLD_SS_PATH, "Temp Flashcards")
TXTBK_SOURCE_PATH = "W:\\Textbooks (Local)\\Print List 2"

RESOURCE_PATH = os.path.join(os.getcwd(), "Resources")
SOUND_WARNING = os.path.join(RESOURCE_PATH, "Sounds", "warning - Universfield from Pixabay.wav")
SOUND_TICK = os.path.join(RESOURCE_PATH, "Sounds", "tick edited 2 - Universfield from Pixabay.wav")
SOUND_NEXT = os.path.join(RESOURCE_PATH, "Sounds", "next edited 2 - Universfield from Pixabay.wav")
DOWN_ARROW = os.path.join(RESOURCE_PATH, "Icons", "down-arrow.svg")
RIGHT_ARROW = os.path.join(RESOURCE_PATH, "Icons", "right-arrow.svg")
DRAG_HANDLE = os.path.join(RESOURCE_PATH, "Icons", "drag-handle.svg")

HOSTNAME = "localhost"
USERNAME = "root"
DATABASENAME = "ls_data"
with open("C:\\Users\\Stephan\\Downloads\\db.txt") as file:
    PASSWORD = file.read()
    file.close()

MONITOR_NUMBER = 1

OP_SIMPLE = "ctrl+shift+alt+1"
OP_APP_TO_LAST = "ctrl+shift+alt+2"
OP_SET_HEADER = "ctrl+shift+alt+3"
OP_COMBINE_W_H = "ctrl+shift+alt+4"
OP_APP_TO_HEAD = "ctrl+shift+alt+5"
OP_GRID_MODE = "ctrl+shift+alt+6"
OP_CANCEL = 'esc'
OP_TWO_COLUMNS = "ctrl+shift+alt+x"
OP_INC_INDEX = "ctrl+shift+alt+y"
OP_RESET_IMAGE_LIST = "ctrl+shift+alt+z"

SHAPE_BBOX = "BBox"
SHAPE_LINE = "Line"

ALL_OPs = [OP_SIMPLE,
           OP_APP_TO_LAST,
           OP_SET_HEADER,
           OP_COMBINE_W_H,
           OP_APP_TO_HEAD,
           OP_GRID_MODE,
           OP_TWO_COLUMNS,
           OP_RESET_IMAGE_LIST]

STANDARD_OPs = [OP_SIMPLE,
                OP_APP_TO_LAST,
                OP_SET_HEADER,
                OP_COMBINE_W_H,
                OP_APP_TO_HEAD,
                OP_GRID_MODE]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 168, 0)
NEON_GREEN = (20, 255, 57)
RED = (0, 0, 255)
PURPLE = (201, 6, 162)
BLUE = (240, 96, 7)
ORANGE = (5, 104, 252)
TURQUOISE = (229, 235, 52)
GREY_LIGHT_BLUE = (213, 223, 240)
BBOX_COLOR = {
    OP_SIMPLE: RED,
    OP_APP_TO_LAST: PURPLE,
    OP_SET_HEADER: BLUE,
    OP_COMBINE_W_H: ORANGE,
    OP_APP_TO_HEAD: TURQUOISE,
}

COLUMN_LEFT = "Left"#-0.1
COLUMN_RIGHT = "Right"#0.1


DEFAULT_SCAN_RADIUS_BBOX = 20  # default: 20
DEFAULT_SCAN_RADIUS_MASK = 20  # default: 20
DEFAULT_SCAN_RADIUS_COL_LINE = 100  # default: 100
DEFAULT_SCAN_RADIUS_GRID_COL = 150  # default: 150

DEFAULT_SCAN_ROW_AVERAGE_COLOR_THRESHOLD = 254 #255 strongest intensity
DEFAULT_BIN_SEARCH_WHITE_THRESHOLD = 250 # default: 240
DEFAULT_BIN_SEARCH_USE_AVERAGE_INTENSITY = True # default: False; if false then minimum pixel intensity is used
DEFAULT_USE_LAST_WHITE_REG = True # default: False


EXERCISE_GRADE_COLORS = {
    "A": (147, 235, 52),
    "B": (217, 235, 52),
    "C": (235, 171, 52),
    "D": (235, 92, 52),
    "F": (235, 52, 52),
}


DashboardPage_page_number = 0
CategoryPage_page_number = 1
LearningPage_page_number = 2
ExercisePage_page_number = 3
AddTextbookPage_page_number = 4
AddExercisesPage_page_number = 5
AddToStudyListPage_page_number = 6
StudyListPage_page_number = 7
FlashcardsPage_page_number = 8
EditFlashcardsPage_page_number = 9
StudyFlashcardsPage_page_number = 10

UI_BLUE = ""
NAVY_BLUE = (58, 74, 97)
DARK_NAVY_BLUE = (49, 63, 83)


