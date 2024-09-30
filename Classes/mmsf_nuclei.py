import os
import shutil
import subprocess
from subprocess import DEVNULL, PIPE
from colorama import Fore
from Classes.constants import Constants
import xml.etree.ElementTree as ET

class nuclei:
    
    id: str
    _config: dict

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, data):
        self._config = data

    def __init__(self, low_power_mode=False) -> None:
        self._config = {
            "dir_name": "",
            "out_file": "",
            "app_name": "",
            "out_dir": ""
        }
        self.low_power_mode = low_power_mode     

    def _start_scan(self, path):
        app_name = self.config.get('app_name') if self.config.get('app_name') else os.path.basename(os.path.normpath(self.config.get('dir_name')))
        filename = f"{app_name}_nuclei_scan_{path}.txt" if not self.config.get("out_file") else self.config.get("out_file")
        outdir = Constants.DIR_NUCLEI_SCANS.value if not self.config.get("out_dir") else os.path.join(self.config.get("out_dir"), 'nuclei_scans')
        if not os.path.isdir(outdir):
            os.mkdir(outdir)

        if not self.config.get("dir_name"):
            self.config["dir_name"] = os.path.join(Constants.DIR_PULLED_APKS.value, self.config["dir_name"])

        command_echo = f"echo {self.config.get('dir_name')}"
        command_nuclei = f"nuclei -t {os.path.join(Constants.DIR_NUCLEI_SCRIPTS.value, path)} -o {os.path.join(outdir,filename)}"

        try:
            # Run the echo command and capture its output
            echo_result = subprocess.run(command_echo, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # If the echo command was successful, run the nuclei command with its output as input
            if echo_result.returncode == 0:
                nuclei_result = subprocess.run(command_nuclei, input=echo_result.stdout, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Print the nuclei command output or error
                if nuclei_result.returncode == 0:
                    print(Fore.GREEN + f"\n[+] Results written at {os.path.join(outdir,filename)}" + Fore.RESET)
                else:
                    print(Fore.RED + '\n[-] Error' + Fore.RESET)
            else:
                print(Fore.RED + '\n[-] Error' + Fore.RESET)

        except Exception as e:
            print(Fore.RED + f"\n[-] An error occurred: {str(e)}" + Fore.RESET)