from json import loads
import os
import subprocess
from subprocess import DEVNULL, PIPE
from bs4 import BeautifulSoup
from colorama import Fore
import requests
from Classes.utils import quit
from Classes.constants import Constants

class Installer:
    def __init__(self, forced=False) -> None:
        self.packages = ['apktool', 'apksigner', 'java', 'drozer', 'reflutter', 'objection', 'frida']
        self._forced = forced
        if not self._is_sudo():
            print(Fore.RED + '[-] sudo required!'  + Fore.RESET)
            quit()

    def _is_sudo(self):
        if os.getuid() == 0:
            return True
        return False

    def install_packages(self):
        for package in self.packages:
            self._install(package)

    def _install(self, package):
        if package == "apktool":
            self._install_apktool()
        elif package == "apksigner":
            self._install_apksigner()
        elif package == "java":
            self._install_java()
        elif package == "drozer":
            self._install_drozer()
        elif package == "reflutter":
            self._install_reflutter()
        elif package == "objection":
            self._install_objection()
        elif package == "frida":
            self._install_frida()

    def _check_installed(self, cmd):
        try:
            print(Fore.BLUE + '[*] Checking for ' + cmd + Fore.RESET)
            subprocess.run([cmd], stderr=DEVNULL, stdout=DEVNULL)
            print(Fore.GREEN + '[+] Installed' + Fore.RESET)
            return True
        except Exception:
            return False

    def _install_apktool(self):
        installed = self._check_installed('apktool')
        if not installed or self._forced:
            resp = requests.get("https://api.github.com/repos/iBotPeaches/Apktool/releases/latest")
            latest = loads(resp.content)['tag_name'][1:]
            jar_url = f'https://github.com/iBotPeaches/Apktool/releases/latest/download/apktool_{latest}.jar'
            apktool_jar = requests.get(jar_url)
            open(Constants.APKTOOL_JAR_PATH.value, 'wb').write(apktool_jar.content)
            apktool_wrapper_url = 'https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool'
            apktool = requests.get(apktool_wrapper_url)
            open(Constants.APKTOOL_PATH.value, 'wb').write(apktool.content)
            subprocess.run(['chmod', '+x', Constants.APKTOOL_JAR_PATH.value], stdout=DEVNULL, stderr=DEVNULL)
            subprocess.run(['chmod', '+x', Constants.APKTOOL_PATH.value], stdout=DEVNULL, stderr=DEVNULL)

    def _install_apksigner(self):
        installed = self._check_installed('apksigner')
        if not installed or self._forced:
            subprocess.run(['sudo', 'apt-get', 'install', 'apksigner'], stderr=DEVNULL, stdout=DEVNULL)

    def _install_java(self):
        installed = self._check_installed('java')
        if not installed or self._forced:
            subprocess.run(['sudo', 'apt-get', 'install','default-jdk'])
            subprocess.run(['sudo', 'apt-get', 'instal', 'default-jre'])

    def _install_drozer(self):
        installed = self._check_installed('drozer')
        if not installed or self._forced:
            drozer_wheel = requests.get("https://github.com/FSecureLABS/drozer/releases/download/2.4.4/drozer-2.4.4-py2-none-any.whl")
            open(Constants.DROZER_WHEEL.value, 'wb').write(drozer_wheel.content)
            subprocess.run(['sudo', 'pip', 'install', Constants.DROZER_WHEEL.value], stderr=DEVNULL, stdout=DEVNULL)

    def _install_reflutter(self):
        installed = self._check_installed('reflutter')
        if not installed or self._forced:
            cmd = 'python3 -m pip install reflutter'
            subprocess.run(cmd.split(), stderr=DEVNULL, stdout=DEVNULL)

    def _install_objection(self):
        installed = self._check_installed('objection')
        if not installed or self._forced:
            cmd = "python3 -m pip install --upgrade objection"
            subprocess.run(cmd.split(), stderr=DEVNULL, stdout=DEVNULL)

    def _install_frida(self):
        installed = self._check_installed('frida')
        frida_path = os.path.join(Constants.DIR_UTILS_PATH.value, 'frida-server')
        if not installed or self._forced:
            try:
                abi = subprocess.run([Constants.ADB.value, 'shell', 'getprop ro.product.cpu.abi'], stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()[0]
            except IndexError as e:
                print(Fore.RED + '[-] Device not running. Power on the device first... Exitting...' + Fore.RESET)
                quit()
            url = "https://github.com/frida/frida/releases"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            classes = soup.find_all("a", class_="Link--primary")
            latest_ver = ""
            for class_ in classes:
                if class_.text.startswith("Frida"):
                    latest_ver = class_.text.split(" ")[1]
                    break
            file_to_download = url + "/download/" + latest_ver + "/frida-server-" + latest_ver + "-android-" + abi + ".xz"
            frida_server = requests.get(file_to_download)
            open(frida_path + '.xz', 'wb').write(frida_server.content)

            # Decompress frida server and push it to the mobile
            subprocess.run(['xz', '-f', '-d', frida_path+'.xz'])
            subprocess.run([Constants.ADB.value, 'push', frida_path, '/tmp/frida-server'], stderr=DEVNULL, stdout=DEVNULL)
            subprocess.run([Constants.ADB.value, 'shell', 'chmod +x /tmp/frida-server'], stderr=DEVNULL, stdout=DEVNULL)

if __name__ == "__main__":
    installer = Installer()
    installer.install_packages()