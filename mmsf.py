#!/usr/bin/python3

import os
import re
from asyncio.subprocess import DEVNULL
import subprocess
from subprocess import PIPE
import warnings
from colorama import Fore
import readline
import shlex
from signal import signal, SIGINT

from Classes.mmsf_drozer import drozer
from Classes.commands import Commands
from Classes.constants import Constants
from Classes.mmsf_apktool import apktool
from Classes.mmsf_frida import Frida
from Classes.mmsf_objection import objection
from Classes.mmsf_flutter import reflutter
from Classes.utils import *

warnings.filterwarnings("ignore")
# Set the unbuffered output
os.environ.setdefault('PYTHONUNBUFFERED', '1')

class MassiveMobileSecurityFramework:
    id: str
    _drozer: drozer
    _frida: Frida
    _objection: objection
    _reflutter: reflutter
    _apktool: apktool

    @property
    def all_apps(self):
        return self._all_apps

    @all_apps.setter
    def all_apps(self, data):
        self._all_apps = data

    def __init__(self) -> None:
        self.__init_print()
        self.__check_prerequisites()
        self.__init_dirs()
        self.__init_frameworks()
        self._all_apps = self.get_all_apps()

    def __check_prerequisites(self):
        packages = ['apktool', 'apksigner', 'java', 'drozer', 'reflutter', 'objection', 'frida']
        not_installed = []
        for package in packages:
            try:
                subprocess.run([package], stderr=PIPE, stdout=PIPE)
            except Exception:
                not_installed.append(package)
        for package in not_installed:
            print(Fore.RED + "[-] " + package + ' is not installed!' + Fore.RESET)
        if len(not_installed):
            print(Fore.RED + "Please use mmsfupdate first!" + Fore.RESET)
            quit()
        
    def __init_frameworks(self):
        self._drozer = drozer()
        self._frida = Frida()
        self._objection = objection()
        self._reflutter = reflutter()
        self._apktool = apktool()

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

    def __mkdir(self, path):
        if not os.path.isdir(path):
            try:
                os.mkdir(path)
            except OSError as e:
                print(Fore.LIGHTBLUE_EX + '[DEBUG] ' + e + Fore.RESET)

    def __init_dirs(self):
        for path in (Constants):
            if path.name.startswith('DIR_'):
                self.__mkdir(path.value)

    # methods
    # Get a list of all installed apps
    def get_all_apps(self) -> list:
        final_command = self._drozer._drozer_cmd + ['-c', Commands.FIND_APP.value["cmd"], '--debug']
        return list(map(lambda x: x.split(" ")[0] ,subprocess.run(final_command, stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()[2:])) 

    # run all drozer scans
    def run_all(self, cmd, data):
        self._drozer.full_path = data["full_path"]
        self._drozer.app_name = data["app_name"]

        if cmd == "run":
            if self._drozer.full_path and self._drozer.app_name:
                self._drozer.run_all()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0
        elif cmd == "show":
            print_show_table([
                {"name": "OUTDIR", "value": self._drozer.full_path, "description": "The directory where the scans will save the data."},
                {"name": "APP_NAME", "value": self._drozer.app_name, "description": "The name of the application to be scanned."}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2

    # Find specific app using drozer
    def find_app(self, cmd, data) -> list:
        apps = data["apps"]
        self._drozer.find_app_query = data["query"]
        if cmd == "run":
            if self._drozer.find_app_query:
                self._drozer.find_app()

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
                    final_command = self._drozer._drozer_cmd + ['-c', Commands.COMMAND_PACKAGEINFO.value["cmd"] + value, '--debug']
                    output = subprocess.run(final_command, stdout=PIPE, stderr=DEVNULL).stdout.decode()
                    print(Fore.GREEN + "Details: \n" + output + Fore.RESET)
                    return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0                 
        elif cmd == "show":
            print_show_table([{"name": "FILTER", "value": self._drozer.find_app_query, "description": "The query used to find the apps."}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2
        
    # start activity using intent
    def start_activity(self, cmd, data):
        self._drozer.activity = data
        if cmd == "run":
            if self._drozer.activity["app_name"] and self._drozer.activity["component"]:
                self._drozer.start_activity()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0                 
        elif cmd == "show":
            print_show_table([{"name": "APP_NAME", "value": self._drozer.activity["app_name"], "description": "The package name: e.g. com.example.android"},
            {"name": "COMPONENT", "value": self._drozer.activity["component"], "description": "The exported component: e.g. com.example.com.MainActivity"},
            {"name": "EXTRA", "value": self._drozer.activity["extras"], "description": "The extra values to be passed to the intent: e.g. string url file:///etc/hosts", "required": False},
            {"name": "DATA_URI", "value": self._drozer.activity["deeplink"], "description": "The URI used to open the application as deeplink", "required": False},
            {"name": "ACTION", "value": self._drozer.activity["intent_action"], "description": "The intent action (may be custom actions: e.g. theAction): e.g. android.intent.action.VIEW", "required": False},
            {"name": "MIMETYPE", "value": self._drozer.activity["mimetype"], "description": "The mimetype passed to the intent", "required": False}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2

    # start activity using intent
    def send_broadcast(self, cmd, data):
        self._drozer.activity = data
        if cmd == "run":
            if (self._drozer.activity["app_name"] and self._drozer.activity["component"]) or self._drozer.activity["intent_action"]:
                self._drozer.send_broadcast()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0                 
        elif cmd == "show":
            print_show_table([
            {"name": "COMPONENT", "value": self._drozer.activity["app_name"]+ " " + self._drozer.activity["component"], "description": "The exported component: e.g. com.example.com com.example.com.BroadCastActivity", "required": False},
            {"name": "EXTRA", "value": self._drozer.activity["extras"], "description": "The extra values to be passed to the intent: e.g. string url file:///etc/hosts", "required": False},
            {"name": "DATA_URI", "value": self._drozer.activity["deeplink"], "description": "The URI used to open the application as deeplink", "required": False},
            {"name": "ACTION", "value": self._drozer.activity["intent_action"], "description": "The intent action (may be custom actions: e.g. theAction): e.g. android.intent.action.VIEW", "required": False},
            {"name": "MIMETYPE", "value": self._drozer.activity["mimetype"], "description": "The mimetype passed to the intent", "required": False}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2   
       
    # Open DeepLinks
    def open_deeplink(self, cmd, data):
        self._drozer.activity["deeplink"] = data
        if cmd == "run":
            if self._drozer.activity["deeplink"]:
                self._drozer.open_deeplink()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0                 
        elif cmd == "show":
            print_show_table([{"name": "DATA_URI", "value": self._drozer.activity["deeplink"], "description": "The URI used to open the application as deeplink"}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2
        self._drozer.open_deeplink()

    # Sniff broadcast data
    def sniff_broadcast_data(self, cmd, data):
        self._drozer.sniff_data = data
        if cmd == "run":
            if self._drozer.sniff_data["intent_action"] or self._drozer.sniff_data["category"] or (self._drozer.sniff_data["authority"] and self._drozer.sniff_data["scheme"]):
                self._drozer.sniff_broadcast_data()
                return 1
            else:
                print(Fore.RED + "[-] Set any of the ACTION, CATEGORY or DATA values!" + Fore.RESET)
                return 0                 
        elif cmd == "show":
            print_show_table([{"name": "ACTION", "value": self._drozer.sniff_data["intent_action"] , "description": "The action to match the broadcast receiver: e.g. android.intent.action.BATTERY_CHANGED", "required": False},
            {"name": "CATEGORY", "value": self._drozer.sniff_data["category"], "description": "The category to match the broadcast receiver: e.g. android.intent.category.LAUNCHER", "required": False},
            {"name": "DATA_AUTHORITY", "value": self._drozer.sniff_data["authority"], "description": "The authority used in URI (HOST PORT): e.g. com.mwr.dz 31415", "required": False},
            {"name": "DATA_PATH", "value": self._drozer.sniff_data["path"], "description": "The path used in URI: e.g. /sensitive-data/", "required": False},
            {"name": "DATA_SCHEME", "value": self._drozer.sniff_data["scheme"], "description": "The scheme used in URI: e.g. scheme://", "required": False},
            {"name": "DATA_TYPE", "value": self._drozer.sniff_data["type"], "description": "The mimetype used in URI", "required": False}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2


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
    def bypass_ssl_frida(self, cmd, data):
        self._frida.config = data
        if cmd == "run":
            if self._frida.config["mode"] == '-R':
                if not self._frida.config["host"]:
                    print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                    return 0    
            if self._frida.config["app"]:
                self._frida.bypass_ssl()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "MODE", "value": "SERIAL" if self._frida.config["mode"] == "-U" else "REMOTE", "description": "The Type of Connection with frida-server: Serial or Remote. Default set to Serial", "required": False},
                {"name": "APP", "value": self._frida.config["app"], "description": "The application package name: com.example.android"},
                {"name": "HOST", "value": self._frida.config["host"], "description": "If MODE set to Remote, specify HOST. Default set to 127.0.0.1", "required": False},
                {"name": "PAUSE", "value": "FALSE" if self._frida.config["pause"] == "--no-pause" else "TRUE" , "description": "The application should be paused on start? Default set to FALSE", "required": False}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2

    # Bypass SSL Network Config
    def bypass_network_config(self, cmd, data):
        self._apktool.config["path"] = data["path"]
        self._apktool.config["app"] = data["app"]
        if cmd == "run": 
            if self._apktool.config["app"]:
                if not self.__exists_apk():
                    self.pull_apk(self._apktool.config["app"])
                if not self.__is_decompiled():
                    self.__decompile_apk()
                self.__modify_network_config()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APP", "value": self._apktool.config["app"], "description": "The application package: com.example.android"},
                {"name": "PATH", "value": self._apktool.config["path"], "description": "The location of the apk, default to ~/.mmsf/apks/", "required": False}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2

    def __is_decompiled(self):
        return os.path.isdir(os.path.join(self._apktool.config["path"], self._apktool.config["apk"]))

    def __exists_apk(self):
        return os.path.isfile(os.path.join(self._apktool.config['path'], self._apktool.config['apk']+ '.apk'))

    def __decompile_apk(self):
        print(Fore.GREEN + '[*] Decompiling apk..' + Fore.RESET)
        self._apktool._decompile_apk()

    def __modify_network_config(self):
        self._apktool._modify_network_config()

    def bypass_ssl_objection(self):
        self._objection.bypass_ssl_pinning()

    # Bypass ROOT detection using frida
    def bypass_root_frida(self, cmd, data):
        self._frida.config = data
        if cmd == "run":
            if self._frida.config["mode"] == '-R':
                if not self._frida.config["host"]:
                    print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                    return 0    
            if self._frida.config["app"]:
                self._frida.bypass_root()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "MODE", "value": "SERIAL" if self._frida.config["mode"] == "-U" else "REMOTE", "description": "The Type of Connection with frida-server: Serial or Remote. Default set to Serial", "required": False},
                {"name": "APP", "value": self._frida.config["app"], "description": "The application package name: com.example.android"},
                {"name": "HOST", "value": self._frida.config["host"], "description": "If MODE set to Remote, specify HOST. Default set to 127.0.0.1", "required": False},
                {"name": "PAUSE", "value": "FALSE" if self._frida.config["pause"] == "--no-pause" else "TRUE" , "description": "The application should be paused on start? Default set to FALSE", "required": False}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2
    
    def bypass_root_objection_android(self, cmd, data):
        self._objection._config["app"] = data["app"]
        if cmd == "run": 
            if self._objection._config["app"]:
                self._objection.bypass_root_detection_android()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APP", "value": self._objection._config["app"], "description": "The application package name: com.example.android"}])
            return 0
        elif cmd == "exit":
            quit()
        elif cmd == "back":
            back()
            return 2

    # Patch apk and sign
    def patch_apk(self):
        pass

    # Patch IPA
    def patch_ipa(self):
        pass

    # Use reflutter to patch ssl pinning apk
    def reflutter_sslpinning(self, cmd, data):
        self._reflutter.bypass_ssl_pinning()

    # Antifrida bypass
    def antifrida_bypass(self, cmd, data):
        pass    

    # Listen for clipboard data
    def clipboard_manager(self, cmd, data):
        pass

    # Install burp CA as root
    def install_burp_root_ca(self, cmd, data):
        pass

    # Extract backup
    def extract_backup(self, cmd, data):
        pass

    # Pull apk from device
    def pull_apk(self, app_name):
        cmd_to_run = [Constants.ADB.value, 'shell', 'pm', 'list', 'packages', '-f']
        output = subprocess.run(cmd_to_run, stderr=DEVNULL, stdout=PIPE).stdout.decode().splitlines()
        for line in output:
            if app_name in line:
                pattern = re.compile(r"package:(.*?\.apk)=")
                file_path = pattern.findall(line)[0]
                file_name = os.path.splitext(os.path.basename(file_path))
                self._apktool.config["apk"] = file_name[0]
                self._apktool.reconfigure()
                pull_cmd = [Constants.ADB.value, 'pull', file_path, os.path.join(self._apktool.config["path"], ''.join(file_name))]
                subprocess.run(pull_cmd, stdout=DEVNULL, stderr=DEVNULL)
                print(Fore.GREEN + '[*] Pulling apk...' + Fore.RESET)
                break
                

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
            options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
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
            options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
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
            options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
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
            options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
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
        data_scan = {"app_name": "", "full_path": "~/.mmsf/loot/drozer_scans/"}
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
                options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            # The commands to be executed
            def execute(cmd, data):
                mmsf.run_all(cmd, data)
                
            readline.set_completer(cmd_completer)

            # get user input
            input_val = shlex.split(input('mmsf (scan)> '))
            if len(input_val) >= 1:
                command = input_val[0].lower()
            else:
                unknown_cmd()
            if command == "back":
                back()
                break
            elif command == "set":
                # wait for data to be set
                while True:
                    readline.set_completer(data_completer)
                    inpt = shlex.split(input('mmsf (scan/set)> '))
                    if len(inpt) > 1:
                        cmd, *args = inpt
                    else:
                        cmd = inpt[0]
                        args = None
                    if args:
                        if cmd.lower() == "outdir":
                            data_scan["full_path"] = args[0]
                        elif cmd.lower() == "app_name":
                            data_scan["app_name"] = args[0]
                    else:
                        if execute(cmd.lower(), data_scan):
                            break
            else:
                if execute(command, data_scan) == 2:
                    break 
    elif cmd == "find":
        while True:
            set_data = ["filter"]
            data = {
                "apps": apps,
                "query": ""
            }
            def data_completer(text, state):
                options = [i for i in set_data if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def cmd_completer(text, state):
                options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def execute(cmd, data):
                return mmsf.find_app(cmd, data)

            readline.set_completer(cmd_completer)

            value = shlex.split(input('mmsf (find)> '))
            if len(value) >= 1:
                command = value[0].lower()
            else:
                unknown_cmd()

            if command == "back":
                back()
                break
            elif command == "set":
                while True:
                    readline.set_completer(data_completer)
                    cmds = shlex.split(input('mmsf (find/set)> '))
                    if len(cmds) >= 2:
                        cmd, *args = cmds
                    else:
                        cmd = cmds[0]
                        args = None
                    if cmd.lower() == "filter" and args:
                        data["query"] = args[0].lower()
                    else:
                        if execute(cmd.lower(), data):
                            break
            else:
                if execute(command, data) == 2:
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
                elif action == "read":
                    handle_read(mmsf)
                else:
                    handle_update(mmsf)
            elif input_val[0].lower() == "back":
                back()
                break
    elif cmd == "deeplink":
        deeplink = ""
        while True:
            set_data = ["data_uri"]
            def data_completer(text, state):
                options = [i for i in set_data if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def cmd_completer(text, state):
                options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def execute(cmd, data):
                return mmsf.open_deeplink(cmd, data)

            readline.set_completer(cmd_completer)

            values = shlex.split(input('mmsf (deeplink)> '))
            if len(values) >= 1:
                value = values[0].lower()
            else:
                continue
            if value == "set":
                while True:
                    readline.set_completer(data_completer)
                    cmds = shlex.split(input('mmsf (deeplink/set)> '))
                    if len(cmds) == 2:
                        cmd, *args = cmds
                    else:
                        cmd = cmds[0]
                        args = None
                    if cmd.lower() == "data_uri" and args:
                        deeplink = args[0].lower()
                    else:
                        if execute(cmd.lower(), deeplink):
                            break
            else:
                if execute(value, deeplink) == 2:
                    break
    elif cmd == "intent":
        while True:
            set_data = ["data_uri", "extra", "component", "action", "mimetype", "app_name"] + apps
            actions = ["android.intent.action.VIEW", "android.intent.action.MAIN", "android.intent.action.SEND", "android.intent.action.SENDTO", "android.intent.action.SEARCH"]
            extras_type = ["parcelable", "long", "byte", "double", "charsequence", "boolean", "int", "Bundle", "string", "char", "serializable", "short"]
            activity_data = {
                "component": "",
                "extras": [],
                "deeplink": "",
                "intent_action": "",
                "mimetype": "",
                "app_name": ""
            }
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
                options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def execute(cmd, data):
                return mmsf.start_activity(cmd, data)

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
                                    if execute(cmdds[0].lower(), activity_data):
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
                        activity_data["extras"] = extra
                    elif cmd.lower() == "action" and args:
                        activity_data["intent_action"] = args[0]
                    elif cmd.lower() == "component" and args:
                        activity_data["component"] = args[0]
                    elif cmd.lower() == "app_name" and args:
                        activity_data["app_name"] = args[0]
                    elif cmd.lower() == "mimetype" and args:
                        activity_data["mimetype"] = args[0]
                    elif cmd.lower() == "data_uri" and args:
                        activity_data["deeplink"] = args[0]
                    else:
                        if execute(cmd.lower(), activity_data):
                            break
            else:
                if execute(value, activity_data) == 2:
                    break                  
    elif cmd == "broadcast":
        while True:
            set_data = ["data_uri", "extra", "component", "action", "mimetype", "app_name"] + apps
            actions = ["android.intent.action.VIEW", "android.intent.action.MAIN", "android.intent.action.SEND", "android.intent.action.SENDTO", "android.intent.action.SEARCH"]
            extras_type = ["parcelable", "long", "byte", "double", "charsequence", "boolean", "int", "Bundle", "string", "char", "serializable", "short"]
            activity_data = {
                "component": "",
                "extras": [],
                "deeplink": "",
                "intent_action": "",
                "mimetype": "",
                "app_name": ""
            }
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
                options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def execute(cmd, data):
                return mmsf.send_broadcast(cmd, data)

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
                                    if execute(cmdds[0].lower(), activity_data):
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
                        activity_data["extras"] = extra
                    elif cmd.lower() == "action" and args:
                        activity_data["intent_action"] = args[0]
                    elif cmd.lower() == "component" and args:
                        if len(args) != 2:
                            print(Fore.RED + '[-] Usage: component com.example.com com.exaple.com.BroadCastActivity' + Fore.RESET)
                            continue
                        else:
                            activity_data["component"] = args[1]
                            activity_data["app_name"] = args[0]
                    elif cmd.lower() == "mimetype" and args:
                        activity_data["mimetype"] = args[0]
                    elif cmd.lower() == "data_uri" and args:
                        activity_data["deeplink"] = args[0]
                    else:
                        if execute(cmd.lower(), activity_data):
                            break
            else:
                if execute(value, activity_data) == 2:
                    break                 
    elif cmd == "sniff":
        while True:
            set_data = ["data_authority", "data_path", "data_scheme", "data_type", "action", "category"]
            sniffdata = {
                "authority": "",
                "scheme": "",
                "path": "",
                "type": "",
                "intent_action": "",
                "category": ""

            }
            def data_completer(text, state):
                options = [i for i in set_data if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def cmd_completer(text, state):
                options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def execute(cmd, data):
                return mmsf.sniff_broadcast_data(cmd, data)

            readline.set_completer(cmd_completer)
            data = shlex.split(input('mmsf (sniff)> '))
            if len(data) > 0:
                value = data[0].lower()
            else:
                continue
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
                        sniffdata["intent_action"] = args[0]
                    elif cmd.lower() == "category" and args:
                        sniffdata["category"] = args[0]
                    elif cmd.lower() == "data_authority" and args:
                        sniffdata["authority"] = f'{args[0]} {args[1]}'
                    elif cmd.lower() == "data_path" and args:
                        sniffdata["path"] = args[0]
                    elif cmd.lower() == "data_scheme" and args:
                        sniffdata["scheme"] = args[0]
                    elif cmd.lower() == "data_type" and args:
                        sniffdata["type"] = args[0]
                    else:
                        if execute(cmd.lower(), sniffdata):
                            break
            else:
                if execute(value, sniffdata) == 2:
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
                    options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def execute(cmd, data):
                    return mmsf.bypass_ssl_frida(cmd,data)

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
                            if execute(cmd.lower(), frida_data):
                                break
                else:
                    if execute(value, frida_data) == 2:
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
                    options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
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

        def handle_network_config():
            network_data = {
                "app": "",
                "path": Constants.DIR_PULLED_APKS.value
            }
            while True:
                set_data = ["app", "path"]
                def data_completer(text, state):
                    options = [i for i in set_data if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def cmd_completer(text, state):
                    options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def execute(cmd, data):
                    return mmsf.bypass_network_config(cmd, data)

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (sslpinning/network_config)> '))[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (sslpinning/network_config/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "app" and args:
                            network_data["app"] = args[0]
                        elif cmd.lower() == "path" and args:
                            network_data["path"] = args[0]
                        else:
                            if execute(cmd.lower(), network_data):
                                break
                else:
                    if execute(value, network_data) == 2:
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
                    options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
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

        modules = ["objection", "frida", "flutter", "burp_ca", "network_config"]
        descriptions = [
            "Bypass the SSL Pinning using Objection", 
            "Frida Script to bypass the SSL Pinning",
            "Patch Flutter Applications",
            "Push the Burp CA to the Trusted ROOT CAs",
            "Modify the network_security_config.xml file"]

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
                elif action == "network_config":
                    handle_network_config()
            elif input_val[0].lower() == "back":
                back()
                break
    elif cmd == "rootdetection":
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
                    options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def execute(cmd, data):
                    return mmsf.bypass_root_frida(cmd,data)

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (rootdetection/frida)> '))[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (rootdetection/frida/set)> '))
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
                            if execute(cmd.lower(), frida_data):
                                break
                else:
                    if execute(value, frida_data) == 2:
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
                    options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                def execute(cmd, data):
                    return mmsf.bypass_root_objection_android(cmd,data)

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (rootdetection/objection)> '))[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (rootdetection/objection/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "app" and args:
                            objection_data["app"] = args[0]
                        else:
                            if execute(cmd.lower(), objection_data):
                                break
                else:
                    if execute(value, objection_data) == 2:
                        return 1

        modules = ["objection", "frida"]
        descriptions = [
            "Bypass the Android root detection mechanism using Objection (not working with System.exit)", 
            "Frida Script to bypass the Root Detection"
            ]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (rootdetection)> '))
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
            elif input_val[0].lower() == "back":
                back()
                break

def main():

    mmsf = MassiveMobileSecurityFramework()
    apps = mmsf.all_apps
    initial_commands = ["usemodule", "exit", "listmodules"]
    readline.parse_and_bind("tab: complete")
    modules = ["scan", "broadcast", "intent", "provider", "find", "deeplink", "sniff", "sslpinning", "rootdetection", "retrieveapk", "generateapk"]
    descriptions = [
        "Scan the application to retrieve crucial information such as exported activities, path traversal, SQL injections, attack vector and so on.", 
        "Send a broadcast intent.",
        "Start an intent using supplied values like: extra values, action, mimetype or data.",
        "Exploit the exported content provider to extract data.",
        "Find the package name of an application and/or its details by supplying a filter keyword.", 
        "Launch a deeplink with supplied value",
        "Sniffing a broadcast intent",
        "Bypass the SSL Pinning mechanism through different methods",
        "Bypass root detection mechanisms through different methods (works both on iOS and Android)",
        "Pull apk from device", 
        "Generate and sign apks"]

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
            if len(input_val) == 2:
                action = input_val[1].lower()
                if action not in modules:
                    unknown_cmd()
                else:
                    execute_cmd(mmsf, apps, action)
            else:
                print(Fore.RED + '[-] Usage: usemodule modulename' + Fore.RESET)

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Type \'exit\' to exit')
    
if __name__ == "__main__":
    signal(SIGINT, handler)
    main()