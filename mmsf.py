#!/usr/bin/python3

from json import loads
import os
from sys import stdout
from time import sleep
import requests
from asyncio.subprocess import DEVNULL
import subprocess
from subprocess import PIPE
import warnings
from colorama import Fore
import readline
import shlex
from signal import signal, SIGINT
from bs4 import BeautifulSoup

from Classes.mmsf_drozer import drozer
from Classes.commands import Commands
from Classes.constants import Constants
# from Classes.mmsf_apktool import apktool
# from Classes.mmsf_frida import frida
# from Classes.mmsf_objection import objection
from Classes.utils import *

warnings.filterwarnings("ignore")
# Set the unbuffered output
os.environ.setdefault('PYTHONUNBUFFERED', '1')

class MassiveMobileSecurityFramework:
    id: str
    _drozer: drozer
    _frida: dict
    _objection: dict
    _flutter: dict
    _apktool: dict
    _drozer: drozer

    # getters
    @property
    def all_apps(self):
        return self._all_apps
        
    @property
    def frida(self):
        return self._frida

    @property
    def objection(self):
        return self._objection

    @property
    def flutter(self):
        return self._flutter

    @property
    def apktool(self):
        return self._apktool

    # setters
    @apktool.setter
    def apktool(self, apktool):
        self._apktool = apktool

    @frida.setter
    def frida(self, frida):
        self._frida = frida

    @objection.setter
    def objection(self, obj):
        self._objection = obj

    @flutter.setter
    def flutter(self, obj):
        self._flutter = obj

    def __init__(self) -> None:
        self.__init_print()
        self._drozer = drozer()
        # self.__check_prerequisites()
        self._frida_path = '~/.mmsf/utils/frida-server'
        self._apktool_path = '/usr/local/bin/apktool'
        self._apktool_jar_path = '/usr/local/bin/apktool.jar'
        # self.__init_frida()
        # self.__init_objection()
        # self.__init_reflutter()
        # self.__init_java()
        # self.__init_apktool()
        self._all_apps = self.get_all_apps()
        self._frida = {
            "mode": "-U",
            "app": "",
            "host": "127.0.0.1",
            "pause": "--no-pause"
        }
        self._objection = {
            "app": ""
        }
        self._flutter = {
            "burp": "127.0.0.1",
            "apk": "base.apk"
        }
        self._apktool = {
            "app": "",
            "path": "~/.mmsf/loot/apks/",
            "mode": "d",
            "apk": "base.apk"
        }

    def __repr__(self) -> str:
        pass

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, __o: object) -> bool:
        """Compare two class instances."""
        if __o.id == self.id:
            return True
        return False
    
    def __init_print(self):
        print(Fore.GREEN + '... MMSF Intializating ... ' + Fore.RESET)

    def __update_frida(self):
        try:
            abi = subprocess.run([self._adb, 'shell', 'getprop ro.product.cpu.abi'], stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()[0]
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
        open(self._frida_path + '.xz', 'wb').write(frida_server.content)
    
        # Decompress frida server and push it to the mobile
        subprocess.run(['xz', '-f', '-d', self._frida_path+'.xz'])
        subprocess.run([self._adb, 'push', self._frida_path, '/tmp/frida-server'], stderr=DEVNULL, stdout=DEVNULL)
        subprocess.run([self._adb, 'shell', 'chmod +x /tmp/frida-server'], stderr=DEVNULL, stdout=DEVNULL)

    def __init_frida(self):
        p = subprocess.run([self._adb, 'shell', '/tmp/frida-server &'], stderr=PIPE, stdout=DEVNULL)
        if 'already' not in p.stderr.decode():
            print(p.stderr)
            self.__update_frida()
        subprocess.run([self._adb, 'forward', 'tcp:27042', 'tcp:27042'], stderr=DEVNULL, stdout=DEVNULL)

        p = subprocess.run(['frida-ps', '-U'], stdout=PIPE, stderr=PIPE)
        if not p.stdout or p.stderr:
            print(Fore.RED + '[-] frida is missing. Check your installation... Exitting... ')
            quit()

    def __init_objection(self):
        p = subprocess.run(['objection'], stdout=PIPE, stderr=PIPE)
        if not p.stdout or p.stderr:
            print(Fore.RED + '[-] Objection is missing. Check your installation... Exitting... ')
            quit()

    def __init_reflutter(self):
        p = subprocess.run(['reflutter'], stdout=PIPE, stderr=PIPE)
        if not p.stdout or p.stderr:
            print(Fore.RED + '[-] reflutter is missing. Check your installation... Exitting... ')
            quit()

    def __init_apktool(self):
        if not subprocess.run(['apktool', '--version'], stdout=PIPE).stdout.decode():
            if os.getuid() == 0:
                self.__update_apktool()
                self.__update_apksigner()
            else:
                print(Fore.RED + '[-] sudo required to update apktool' + Fore.RESET)

    def __update_apksigner():
        subprocess.run(['sudo', 'apt-get', 'install', 'apksigner'], stderr=DEVNULL, stdout=DEVNULL)

    def __update_apktool(self):
        resp = requests.get("https://api.github.com/repos/iBotPeaches/Apktool/releases/latest")
        latest = loads(resp.content)['tag_name'][1:]
        jar_url = f'https://github.com/iBotPeaches/Apktool/releases/latest/download/apktool_{latest}.jar'
        apktool_jar = requests.get(jar_url)
        open(self._apktool_jar_path, 'wb').write(apktool_jar.content)
        apktool_wrapper_url = 'https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool'
        apktool = requests.get(apktool_wrapper_url)
        open(self._apktool_path, 'wb').write(apktool.content)
        subprocess.run(['chmod', '+x', self._apktool_jar_path], stdout=DEVNULL, stderr=DEVNULL)
        subprocess.run(['chmod', '+x', self._apktool_path], stdout=DEVNULL, stderr=DEVNULL)

    def __update_java(self):
        subprocess.run(['sudo', 'apt', 'install','default-jdk'])
        subprocess.run(['sudo', 'apt', 'instal', 'default-jre'])
        #check if succeeded and test for errors

    def __init_java(self):
        if not subprocess.run(['java', '-version'], stdout=PIPE, stderr=stdout).stdout.decode():
            if os.getuid() == 0:
                self.__update_java()
            else:
                print(Fore.RED + '[-] sudo required to update java' + Fore.RESET)        

    def __generate_sign(self):
        pwd = "123456"
        keytool_cmd = ['keytool', '-genkey', '-noprompt', '-keystore', '~/.mmsf/utils/keystore.jsk', '-alias', 'alias_name', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000', '-storepass', pwd, '-keypass', pwd, '-dname', '"CN=signer.com, OU=ID, O=IB, L=John, S=Doe, C=GB"']
        p = subprocess.run(keytool_cmd, stderr=PIPE, stdout=PIPE)
        print(p.stdout)
        print(p.stderr)
        cmd_to_run = ['apktool', 'b', '-o', 'temp.apk', self.apktool["path"]]
        subprocess.run(cmd_to_run, stderr=DEVNULL, stdout=DEVNULL)
        cmd_to_run = ['apksigner', 'sign', '--ks', '~/.mmsf/utils/keystore.jsk', '--out', self.apktool["path"].rstrip('/') + '/' + self.apktool['app'] + '_patched.apk', 'temp.apk']
        subprocess.run(cmd_to_run, input=pwd, stderr=DEVNULL, stdout=DEVNULL)

    # methods
    # Get a list of all installed apps
    def get_all_apps(self) -> list:
        final_command = self._drozer._drozer_cmd + ['-c', Commands.FIND_APP.value["cmd"], '--debug']
        return list(map(lambda x: x.split(" ")[0] ,subprocess.run(final_command, stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()[2:])) 

    # run all drozer scans
    def run_all(self):
        self._drozer.run_all()

    # Find specific app using drozer
    def find_app(self) -> list:
        self._drozer.find_app()
        
    # start activity using intent
    def start_activity(self):
        self._drozer.start_activity()
       
    # Open DeepLinks
    def open_deeplink(self):
        self._drozer.open_deeplink()

    # Sniff broadcast data
    def sniff_broadcast_data(self):
        self._drozer.sniff_broadcast_data()

    # Query the content provider
    def query_provider(self, cmd, content):
        self._drozer.content_provider = content

        if cmd == "run":
            if self._drozer.content_provider["uri"]:
                self._drozer.query_provider()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "URI", "value": self._drozer.content_provider["uri"], "description": "The Content Provider URI to be tested."},
                {"name": "PROJECTION", "value": self._drozer.content_provider["projection"], "description": "The columns to SELECT, as in 'SELECT <projection> FROM table'.", "required": False},
                {"name": "SELECTION", "value": self._drozer.content_provider["selection"], "description": "The Condition to apply to the query, as in \"WHERE <condition>\". e.g. selection \"id=?\"", "required": False},
                {"name": "SELECTION-ARGS", "value": self._drozer.content_provider["selection_args"], "description": "The parameter to replace the '?' in the selection", "required": False}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2

    # Insert Data in content provider
    def insert_provider(self, cmd, data):
        self._drozer.content_provider = data

        if cmd == "run":
            if self._drozer.content_provider["uri"] and self._drozer.content_provider["insert_values"]:
                self._drozer.insert_provider()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "URI", "value": self._drozer.content_provider["uri"], "description": "The Content Provider URI to be tested."},
                {"name": "INSERT_VALUES", "value": self._drozer.content_provider["insert_values"], "description": "The values required for insert. Choose between string, boolean, double, float, integer, long, short. e.g: string pass pass"}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2
        
    # Update data in content provider
    def update_provider(self, cmd, data):
        self._drozer.content_provider = data
        if cmd == "run":
            if self._drozer.content_provider["uri"] and self._drozer.content_provider["update_values"] and self._drozer.content_provider["selection"] and self._drozer.content_provider["selection_args"]:
                self._drozer.update_provider()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "URI", "value": self._drozer.content_provider["uri"], "description": "The Content Provider URI to be tested."},
                {"name": "UPDATE_VALUES", "value": self._drozer.content_provider["update_values"], "description": "The values required for update. Choose between string, boolean, double, float, integer, long, short. e.g: --string pass pass"},
                {"name": "SELECTION", "value": self._drozer.content_provider["selection"], "description": "The Condition to apply to the query, as in \"WHERE <condition>\". e.g. selection \"id=?\""},
                {"name": "SELECTION_ARGS", "value": self._drozer.content_provider["selection_args"], "description": "The parameter to replace the '?' in the selection"}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2
        

    # Read data using content provider
    def read_provider(self, cmd, data):
        self._drozer.content_provider = data
        if cmd == "run":
            if self._drozer.content_provider["uri"]:
                self._drozer.read_provider()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "URI", "value": self._drozer.content_provider["uri"], "description": "The Content Provider URI to be tested."}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2

    # Bypass SSL Pinning 
    def bypass_ssl_frida(self):
        cmd = ['frida', self._frida["mode"], '-f', self._frida['app'], '-l', 'Frida_Scripts/bypass_ssl_pinning_various_methods.js', self._frida["pause"]]
        print(Fore.YELLOW + "Command used: " + " ".join(cmd) + Fore.RESET)
        subprocess.Popen(cmd, stderr=DEVNULL, stdout=DEVNULL)
        sleep(5)
        p = subprocess.Popen(['ps', '-au'], stdout=subprocess.PIPE).communicate()[0]
        if self._frida["app"] in p.decode():
            print(Fore.GREEN + '[+] Command executed successfully, check your traffic!' + Fore.RESET)
        else:
            print(Fore.RED + '[-] Some error occured! Try again!' + Fore.RESET)

    # Bypass SSL Network Config
    def bypass_network_config(self):
        self.__decompile_apk()
        self.__modify_network_config()
        self.__generate_sign()

    def __decompile_apk(self):
        cmd_to_run = ["apktool", 'd', self.apktool['path'].rstrip('/') + '/' + self.apktool['apk']]
        subprocess.run(cmd_to_run, stderr=DEVNULL, stdout=DEVNULL)

    def __modify_network_config(self):
        def check_existance():
            pass

        def create():
            pass

        def modify():
            pass
        
        if not os.path.isdir(self.apktool['path'].rstrip('/') + '/' + self.apktool['apk'].rstrip('.apk')): 
            self.__decompile_apk()
        if check_existance():
            modify()
        else:
            create()
        self.__generate_sign()

    def install_apk(self):
        cmd_to_exec = [Constants.ADB, 'install', '-r', self.apktool["path"].rstrip('/') + '/' + self.apktool['app'] + '_patched.apk']
        subprocess.run(cmd_to_exec, stderr=DEVNULL, stdout=DEVNULL)

    def bypass_ssl_objection(self):
        cmd = ['objection', '-g', self._objection["app"], 'explore', '-q', '-c', 'Objection_Scripts/ssl_pinning.txt']
        print(Fore.YELLOW + "Command used: " + " ".join(cmd) + Fore.RESET)
        subprocess.Popen(cmd, stderr=DEVNULL, stdout=DEVNULL)
        sleep(5)
        p = subprocess.Popen(['ps', '-au'], stdout=subprocess.PIPE).communicate()[0]
        if self._objection["app"] in p.decode():
            print(Fore.GREEN + '[+] Command executed successfully, check your traffic!' + Fore.RESET)
        else:
            print(Fore.RED + '[-] Some error occured! Try again!' + Fore.RESET)

    # Bypass ROOT detection using frida
    def bypass_root(self):
        cmd = ['frida', self._frida["mode"], '-f', self._frida['app'], '-l', 'Frida_Scripts/antiroot_bypass.js', self._frida["pause"]]
        print(Fore.YELLOW + "Command used: " + " ".join(cmd) + Fore.RESET)
        subprocess.Popen(cmd, stderr=DEVNULL, stdout=DEVNULL)
        sleep(5)
        p = subprocess.Popen(['ps', '-au'], stdout=subprocess.PIPE).communicate()[0]
        if self._frida["app"] in p.decode():
            print(Fore.GREEN + '[+] Command executed successfully, check your traffic!' + Fore.RESET)
        else:
            print(Fore.RED + '[-] Some error occured! Try again!' + Fore.RESET)
    
    # Patch apk and sign
    def patch_apk(self):
        pass

    # Patch IPA
    def patch_ipa(self):
        pass

    # Use reflutter to patch ssl pinning apk
    def reflutter_sslpinning(self):
        cmd = ['reflutter', self._flutter["app"]]
        print(Fore.YELLOW + "Command used: " + " ".join(cmd) + Fore.RESET)
        p = subprocess.run(cmd, input=f"1".encode('UTF-8'), stderr=DEVNULL, stdout=PIPE)
        print(p.stdout.decode())

    # Antifrida bypass
    def antifrida_bypass(self):
        pass    

    # Listen for clipboard data
    def clipboard_manager(self):
        pass

    # Install burp CA as root
    def install_burp_root_ca(self):
        pass

    # Extract backup
    def extract_backup(self):
        pass

    # Pull apk from device
    def pull_apk(self):
        cmd_to_run = [Constants.ADB, 'shell', 'pm', 'list', 'packages', '-f']
        out = subprocess.run(cmd_to_run, stderr=DEVNULL, stdout=PIPE).stdout.decode()
        pass

    # Analyze Keystore
    def keystore_analyze(self):
        pass

    # Bypass Local Auth using Fingerprint
    def fingerprint_bypass(self):
        pass

