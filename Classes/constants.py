from enum import Enum
import os

class Constants(Enum):
    DELIM = " " * 10  + "|  "
    MMSF_COMMANDS = ["back", "run", "set", "show", "exit"]
    ADB = "adb"
    DIR_HOMEDIR = os.path.expanduser('~')
    DIR_WORKINGDIR = os.path.join(DIR_HOMEDIR, '.mmsf')
    DIR_INSTALLDIR = "/opt/mmsf/"
    DIR_LOOT_PATH = os.path.join(DIR_WORKINGDIR, 'loot')
    DIR_FRIDA_SCRIPTS = os.path.join(DIR_WORKINGDIR, 'Frida_Scripts')
    DIR_UTILS_PATH = os.path.join(DIR_WORKINGDIR, 'utils')
    DIR_PULLED_APKS = os.path.join(DIR_LOOT_PATH, 'apks')
    DIR_LOOT_DATA = os.path.join(DIR_LOOT_PATH, 'data')
    DIR_SCANS_PATH = os.path.join(DIR_LOOT_PATH, 'drozer_scans')
    GENERATED_APK = os.path.join(DIR_PULLED_APKS, 'base_unsigned.apk')
    PATCHED_APK = os.path.join(DIR_PULLED_APKS, 'base_patched.apk')
    APKTOOL_PATH = '/usr/local/bin/apktool'
    APKTOOL_JAR_PATH = '/usr/local/bin/apktool.jar'
    NEWBACKUP_NAME_TAR = "newbackup.tar"
    NEWBACKUP_NAME = "newbackup.ab"
    PCKLIST_NAME = "package.list"
    BACKUP_NAME = "backup.ab"
    BACKUP_COMPRESSED_NAME = "backup.tar"
    DROZER = "docker run --network host --rm -it withsecurelabs/drozer"
    UBERSIGNER_PATH = f"{os.path.join(DIR_UTILS_PATH,'ubersigner.jar')}"
    UBERSIGNER = f"java -jar {UBERSIGNER_PATH}"
    ZIPALIGN = "zipalign -p -f 4"
    ZIPALIGN_COMMON_DIRECTORIES = ["/usr/local/bin", "/usr/bin", "/bin", "/opt/local/bin", "/usr/sbin", "~/Library/Android/sdk/build-tools", "/sbin", "/Library/Android/sdk/build-tools"] 
