import os
import subprocess
import sys
from time import sleep
from bs4 import BeautifulSoup
from colorama import Fore
from subprocess import DEVNULL, PIPE
import requests
from Classes.constants import Constants


class Frida:
    _config: dict

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, data):
        self._config = data

    def __repr__(self) -> str:
        pass

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, __o: object) -> bool:
        """Compare two class instances."""
        if __o.id == self.id:
            return True
        return False

    def __init__(self, low_power_mode=False) -> None:
        self.__init_frida()
        self.low_power_mode = low_power_mode
        self._config = {
            "mode": "-U",
            "app": "",
            "host": "127.0.0.1",
            "pause": "",
            "method": "-f"
        }

    def __init_frida(self):
        
        p = subprocess.Popen([Constants.ADB.value, 'shell', '"/tmp/frida-server &"'], stderr=PIPE)
        if "inaccessible or not found" in p.communicate()[1].decode():
            p = subprocess.Popen([Constants.ADB.value, 'shell', '"su && /data/local/tmp/frida-server"'], stderr=PIPE)

        subprocess.run([Constants.ADB.value, 'forward', 'tcp:27042', 'tcp:27042'], stderr=DEVNULL, stdout=DEVNULL)

        p = subprocess.run(['frida-ps', '-U'], stdout=PIPE, stderr=PIPE)
        if "Failed to enumerate processes: unable to find process with name 'system_server'" in p.stdout.decode():
            print(Fore.RED + '[-] frida is missing. Check your installation or install via mmsfupdate frida_server... Exitting... ')
            quit()

        print(Fore.BLUE + '[*] Frida is running' + Fore.RESET)

    def bypass_ssl(self):
        cmd = f'frida {self._config["pause"].strip()} {self._config["mode"]} {self.config["method"]} {self._config["app"].strip()} -l Frida_Scripts/bypass_ssl_pinning_various_methods.js'
        print(Fore.YELLOW + "Command used: " + cmd + Fore.RESET)
        subprocess.Popen(cmd.split(), stderr=DEVNULL, stdout=DEVNULL)
        sleep(3)
        p = subprocess.run("ps -C frida -f".split(), stdout=subprocess.PIPE, stderr=PIPE)
        if self._config["app"] in p.stdout.decode():
            print(Fore.GREEN + '[+] Command executed successfully, check your traffic!' + Fore.RESET)
        else:
            print(Fore.RED + '[-] Some error occured! Try again!' + Fore.RESET)
    
    def bypass_root(self):
        cmd = ['frida', self._config["mode"], self.config["method"], self._config['app'], '-l', 'Frida_Scripts/antiroot_bypass.js', self._config["pause"]]
        print(Fore.YELLOW + "Command used: " + " ".join(cmd) + Fore.RESET)
        subprocess.Popen(cmd, stderr=DEVNULL, stdout=DEVNULL)
        sleep(3)
        p = subprocess.run("ps -C frida -f".split(), stdout=subprocess.PIPE, stderr=PIPE)
        if self._config["app"] in p.stdout.decode():
            print(Fore.GREEN + '[+] Command executed successfully, check your application!' + Fore.RESET)
        else:
            print(Fore.RED + '[-] Some error occured! Try again!' + Fore.RESET)
    