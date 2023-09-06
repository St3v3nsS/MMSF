import subprocess
from subprocess import DEVNULL, PIPE
from colorama import Fore


class reflutter:
    id:str
    _config: dict

    def __init__(self, low_power_mode=False) -> None:
        self._config = {
            "burp": "127.0.0.1",
            "apk": "base.apk"
        }
        self.low_power_mode = low_power_mode
        self.__init_reflutter()

    def __init_reflutter(self):
        print(Fore.BLUE + "[*] reflutter is running!" + Fore.RESET)


    def bypass_ssl_pinning(self):
        cmd = ['reflutter', self._config["apk"]]
        print(Fore.YELLOW + "Command used: " + " ".join(cmd) + Fore.RESET)
        p = subprocess.run(cmd, input=f"1".encode('UTF-8'), stderr=DEVNULL, stdout=PIPE)
        print(p.stdout.decode())