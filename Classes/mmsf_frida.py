import os
import subprocess
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

    def __init__(self) -> None:
        self.__init_frida()
        self._config = {
            "mode": "-U",
            "app": "",
            "host": "127.0.0.1",
            "pause": "--no-pause"
        }

    def __init_frida(self):
        p = subprocess.run([Constants.ADB.value, 'shell', '/tmp/frida-server &'], stderr=PIPE, stdout=DEVNULL)
        if 'already' not in p.stderr.decode():
            print(p.stderr)
        subprocess.run([Constants.ADB.value, 'forward', 'tcp:27042', 'tcp:27042'], stderr=DEVNULL, stdout=DEVNULL)

        p = subprocess.run(['frida-ps', '-U'], stdout=PIPE, stderr=PIPE)
        if not p.stdout or p.stderr:
            print(Fore.RED + '[-] frida is missing. Check your installation... Exitting... ')
            quit()

    def bypass_ssl(self):
        cmd = ['frida', self._config["mode"], '-f', self._config['app'], '-l', 'Frida_Scripts/bypass_ssl_pinning_various_methods.js', self._config["pause"]]
        print(Fore.YELLOW + "Command used: " + " ".join(cmd) + Fore.RESET)
        subprocess.Popen(cmd, stderr=DEVNULL, stdout=DEVNULL)
        sleep(5)
        p = subprocess.Popen(['ps', '-au'], stdout=subprocess.PIPE).communicate()[0]
        if self._config["app"] in p.decode():
            print(Fore.GREEN + '[+] Command executed successfully, check your traffic!' + Fore.RESET)
        else:
            print(Fore.RED + '[-] Some error occured! Try again!' + Fore.RESET)
    
    def bypass_root(self):
        cmd = ['frida', self._config["mode"], '-f', self._config['app'], '-l', 'Frida_Scripts/antiroot_bypass.js', self._config["pause"]]
        print(Fore.YELLOW + "Command used: " + " ".join(cmd) + Fore.RESET)
        subprocess.Popen(cmd, stderr=DEVNULL, stdout=DEVNULL)
        sleep(5)
        p = subprocess.Popen(['ps', '-au'], stdout=subprocess.PIPE).communicate()[0]
        if self._config["app"] in p.decode():
            print(Fore.GREEN + '[+] Command executed successfully, check your application!' + Fore.RESET)
        else:
            print(Fore.RED + '[-] Some error occured! Try again!' + Fore.RESET)
    