def handle_query(mmsf):
    content = {
        "uri": "",
        "projection": [],
        "selection": "",
        "selection_args": []
    }
    while True:
        set_data = ["uri", "projection", "selection", "selection_args"]
        def data_completer(text, state):
            options = [i for i in set_data if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def cmd_completer(text, state):
            options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def execute(cmd, data):
            return mmsf.query_provider(cmd, data)

        readline.set_completer(cmd_completer)
        
        value = shlex.split(input('mmsf (provider/query)> '))[0].lower()
        if value == "set":
            while True:
                
                readline.set_completer(data_completer)
                inpt = shlex.split(input('mmsf (provider/query/set)> '))
                if len(inpt) > 1:
                    cmd, *args = inpt
                else:
                    cmd = inpt[0]
                    args = None
                if args:
                    if cmd.lower() == "uri":
                        content["uri"] = args[0].lower()
                    elif cmd.lower() == "projection":
                        content["projection"].append(args[0])
                    elif cmd.lower() == "selection":
                        content["selection"] = args[0]
                    elif cmd.lower() == "selection_args":
                        content["selection_args"].append(args[0])
                else:
                    if execute(cmd.lower(), content):
                        break
        else:
            if execute(value, content) == 2:
                return 1 

def handle_insert(mmsf):
    content = {
        "uri": "",
        "insert_values": [],
    }
    while True:
        set_data = ["uri", "insert_values"]
        def data_completer(text, state):
            options = [i for i in set_data if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def cmd_completer(text, state):
            options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def execute(cmd, data):
            return mmsf.insert_provider(cmd, data)

        readline.set_completer(cmd_completer)
        
        value = shlex.split(input('mmsf (provider/insert)> '))[0].lower()
        if value == "set":
            while True:
                
                readline.set_completer(data_completer)
                inpt = shlex.split(input('mmsf (provider/insert/set)> '))
                if len(inpt) > 1:
                    cmd, *args = inpt
                else:
                    cmd = inpt[0]
                    args = None
                if args:
                    if cmd.lower() == "uri":
                        content["uri"] = args[0].lower()
                    elif cmd.lower() == "insert_values":
                        args[0] = f'--{args[0]}'
                        content["insert_values"].extend(' '.join(args))
                else:
                    if execute(cmd.lower(), content):
                        break
        else:
            if execute(value, content) == 2:
                return 1 

def handle_read(mmsf):
    content = {
        "uri": ""
    }
    while True:
        set_data = ["uri"]
        def data_completer(text, state):
            options = [i for i in set_data if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def cmd_completer(text, state):
            options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def execute(cmd, data):
            return mmsf.read_provider(cmd, data)

        readline.set_completer(cmd_completer)
        
        value = shlex.split(input('mmsf (provider/read)> '))[0].lower()
        if value == "set":
            while True:
                
                readline.set_completer(data_completer)
                inpt = shlex.split(input('mmsf (provider/read/set)> '))
                if len(inpt) > 1:
                    cmd, *args = inpt
                else:
                    cmd = inpt[0]
                    args = None
                if cmd.lower() == "uri"  and args:
                    content["uri"] = args[0].lower()
                else:
                    if execute(cmd.lower(), content):
                        break
        else:
            if execute(value, content) == 2:
                return 1 

def handle_update(mmsf):
    content = {
        "uri": "",
        "selection": "",
        "selection_args": [],
        "update_values": []
    }
    while True:
        set_data = ["uri", "update_values", "selection", "selection_args"]
        def data_completer(text, state):
            options = [i for i in set_data if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def cmd_completer(text, state):
            options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def execute(cmd, data):
            return mmsf.update_provider(cmd, data)

        readline.set_completer(cmd_completer)
        
        value = shlex.split(input('mmsf (provider/update)> '))[0].lower()
        if value == "set":
            while True:
                
                readline.set_completer(data_completer)
                inpt = shlex.split(input('mmsf (provider/update/set)> '))
                if len(inpt) > 1:
                    cmd, *args = inpt
                else:
                    cmd = inpt[0]
                    args = None
                if args:
                    if cmd.lower() == "uri":
                        content["uri"] = args[0].lower()
                    elif cmd.lower() == "update_values":
                        args[0] = f'--{args[0]}'
                        content["update_values"].extend(" ".join(args))
                    elif cmd.lower() == "selection":
                        content["selection"] = args[0]
                    elif cmd.lower() == "selection_args":
                        content["selection_args"].append(args[0])
                else:
                    if execute(cmd.lower(), content):
                        break
        else:
            if execute(value, content) == 2:
                return 1 

def execute_cmd(mmsf, apps, cmd):
    if cmd == "scan":
        set_data = ["outdir", "app_name"] + apps

        # waiting for input 
        while True:

            # set the autocompleters
            def data_completer(text, state):
                options = [i for i in set_data if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def cmd_completer(text, state):
                options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            # The commands to be executed
            def execute(cmd):
                if cmd == "run":
                    if mmsf.full_path and mmsf.app_name:
                        mmsf.run_all()
                        return 1
                    else:
                        print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                        return 0
                elif cmd == "show":
                    print_show_table([
                        {"name": "OUTDIR", "value": mmsf.full_path, "description": "The directory where the scans will save the data."},
                        {"name": "APP_NAME", "value": mmsf.app_name, "description": "The name of the application to be scanned."}])
                    return 0
                elif cmd == "exit":
                    quit()
                elif cmd == "back":
                    back()
                    return 2
                
            readline.set_completer(cmd_completer)

            # get user input
            value = shlex.split(input('mmsf (scan)> '))[0].lower()
            if value == "back":
                back()
                break
            elif value == "set":
                values = 0
                if mmsf.full_path:
                    values += 1
                if mmsf.app_name:
                    values += 1
                # wait for data to be set
                while True:
                    readline.set_completer(data_completer)
                    inpt = shlex.split(input('mmsf (scan/set)> '))
                    cmd = inpt[0]
                    if len(inpt) > 1:
                        if cmd.lower() == "outdir":
                            values += 1 
                            mmsf.full_path = inpt[1]
                        elif cmd.lower() == "app_name":
                            values += 1
                            mmsf.app_name = inpt[1]
                    elif len(inpt) < 2 and inpt[0] in Constants.MMSF_COMMANDS:
                        if execute(cmd.lower()):
                            break
            else:
                if execute(value) == 2:
                    break 
    elif cmd == "find":
        while True:
            set_data = ["filter"]
            def data_completer(text, state):
                options = [i for i in set_data if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def cmd_completer(text, state):
                options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def execute(cmd):
                if cmd == "run":
                    if mmsf.query:
                        apps = mmsf.find_app()
                        # get details of specific app
                        print(Fore.BLUE + "Want to find details of specific app? Enter the application name (press tab to autocomplete) or enter 'exit' to exit!" + Fore.RESET)
                        while True:
                            def completer(text, state):
                                options = [i for i in apps if i.startswith(text)]
                                if state < len(options):
                                    return options[state]
                                else:
                                    return None

                            readline.parse_and_bind("tab: complete")
                            readline.set_completer(completer)
                            value = shlex.split(input('mmsf (find/details)> '))[0]
                            if value not in apps or value == "exit":
                                back()
                                return 0
                            final_command = mmsf.mmsf_cmd + ['-c', Commands.COMMAND_PACKAGEINFO.value["cmd"] + value, '--debug']
                            output = subprocess.run(final_command, stdout=PIPE, stderr=DEVNULL).stdout.decode()
                            print(Fore.GREEN + "Details: \n" + output + Fore.RESET)
                            return 1
                    else:
                        print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                        return 0                 
                elif cmd == "show":
                    print_show_table([{"name": "FILTER", "value": mmsf.query, "description": "The query used to find the apps."}])
                    return 0
                elif cmd == "exit":
                    quit()
                elif cmd == "back":
                    back()
                    return 2

            readline.set_completer(cmd_completer)

            value = shlex.split(input('mmsf (find)> '))[0].lower()
            if value == "back":
                back()
                break
            elif value == "set":
                values = 0
                while True:
                    if values == 1:
                        break
                    readline.set_completer(data_completer)
                    cmds = shlex.split(input('mmsf (find/set)> '))
                    if len(cmds) == 2:
                        cmd, *argv = cmds
                    else:
                        cmd = cmds[0]
                    if cmd.lower() == "filter" and args:
                        values += 1 
                        mmsf.query = argv[0].lower()
                    else:
                        if execute(cmd.lower()):
                            break
            else:
                if execute(value) == 2:
                    break 
    elif cmd == "provider":
        modules = ["query", "update", "insert", "read"]
        descriptions = [
            "Query the exported content provider to extract data.", 
            "Update the exported content provider data",
            "Insert data in the exported content provider",
            "Read file using the exported content provider"]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (provider)> '))
            if len(input_val) < 1:
                continue
            if len(input_val) > 2:
                continue
            elif input_val[0].lower() == "exit":
                quit()
            elif input_val[0].lower() == "listmodules":
                listmodules(modules, descriptions)
            elif input_val[0].lower() == "usemodule":
                action = input_val[1].lower()
                if action not in modules:
                    unknown_cmd()
                elif action == "query":
                    handle_query(mmsf)
                elif action == "insert":
                    handle_insert(mmsf)
                else:
                    handle_update(mmsf)
            elif input_val[0].lower() == "back":
                back()
                break
    elif cmd == "deeplink":
        while True:
            set_data = ["data_uri"]
            def data_completer(text, state):
                options = [i for i in set_data if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def cmd_completer(text, state):
                options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def execute(cmd):
                if cmd == "run":
                    if mmsf.deeplink:
                        mmsf.openDeeplink()
                        return 1
                    else:
                        print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                        return 0                 
                elif cmd == "show":
                    print_show_table([{"name": "DATA_URI", "value": mmsf.deeplink, "description": "The URI used to open the application as deeplink"}])
                    return 0
                elif cmd == "exit":
                    quit()
                elif cmd == "back":
                    back()
                    return 2

            readline.set_completer(cmd_completer)

            value = shlex.split(input('mmsf (deeplink)> '))[0].lower()
            if value == "set":
                values = 0
                if mmsf.deeplink:
                    values += 1
                while True:
                    
                    readline.set_completer(data_completer)
                    cmds = shlex.split(input('mmsf (deeplink/set)> '))
                    if len(cmds) == 2:
                        cmd, *args = cmds
                    else:
                        cmd = cmds[0]
                        args = None
                    if cmd.lower() == "data_uri" and args is not None:
                        values += 1
                        mmsf.deeplink = args[0].lower()
                    else:
                        if execute(cmd.lower()):
                            break
            else:
                if execute(value) == 2:
                    break
    elif cmd == "intent":
        while True:
            set_data = ["data_uri", "extra", "component", "action", "mimetype", "app_name"] + apps
            actions = ["android.intent.action.VIEW", "android.intent.action.MAIN", "android.intent.action.SEND", "android.intent.action.SENDTO", "android.intent.action.SEARCH"]
            extras_type = ["parcelable", "long", "byte", "double", "charsequence", "boolean", "int", "Bundle", "string", "char", "serializable", "short"]
            
            def extras_type_completer(text, state):
                options = [i for i in extras_type if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def data_completer(text, state):
                options = [i for i in set_data + actions if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def cmd_completer(text, state):
                options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def execute(cmd):
                if cmd == "run":
                    if mmsf.app_name and mmsf.component:
                        mmsf.startActivity()
                        return 1
                    else:
                        print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                        return 0                 
                elif cmd == "show":
                    print_show_table([{"name": "APP_NAME", "value": mmsf.app_name, "description": "The package name: e.g. com.example.android"},
                    {"name": "COMPONENT", "value": mmsf.component, "description": "The exported component: e.g. com.example.com.MainActivity"},
                    {"name": "EXTRA", "value": mmsf.extras, "description": "The extra values to be passed to the intent: e.g. string url file:///etc/hosts", "required": False},
                    {"name": "DATA_URI", "value": mmsf.deeplink, "description": "The URI used to open the application as deeplink", "required": False},
                    {"name": "ACTION", "value": mmsf.intent_action, "description": "The intent action (may be custom actions: e.g. theAction): e.g. android.intent.action.VIEW", "required": False},
                    {"name": "MIMETYPE", "value": mmsf.mimetype, "description": "The mimetype passed to the intent", "required": False}])
                    return 0
                elif cmd == "exit":
                    quit()
                elif cmd == "back":
                    back()
                    return 2

            readline.set_completer(cmd_completer)
            extra = []
            value = shlex.split(input('mmsf (intent)> '))[0].lower()
            if value == "set":
                while True:
                    readline.set_completer(data_completer)
                    cmds = shlex.split(input('mmsf (intent/set)> '))
                    if len(cmds) >= 2:
                        cmd, *args = cmds
                    else:
                        cmd = cmds[0]
                        args = None
                    if cmd.lower() == "extra":
                        
                        while True:
                            readline.set_completer(extras_type_completer)
                            cmdds = shlex.split(input('mmsf (intent/set/extra)> '))
                            if len(cmdds) < 2:
                                if len(cmdds) == 1:
                                    if execute(cmdds[0].lower()):
                                        break
                                else:
                                    print(Fore.RED + "[-] The expected arguments should be in form of TYPE KEY VALUE" + Fore.RESET)
                            elif len(cmdds) == 2:
                                if cmdds[0] == "remove":
                                    extras = [i for i in extra if cmdds[1] not in i]
                                    extra = extras
                                    break
                            else:
                                extra += [f"{cmdds[0]} {cmdds[1]} {cmdds[2]}"]
                                break
                        mmsf.extras = extra
                    elif cmd.lower() == "action" and args:
                        mmsf.intent_action = args[0].lower()
                    elif cmd.lower() == "component" and args:
                        mmsf.component = args[0]
                    elif cmd.lower() == "app_name" and args:
                        mmsf.app_name = args[0].lower()
                    elif cmd.lower() == "mimetype" and args:
                        mmsf.mimetype = args[0].lower()
                    elif cmd.lower() == "data_uri" and args:
                        mmsf.deeplink = args[0].lower()
                    else:
                        if execute(cmd.lower()):
                            break
            else:
                if execute(value) == 2:
                    break                  
    elif cmd == "broadcast":
        while True:
            set_data = ["data_uri", "extra", "component", "action", "mimetype", "app_name"] + apps
            actions = ["android.intent.action.VIEW", "android.intent.action.MAIN", "android.intent.action.SEND", "android.intent.action.SENDTO", "android.intent.action.SEARCH"]
            extras_type = ["parcelable", "long", "byte", "double", "charsequence", "boolean", "int", "Bundle", "string", "char", "serializable", "short"]
            
            def extras_type_completer(text, state):
                options = [i for i in extras_type if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def data_completer(text, state):
                options = [i for i in set_data + actions if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def cmd_completer(text, state):
                options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def execute(cmd):
                if cmd == "run":
                    if mmsf.app_name and mmsf.component:
                        mmsf.sendBroadcast()
                        return 1
                    else:
                        print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                        return 0                 
                elif cmd == "show":
                    print_show_table([{"name": "APP_NAME", "value": mmsf.app_name, "description": "The package name: e.g. com.example.android"},
                    {"name": "COMPONENT", "value": mmsf.component, "description": "The exported component: e.g. com.example.com.MainActivity"},
                    {"name": "EXTRA", "value": mmsf.extras, "description": "The extra values to be passed to the intent: e.g. string url file:///etc/hosts", "required": False},
                    {"name": "DATA_URI", "value": mmsf.deeplink, "description": "The URI used to open the application as deeplink", "required": False},
                    {"name": "ACTION", "value": mmsf.intent_action, "description": "The intent action (may be custom actions: e.g. theAction): e.g. android.intent.action.VIEW", "required": False},
                    {"name": "MIMETYPE", "value": mmsf.mimetype, "description": "The mimetype passed to the intent", "required": False}])
                    return 0
                elif cmd == "exit":
                    quit()
                elif cmd == "back":
                    back()
                    return 2

            readline.set_completer(cmd_completer)
            extra = []
            value = shlex.split(input('mmsf (broadcast)> '))[0].lower()
            if value == "set":
                while True:

                    readline.set_completer(data_completer)
                    cmds = shlex.split(input('mmsf (broadcast/set)> '))
                    if len(cmds) >= 2:
                        cmd, *args = cmds
                    else:
                        cmd = cmds[0]
                        args = None
                    if cmd.lower() == "extra":
                        while True:
                            readline.set_completer(extras_type_completer)
                            cmdds = shlex.split(input('mmsf (broadcast/set/extra)> '))
                            if len(cmdds) < 2:
                                if len(cmdds) == 1:
                                    if execute(cmdds[0].lower()):
                                        break
                                else:
                                    print(Fore.RED + "[-] The expected arguments should be in form of TYPE KEY VALUE" + Fore.RESET)
                            elif len(cmdds) == 2:
                                if cmdds[0] == "remove":
                                    extras = [i for i in extra if cmdds[1] not in i]
                                    extra = extras
                                    break
                            else:
                                extra += [f"{cmdds[0]} {cmdds[1]} {cmdds[2]}"]
                                break
                        mmsf.extras = extra
                    elif cmd.lower() == "action" and args:
                        mmsf.intent_action = args[0].lower()
                    elif cmd.lower() == "component" and args:
                        mmsf.component = args[0]
                    elif cmd.lower() == "app_name" and args:
                        mmsf.app_name = args[0].lower()
                    elif cmd.lower() == "mimetype" and args:
                        mmsf.mimetype = args[0].lower()
                    elif cmd.lower() == "data_uri" and args:
                        mmsf.deeplink = args[0].lower()
                    else:
                        if execute(cmd.lower()):
                            break
            else:
                if execute(value) == 2:
                    break                  
    elif cmd == "sniff":
        while True:
            set_data = ["data_authority", "data_path", "data_scheme", "data_type", "action", "category"]

            def data_completer(text, state):
                options = [i for i in set_data if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def cmd_completer(text, state):
                options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def execute(cmd):
                if cmd == "run":
                    if mmsf.intent_action or mmsf.category or mmsf.data:
                        mmsf.sniffData()
                        return 1
                    else:
                        print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                        return 0                 
                elif cmd == "show":
                    print_show_table([{"name": "ACTION", "value": mmsf.intent_action, "description": "The action to match the broadcast receiver: e.g. android.intent.action.BATTERY_CHANGED", "required": False},
                    {"name": "CATEGORY", "value": mmsf.category, "description": "The category to match the broadcast receiver: e.g. android.intent.category.LAUNCHER", "required": False},
                    {"name": "DATA_AUTHORITY", "value": mmsf.data["authority"], "description": "The authority used in URI (HOST PORT): e.g. com.mwr.dz 31415", "required": False},
                    {"name": "DATA_PATH", "value": mmsf.data["path"], "description": "The path used in URI: e.g. /sensitive-data/", "required": False},
                    {"name": "DATA_SCHEME", "value": mmsf.data["scheme"], "description": "The scheme used in URI: e.g. scheme://", "required": False},
                    {"name": "DATA_TYPE", "value": mmsf.data["type"], "description": "The mimetype used in URI", "required": False}])
                    return 0
                elif cmd == "exit":
                    quit()
                elif cmd == "back":
                    back()
                    return 2

            readline.set_completer(cmd_completer)
            data = shlex.split(input('mmsf (sniff)> '))
            if len(data) > 0:
                value = data[0].lower()
            else:
                continue
            sniffdata = {
                "authority": "",
                "scheme": "",
                "path": "",
                "type": ""
            }
            if value == "set":
                while True:

                    readline.set_completer(data_completer)
                    cmds = shlex.split(input('mmsf (sniff/set)> '))
                    if len(cmds) >= 2:
                        cmd, *args = cmds
                    else:
                        cmd = cmds[0]
                        args = None
                    if cmd.lower() == "action" and args:
                        mmsf.intent_action = args[0]
                    elif cmd.lower() == "category" and args:
                        mmsf.category = args[0]
                    elif cmd.lower() == "data_authority" and args:
                        sniffdata["authority"] = f'{args[0]} {args[1]}'
                        mmsf.data = sniffdata
                    elif cmd.lower() == "data_path" and args:
                        sniffdata["path"] = args[0]
                        mmsf.data = sniffdata
                    elif cmd.lower() == "data_scheme" and args:
                        sniffdata["scheme"] = args[0]
                        mmsf.data = sniffdata
                    elif cmd.lower() == "data_type" and args:
                        sniffdata["type"] = args[0]
                        mmsf.data = sniffdata
                    else:
                        if execute(cmd.lower()):
                            break
            else:
                if execute(value) == 2:
                    break
    elif cmd == "sslpinning":
        def handle_frida():
            frida_data = {
                "mode": "-U",
                "app": "",
                "host": "127.0.0.1",
                "pause": "--no-pause"
            }
            while True:
                set_data = ["mode", "app", "host", "pause"]
                def data_completer(text, state):
                    options = [i for i in set_data if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def cmd_completer(text, state):
                    options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def execute(cmd):
                    if cmd == "run":
                        if mmsf.frida["mode"] == '-R':
                            if not mmsf.frida["host"]:
                                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                                return 0    
                        if mmsf.frida["app"]:
                            mmsf.bypass_ssl_frida()
                            return 1
                        else:
                            print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                            return 0              
                    elif cmd == "show":
                        print_show_table([
                            {"name": "MODE", "value": "SERIAL" if mmsf.frida["mode"] == "-U" else "REMOTE", "description": "The Type of Connection with frida-server: Serial or Remote. Default set to Serial", "required": False},
                            {"name": "APP", "value": mmsf.frida["app"], "description": "The application package name: com.example.android"},
                            {"name": "HOST", "value": mmsf.frida["host"], "description": "If MODE set to Remote, specify HOST. Default set to 127.0.0.1", "required": False},
                            {"name": "PAUSE", "value": "FALSE" if mmsf.frida["pause"] == "--no-pause" else "TRUE" , "description": "The application should be paused on start? Default set to FALSE", "required": False}])
                        return 0
                    elif cmd == "exit":
                        quit()
                    elif cmd == "back":
                        back()
                        return 2

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (sslpinning/frida)> '))[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (sslpinning/frida/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "mode"  and args:
                            mode = '-U'
                            if args[0].lower == "remote":
                                mode = '-R'
                            elif args[0] == "serial":
                                mode = '-U'
                            frida_data["mode"] = mode
                        elif cmd.lower() == "app" and args:
                            frida_data["app"] = args[0]
                        elif cmd.lower() == "host" and args:
                            frida_data["host"] = args[0]
                        elif cmd.lower() == "pause" and args:
                            if args[0].lower() == "true":
                                frida_data["pause"] = ""
                        else:
                            mmsf.frida = frida_data
                            if execute(cmd.lower()):
                                break
                else:
                    if execute(value) == 2:
                        return 1 

        def handle_objection():
            objection_data = {
                "app": "",
            }
            while True:
                set_data = ["app"]
                def data_completer(text, state):
                    options = [i for i in set_data if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def cmd_completer(text, state):
                    options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def execute(cmd):
                    if cmd == "run": 
                        if mmsf.objection["app"]:
                            mmsf.bypass_ssl_objection()
                            return 1
                        else:
                            print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                            return 0              
                    elif cmd == "show":
                        print_show_table([
                            {"name": "APP", "value": mmsf.objection["app"], "description": "The application package name: com.example.android"}])
                        return 0
                    elif cmd == "exit":
                        quit()
                    elif cmd == "back":
                        back()
                        return 2

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (sslpinning/objection)> '))[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (sslpinning/objection/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "app" and args:
                            objection_data["app"] = args[0]
                        else:
                            mmsf.objection = objection_data
                            if execute(cmd.lower()):
                                break
                else:
                    if execute(value) == 2:
                        return 1 

        def handle_flutter():
            flutter_data = {
                "burp": "127.0.0.1",
                "apk": "base.apk"
            }
            while True:
                set_data = ["app"]
                def data_completer(text, state):
                    options = [i for i in set_data if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def cmd_completer(text, state):
                    options = [i for i in Constants.MMSF_COMMANDS if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def execute(cmd):
                    if cmd == "run": 
                        if mmsf.flutter["app"]:
                            mmsf.reflutter_sslpinning()
                            return 1
                        else:
                            print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                            return 0              
                    elif cmd == "show":
                        print_show_table([
                            {"name": "APP", "value": mmsf.flutter["app"], "description": "The application apk: main.apk"},
                            {"name": "BURP", "value": mmsf.flutter["burp"], "description": "The BurpSuite IP, default to 127.0.0.1", "required": False}])
                        return 0
                    elif cmd == "exit":
                        quit()
                    elif cmd == "back":
                        back()
                        return 2

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (sslpinning/flutter)> '))[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (sslpinning/flutter/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "app" and args:
                            flutter_data["app"] = args[0]
                        elif cmd.lower() == "burp" and args:
                            flutter_data["burp"] = args[0]
                        else:
                            mmsf.flutter = flutter_data
                            if execute(cmd.lower()):
                                break
                else:
                    if execute(value) == 2:
                        return 1 

        def handle_burp_ca():
            pass

        modules = ["objection", "frida", "flutter", "burp_ca"]
        descriptions = [
            "Bypass the SSL Pinning using Objection", 
            "Frida Script to bypass the SSL Pinning",
            "Patch Flutter Applications",
            "Push the Burp CA to the Trusted ROOT CAs"]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (sslpinning)> '))
            if len(input_val) < 1:
                continue
            if len(input_val) > 2:
                continue
            elif input_val[0].lower() == "exit":
                quit()
            elif input_val[0].lower() == "listmodules":
                listmodules(modules, descriptions)
            elif input_val[0].lower() == "usemodule":
                action = input_val[1].lower()
                if action not in modules:
                    unknown_cmd()
                elif action == "objection":
                    handle_objection()
                elif action == "frida":
                    handle_frida()
                elif action == "flutter":
                    handle_flutter()
                elif action == "burp_ca":
                    handle_burp_ca()
            elif input_val[0].lower() == "back":
                back()
                break
def main():

    mmsf = MassiveMobileSecurityFramework()
    apps = mmsf.all_apps
    initial_commands = ["usemodule", "exit", "listmodules"]
    readline.parse_and_bind("tab: complete")
    modules = ["scan", "broadcast", "intent", "provider", "find", "deeplink", "sniff", "sslpinning"]
    descriptions = [
        "Scan the application to retrieve crucial information such as exported activities, path traversal, SQL injections, attack vector and so on.", 
        "Send a broadcast intent.",
        "Start an intent using supplied values like: extra values, action, mimetype or data.",
        "Exploit the exported content provider to extract data.",
        "Find the package name of an application and/or its details by supplying a filter keyword.", 
        "Launch a deeplink with supplied value",
        "Sniffing a broadcast intent",
        "Bypass the SSL Pinning mechanism through different methods"]

    while True:
        def init_completer(text, state):
                options = [i for i in initial_commands if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

        readline.set_completer(init_completer)

        input_val = shlex.split(input('mmsf> '))
        if len(input_val) < 1:
            continue
        if len(input_val) > 2:
            unknown_cmd()
        elif input_val[0].lower() == "exit":
            quit()
        elif input_val[0].lower() == "listmodules":
            listmodules(modules, descriptions)
        elif input_val[0].lower() == "usemodule":
            action = input_val[1].lower()
            if action not in modules:
                unknown_cmd()
            else:
                execute_cmd(mmsf, apps, action)

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Type \'exit\' to exit')
    
if __name__ == "__main__":
    signal(SIGINT, handler)
    main()