import subprocess
from subprocess import DEVNULL, PIPE
from time import sleep
from colorama import Fore


class objection:
    id: str
    _config: dict

    def __init__(self) -> None:
        self._config = {
            "app": ""
        }
        self.__init_objection()
    
    def __init_objection(self):
        p = subprocess.run(['objection'], stdout=PIPE, stderr=PIPE)
        if not p.stdout or p.stderr:
            print(Fore.RED + '[-] Objection is missing. Check your installation... Exitting... ')
            quit()

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
