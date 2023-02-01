import subprocess
from subprocess import DEVNULL, PIPE
from time import sleep
from colorama import Fore
import os


class objection:
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
            "apk": "~/.mmsf/loot/apks/base.apk",
            "network": False,
            "abi": "autodetect"
        }
        self.__init_objection()
    
    def __init_objection(self):
        p = subprocess.run(['objection'], stdout=PIPE, stderr=PIPE)
        if not p.stdout or p.stderr:
            print(Fore.RED + '[-] Objection is missing. Check your installation... Exitting... ')
            quit()
        else:
            print(Fore.BLUE + '[*] objection is running!' + Fore.RESET)

    def bypass_ssl_pinning(self):
        cmd = ['objection', '-g', self._config["app"], 'explore', '-q', '-c', 'Objection_Scripts/ssl_pinning.txt']
        print(Fore.YELLOW + "Command used: " + " ".join(cmd) + Fore.RESET)
        subprocess.Popen(cmd, stderr=DEVNULL, stdout=DEVNULL)
        sleep(5)
        p = subprocess.Popen(['ps', '-au'], stdout=subprocess.PIPE).communicate()[0]
        if self._config["app"] in p.decode():
            print(Fore.GREEN + '[+] Command executed successfully, check your traffic!' + Fore.RESET)
        else:
            print(Fore.RED + '[-] Some error occured! Try again!' + Fore.RESET)

    def bypass_root_detection_android(self):
        cmd = ['objection', '-g', self._config["app"], 'explore', '-q', '-c', 'Objection_Scripts/root_detection_android.txt']
        print(Fore.YELLOW + "Command used: " + " ".join(cmd) + Fore.RESET)
        subprocess.Popen(cmd, stderr=DEVNULL, stdout=DEVNULL)
        sleep(5)
        p = subprocess.Popen(['ps', '-au'], stdout=subprocess.PIPE).communicate()[0]
        if self._config["app"] in p.decode():
            print(Fore.GREEN + '[+] Command executed successfully, check your traffic!' + Fore.RESET)
        else:
            print(Fore.RED + '[-] Some error occured! Try again!' + Fore.RESET)

    def patch_apk(self):
        network = ""
        if self.config["network"]:
            network = "-N"
        self.config["apk"] = os.path.expanduser(self.config['apk'])
        if not os.path.isfile(self.config['apk']):
            print(Fore.RED + 'Source not found! Try again!' + Fore.RESET)
            return
        cmd = f"objection patchapk -a {self.config['abi']} {network} -s {self.config['apk']}"
        print(Fore.GREEN + "[+] Patching apk.. Waiting for output" + Fore.RESET)

        p = subprocess.run(cmd.split(), input="True".encode('UTF-8'), stdout=PIPE, stderr=PIPE)
        if p.stderr.decode():
            print(Fore.RED + p.stderr.decode() + Fore.RESET) 
        print(Fore.GREEN + p.stdout.decode() + Fore.RESET)

    def patch_ipa(self):
        pass
