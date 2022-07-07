from enum import Enum

class Constants(Enum):
    DELIM = " " * 10  + "|  "
    MMSF_COMMANDS = ["back", "run", "set", "show", "exit"]
    ADB = "/opt/genymobile/genymotion/tools/adb"