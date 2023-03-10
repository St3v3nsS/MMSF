import shutil
import subprocess
from subprocess import DEVNULL, PIPE
import tempfile
import time
from colorama import Fore
import os
import psutil
from .constants import Constants
import requests
import random
from .utils import execute_command, find_command, is_port_open

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
        self.ports_list = range(8800, 9999)
        self.current_port = random.choice(self.ports_list)
        self.api_is_running = False
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = tempfile.mkstemp(dir=self.temp_dir, suffix=".js")[1]
        self.files = {'ssl-android': os.path.join(self.temp_dir,'objection-ssl-android.log'), 
                      'root-android': os.path.join(self.temp_dir,'objection-root-android.log'), 
                      'biometrics-ios': os.path.join(self.temp_dir,'objection-biometrics-ios.log'),
                      'jailbreak-ios': os.path.join(self.temp_dir,'objection-jailbreak-ios.log')}
        
        for file in self.files.keys():
            if (os.path.exists(self.files[file])):
                os.remove(self.files[file])
    
    def __del__(self):
        shutil.rmtree(self.temp_dir)
    
    def __init_objection(self):
        p = subprocess.run(['objection'], stdout=PIPE, stderr=PIPE)
        if not p.stdout or p.stderr:
            print(Fore.RED + '[-] Objection is missing. Check your installation... Exitting... ')
            quit()
        else:
            print(Fore.BLUE + '[*] objection is running!' + Fore.RESET)

    def is_frida_running(self):
        return find_command('frida', self.config['app'])
    
    def get_pid(self):
        cmd = f'{Constants.ADB.value} shell ps'
        p = subprocess.run(cmd.split(), stderr=PIPE, stdout=PIPE)
        for line in p.stdout.decode().splitlines():
            if self.config["app"] in line:
                return line.split()[1]

    def bypass_ssl_pinning(self):
        if self.api_is_running:
            self.exec_api_cmd('androidSslPinningDisable')
        elif self.is_frida_running():
            pid = self.get_pid()
            print(Fore.YELLOW + '[*] Frida is already running. Attaching to it ...' + Fore.RESET)
            while is_port_open(self.current_port):
                self.current_port = random.choice(self.ports_list)
            cmd = f'objection -ap {self.current_port} -g {pid} api'
            outfile = self.files['ssl-android']
            execute_command(cmd, outfile, 'objection')
            self.api_is_running = True
            time.sleep(5)
            self.exec_api_cmd('androidSslPinningDisable')
        else:    
            cmd = " ".join(['objection', '-g', self._config["app"], 'explore', '-s', "'android sslpinning disable'"])
            outfile = self.files['ssl-android']
            execute_command(cmd, outfile, 'objection')

    def bypass_root_detection_android(self):
        if self.api_is_running:
            self.exec_api_cmd('androidRootDetectionDisable')
        elif self.is_frida_running():
            pid = self.get_pid()
            print(Fore.YELLOW + '[*] Frida is already running. Attaching to it ...' + Fore.RESET)
            while is_port_open(self.current_port):
                self.current_port = random.choice(self.ports_list)
            cmd = f'objection -ap {self.current_port} -g {pid} api'
            outfile = self.files['root-android']
            execute_command(cmd, outfile, 'objection')
            self.api_is_running = True
            time.sleep(5)
            self.exec_api_cmd('androidRootDetectionDisable')
        else:  
            cmd = " ".join(['objection', '-g', self._config["app"], 'explore', '-s', "'android root disable'"])
            outfile = self.files['root-android']
            execute_command(cmd, outfile, 'objection')

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
    
    def get_ios_pid(self):
        cmd = 'frida-ps -Ua'
        out = subprocess.run(cmd.split(), stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()
        for line in out:
            if self._config['app'] in line:
                return line.split()[0]
    
    def bypass_ios_biometrics(self):
        if self.api_is_running:
            self.exec_api_cmd('iosUiBiometricsBypass')
        elif self.is_frida_running():
            pid = self.get_ios_pid()
            print(Fore.YELLOW + '[*] Frida is already running. Attaching to it ...' + Fore.RESET)
            while is_port_open(self.current_port):
                self.current_port = random.choice(self.ports_list)
            cmd = f'objection -ap {self.current_port} -g {pid} api'
            outfile = self.files['biometrics-ios']
            execute_command(cmd, outfile, 'objection')
            self.api_is_running = True
            time.sleep(5)
            self.exec_api_cmd('iosUiBiometricsBypass')
        else:  
            cmd = " ".join(['objection', '-g', self._config["app"], 'explore', '-s', "'ios ui biometrics_bypass'"])
            outfile = self.files['biometrics-ios']
            execute_command(cmd, outfile, 'objection')
            
    def exec_api_cmd(self, cmd):
        url = f"http://127.0.0.1:{self.current_port}/rpc/invoke/{cmd}"
        r = requests.get(url=url)
        if r.status_code == 200:
            if 'Failed to call method' in r.text:
                print(Fore.RED + '[-] The following error occured: \n' + "\n".join(r.json()["message"].split("\n")) + Fore.RESET)
                self.api_is_running = False
            else:
                print(Fore.GREEN + '[+] Objection command executed successfully!' + Fore.RESET)
                
    def patch_ipa(self):
        pass
    
    def bypass_ios_jailbreak(self):
        if self.api_is_running:
            self.exec_api_cmd('iosJailbreakDisable')
        elif self.is_frida_running():
            pid = self.get_ios_pid()
            print(Fore.YELLOW + '[*] Frida is already running. Attaching to it ...' + Fore.RESET)
            while is_port_open(self.current_port):
                self.current_port = random.choice(self.ports_list)
            cmd = f'objection -ap {self.current_port} -g {pid} api'
            outfile = self.files['jailbreak-ios']
            execute_command(cmd, outfile, 'objection')
            self.api_is_running = True
            time.sleep(5)
            self.exec_api_cmd('iosJailbreakDisable')
        else:  
            cmd = " ".join(['objection', '-g', self._config["app"], 'explore', '-s', "'ios jailbreak disable'"])
            outfile = self.files['jailbreak-ios']
            execute_command(cmd, outfile, 'objection')