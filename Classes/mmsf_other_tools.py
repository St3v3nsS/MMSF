import subprocess
from subprocess import DEVNULL, PIPE
from time import sleep
import time
from colorama import Fore
import os
from .constants import Constants


class OtherTools:
    id: str
    _config: dict

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, data):
        self._config = data

    def __init__(self, low_power_mode=False) -> None:
        self.low_power_mode = low_power_mode
        self._config = {
            "app": "",
            "path": Constants.DIR_LOOT_DATA.value,
            "password": ""

        }
        self.backup_files = {}
        self._init_backup_constants()
        self._init_tools()
    
    def _init_backup_constants(self):
        self._abe = f'java -jar {os.path.join(Constants.DIR_UTILS_PATH.value, "abe.jar")}'
        self.backup_files["restore_tar"] = os.path.join(self.config["path"], Constants.NEWBACKUP_NAME_TAR.value)
        self.backup_files["new_backup_ab"] = os.path.join(self.config["path"], Constants.NEWBACKUP_NAME.value)
        self.backup_files["backup_ab_location"] = os.path.join(self.config["path"], Constants.BACKUP_NAME.value)
        self.backup_files["package_list"] = os.path.join(self.config["path"], Constants.PCKLIST_NAME.value)
        self.backup_files["backup_tar_location"] = os.path.join(self.config["path"], Constants.BACKUP_COMPRESSED_NAME.value)

    def _init_tools(self):
        p = subprocess.run(self._abe.split(), stdout=PIPE, stderr=PIPE)
        if not p.stdout or p.stderr:
            print(Fore.RED + '[-] AndroidBackupExtractor is missing. Install the abe.jar file... Exitting... ')
            quit()
        else:
            print(Fore.BLUE + '[*] ABE is running!' + Fore.RESET)

    # Get package list
    def get_package_list(self):
        cmd_get_package_list = f'tar tf {self.backup_files["backup_tar_location"]}'
        p = subprocess.run(cmd_get_package_list.split(), stderr=PIPE, stdout=PIPE)
        out = p.stdout.decode().splitlines()
        with open(self.backup_files["package_list"]) as f:
            f.writelines(out)
    

    def extract_backup(self):
        cmd = f'{Constants.ADB.value} backup -f {self.backup_files["backup_ab_location"]} {self.config["app"]}'
        # if result code != 0 exit
        time.sleep(5)
        cmd_unpack = f'{self._abe} unpack {self.backup_files["backup_ab_location"]} {self.backup_files["backup_tar_location"]} {self.config["password"]}'
        p = subprocess.run(cmd_unpack.split(), stderr=PIPE, stdout=PIPE)
        # check for errors
        # Deflating the files 
        cmd_untar = f'tar -C {self.config["path"]} -xf {self.backup_files["backup_tar_location"]}'
        p = subprocess.run(cmd_untar.split(), stderr=PIPE, stdout=PIPE)
        # check for success or error
        self.get_package_list()

    def restore_backup(self):
        if not os.path.isfile(self.backup_files["package_list"]):
            self._get_package_list()
        cmd_tar = f'tar cf {self.backup_files["restore_tar"]} -T {self.backup_files["package_list"]}'
        p = subprocess.run(cmd_tar.split(), stderr=PIPE, stdout=PIPE)
        # check for errors
        cmd_pack = f'{self._abe} pack {self.backup_files["restore_tar"]} {self.backup_files["new_backup_ab"]} {self.config["password"]}'
        p = subprocess.run(cmd_pack.split(), stderr=PIPE, stdin=PIPE)
        # check for errors
        cmd = f'adb restore {self.backup_files["new_backup_ab"]}'
        p = subprocess.run(cmd.split(), stderr=PIPE, stdin=PIPE)
        # check for errors