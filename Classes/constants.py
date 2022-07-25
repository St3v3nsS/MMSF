from enum import Enum
import os

class Constants(Enum):
    DELIM = " " * 10  + "|  "
    MMSF_COMMANDS = ["back", "run", "set", "show", "exit"]
    ADB = "/opt/genymobile/genymotion/tools/adb"
    DIR_HOMEDIR = os.path.expanduser('~')
    DIR_WORKINGDIR = os.path.join(DIR_HOMEDIR, '.mmsf')
    DIR_INSTALLDIR = "/opt/mmsf/"
    DIR_LOOT_PATH = os.path.join(DIR_WORKINGDIR, 'loot')
    DIR_UTILS_PATH = os.path.join(DIR_WORKINGDIR, 'utils')
    DIR_PULLED_APKS = os.path.join(DIR_LOOT_PATH, 'apks')
    DIR_SCANS_PATH = os.path.join(DIR_LOOT_PATH, 'drozer_scans')
    TEMP_APK = os.path.join(DIR_PULLED_APKS, 'temp.apk')
    APKTOOL_PATH = '/usr/local/bin/apktool'
    APKTOOL_JAR_PATH = '/usr/local/bin/apktool.jar'
    DROZER_WHEEL = '/tmp/drozer_setup.whl'