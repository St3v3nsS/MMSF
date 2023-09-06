#!/usr/bin/python3

from json import loads
import os
import subprocess
from subprocess import DEVNULL, PIPE
import sys
from bs4 import BeautifulSoup
from colorama import Fore
import requests
from Classes.utils import quit
from Classes.constants import Constants

class Installer:
    def __init__(self, forced=False) -> None:
        self.packages = ['apktool', 'apksigner', 'java', 'drozer', 'reflutter', 'objection', 'frida', 'abe']
        self._forced = forced

    @property
    def forced(self):
        return self._forced

    @forced.setter
    def forced(self, forced):
        self._forced = forced

    def _is_sudo(self):
        if os.getuid() == 0:
            return True
        return False

    def install_packages(self):
        # if not self._is_sudo():
        #     print(Fore.RED + '[-] sudo required!'  + Fore.RESET)
        #     quit()
        for package in self.packages:
            self._install(package)

    def _install(self, package):
        if package == "apktool":
            self._install_apktool()
        elif package == "abe":
            self._install_abe()
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
            self._install_frida_server()
            self._install_frida_client()
        

    def _check_installed(self, cmd):
        try:
            print(Fore.BLUE + '[*] Checking for ' + cmd + Fore.RESET)
            p = subprocess.run(cmd.split(), stderr=PIPE, stdout=PIPE)
            if 'Unable to find image' in p.stderr.decode():
                print(Fore.RED + '[-] Not installed ' + Fore.RESET )
                return False
            print(Fore.GREEN + '[+] Installed' + Fore.RESET)
            return True
        except Exception:
            print(Fore.RED + f'[-] {cmd} not found' + Fore.RESET)
            return False

    def _install_apktool(self):
        installed = self._check_installed('apktool')
        if not installed or self._forced:
            print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
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
            print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
            subprocess.run(['sudo', 'apt-get', 'install', 'apksigner'], stderr=DEVNULL, stdout=DEVNULL)

    def _install_java(self):
        installed = self._check_installed('java')
        if not installed or self._forced:
            print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
            subprocess.run(['sudo', 'apt-get', 'install','default-jdk'])
            subprocess.run(['sudo', 'apt-get', 'instal', 'default-jre'])

    def _install_drozer(self):
        installed = self._check_installed(Constants.DROZER.value)
        if not installed or self._forced:
            print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
            p = subprocess.run('docker build --rm -t fsecure/drozer docker_files/drozer'.split(), stderr=PIPE, stdout=PIPE)
            if 'Successfully tagged fsecure/drozer:latest' in p.stdout.decode():
                print(Fore.GREEN + '[*] Successfully installed drozer'  + Fore.RESET)
            else:
                print(Fore.RED + p.stderr.decode() + Fore.RESET)

    def _install_reflutter(self):
        installed = self._check_installed('reflutter')
        if not installed or self._forced:
            print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
            cmd = 'pipx install reflutter --force'
            subprocess.run(cmd.split(), stderr=DEVNULL, stdout=DEVNULL)

    def _install_objection(self):
        installed = self._check_installed('objection')
        if not installed or self._forced:
            print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
            cmd = "pipx install objection --force"
            p = subprocess.run(cmd.split(), stderr=PIPE, stdout=PIPE)
            print(p.stderr)
            print(p.stdout)

    def _check_frida_server(self):
        p = subprocess.run([Constants.ADB.value, 'shell', 'ls /tmp/frida-server'], capture_output=True)
        if "No such file" in p.stderr.decode() or "No such file" in p.stdout.decode():
            return False
        return True

    def _install_frida_client(self):
        installed = self._check_installed('frida')
        if not installed or self._forced:
            print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
            subprocess.run('pipx install frida-tools --force'.split(), stderr=DEVNULL, stdout=DEVNULL)

    def _install_frida_server(self):
        installed_server = self._check_frida_server()
        frida_path = os.path.join(Constants.DIR_UTILS_PATH.value, 'frida-server')
        if not installed_server or self._forced:
            print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
            try:
                abi = subprocess.run([Constants.ADB.value, 'shell', 'getprop ro.product.cpu.abi'], stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()[0]
                print(abi)
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

    def _install_abe(self):
        installed = True
        if self.forced or not installed:
            print(Fore.YELLOW + '[*] Installing ' + Fore.RESET)
            url = "https://github.com/nelenkov/android-backup-extractor/releases/"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            classes = soup.find_all("a", class_="Link--primary")
            latest_ver = ""
            for class_ in classes:
                if class_.text.startswith("master-"):
                    latest_ver = class_.text.split(":")[0]
                    print(Fore.GREEN + "[+] Downloading abe.jar... " + Fore.RESET)
                    print(os.path.join(Constants.DIR_UTILS_PATH.value, "abe.jar"))
                    if not os.path.isdir(Constants.DIR_UTILS_PATH.value):
                        try:
                            print(Fore.YELLOW + f"[*] Creating directory in {Constants.DIR_UTILS_PATH.value}")
                            os.makedirs(Constants.DIR_UTILS_PATH.value)
                        except OSError as e:
                            print(Fore.LIGHTBLUE_EX + '[DEBUG] ' + e + Fore.RESET)
                    new_url = f"https://github.com/nelenkov/android-backup-extractor/releases/download/{latest_ver}/abe.jar"
                    open(os.path.join(Constants.DIR_UTILS_PATH.value, "abe.jar"), "wb").write(requests.get(new_url).content)
                    break

if __name__ == "__main__":
    installer = Installer()
    if len(sys.argv) > 1:
        if sys.argv[1] == "apktool":
            installer.forced = True
            installer._install_apktool()
        elif sys.argv[1] == "apksigner":
            installer.forced = True
            installer._install_apksigner()
        elif sys.argv[1] == "java":
            installer.forced = True
            installer._install_java()
        elif sys.argv[1] == "drozer":
            installer.forced = True
            installer._install_drozer()
        elif sys.argv[1] == "reflutter":
            installer.forced = True
            installer._install_reflutter()
        elif sys.argv[1] == "objection":
            installer.forced = True
            installer._install_objection()
        elif sys.argv[1] == "frida_client":
            installer.forced = True
            installer._install_frida_client()
        elif sys.argv[1] == "frida_server":
            installer.forced = True
            installer._install_frida_server()
        elif sys.argv[1] == "abe":
            installer.forced = True
            installer._install_abe()
    else:
        installer.install_packages()