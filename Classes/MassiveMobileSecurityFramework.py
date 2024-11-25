import multiprocessing
import os
from pathlib import Path
import re
from asyncio.subprocess import DEVNULL
import shutil
import subprocess
from subprocess import PIPE
import threading
import warnings
from colorama import Fore
import readline
import shlex

from Classes.mmsf_drozer import drozer
from Classes.commands import Commands
from Classes.constants import Constants
from Classes.mmsf_apktool import apktool
from Classes.mmsf_frida import Frida
from Classes.mmsf_objection import objection
from Classes.mmsf_flutter import reflutter
from Classes.mmsf_nuclei import nuclei
from Classes.mmsf_other_tools import OtherTools
from Classes.utils import *
from modules import *

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
    _other_tools: OtherTools
    _device_type: str
    _nuclei:  nuclei

    @property
    def all_apps(self):
        return self._all_apps

    def __init__(self) -> None:
        self.__init_print()
        self.__check_prerequisites()
        self.__init_dirs()
        self.__init_frameworks()

    def __check_prerequisites(self):
        packages = ['apktool', Constants.UBERSIGNER.value, 'java', Constants.DROZER.value, 'reflutter', 'objection', 'frida', f'java -jar {os.path.join(Constants.DIR_UTILS_PATH.value, "abe.jar")}']
        not_installed = []
        for package in packages:
            try:
                print(Fore.YELLOW + f'[*] Initiating {package}' + Fore.RESET)
                subprocess.run(package.split(), stderr=DEVNULL, stdout=DEVNULL)
            except Exception:
                not_installed.append(package)
        for package in not_installed:
            print(Fore.RED + "[-] " + package + ' is not installed!' + Fore.RESET)
        if len(not_installed):
            print(Fore.RED + "Please use mmsfupdate first!" + Fore.RESET)
            quit_app()
        
    def is_ios(self):
        cmd = "frida-ps -U"
        p = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode()
        if "springboard" in p.lower():
            print(Fore.BLUE + '[*] Detected iOS device' + Fore.RESET)
            self._device_type = 'iOS'
            return True
        self._device_type = 'android'
        return False
        
    def __init_frameworks(self):
        low_power_mode = False
        if not check_alive_devices():
            print(Fore.RED + "[-] No devices found!" + Fore.RESET)
            resp = str(input(Fore.YELLOW + "Do you want to continue without any device? You'll be limited in terms of capabilities! Y/N (default: N) " + Fore.RESET) or "N")
            if resp.lower() == 'n':
                print(Fore.RED + '[-] Exitting' + Fore.RESET)
                exit(1)
            else:
                low_power_mode = True
        if low_power_mode:
            print(Fore.YELLOW + "[*] Running in low power mode ..." + Fore.RESET)
        else:
            self._frida = Frida(low_power_mode)
            self._objection = objection(low_power_mode)
            if self.is_ios():
                return
            self._other_tools = OtherTools(low_power_mode)
            self._drozer = drozer(low_power_mode)
            self._apktool = apktool(low_power_mode)
            self._reflutter = reflutter(low_power_mode)        
            self._nuclei = nuclei(low_power_mode)
            print(Fore.BLUE + '[*] Detected Android device' + Fore.RESET)
            self._all_apps = self.get_all_apps()

        
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
                print(Fore.YELLOW + "[*] Creating directories ... " + Fore.RESET)
                os.system(f"mkdir {path}")
            except OSError as e:
                print(Fore.LIGHTBLUE_EX + '[DEBUG] ' + e + Fore.RESET)

    def __init_dirs(self):
        for path in (Constants):
            if path.name.startswith('DIR_'):
                self.__mkdir(path.value)

    # methods
    # Get a list of all installed apps
    def get_all_apps(self) -> list:
        if self._device_type == 'iOS':
            return list()
        final_command = " ".join(self._drozer._drozer_cmd).split() + ['-c', Commands.FIND_APP.value["cmd"], '--debug']
        return list(map(lambda x: x.split(" ")[0], subprocess.run(final_command, stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()[2:])) 

    # run all drozer scans
    def run_all(self, cmd, data):
        if data["full_path"]:
            self._drozer.config["full_path"] = data["full_path"]
        self._drozer.config["app_name"] = data["app_name"]
        self._drozer._regenerate()

        if cmd == "run":
            if self._drozer.config["app_name"]:
                self._drozer.run_all()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0
        elif cmd == "show":
            print_show_table([
                {"name": "OUTDIR", "value": self._drozer.config["full_path"], "description": "The directory where the scans will save the data. Default is ~/.mmsf/loot/drozer_scans/"},
                {"name": "APP_NAME", "value": self._drozer.config["app_name"], "description": "The name of the application to be scanned."}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    # Find specific app using drozer
    def find_app(self, cmd, data) -> list:
        apps = data["apps"]
        self._drozer.config["find_app_query"] = data["query"]
        if cmd == "run":
            if self._drozer.config["find_app_query"]:
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
            print_show_table([{"name": "FILTER", "value": self._drozer.config["find_app_query"], "description": "The query used to find the apps."}])
            return 0
        elif cmd == "exit":
            quit_app()
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
            quit_app()
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
            quit_app()
        elif cmd == "back":
            back()
            return 2   
       
    # Open DeepLinks
    def open_deeplink(self, cmd, data):
        self._other_tools._deeplink = data
        if cmd == "run":
            if self._other_tools._deeplink:
                self._other_tools.open_deeplink()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0                 
        elif cmd == "show":
            print_show_table([{"name": "DATA_URI", "value": self._other_tools._deeplink, "description": "The URI used to open the application as deeplink"}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2
        self._other_tools.open_deeplink()

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
            quit_app()
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
            quit_app()
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
            quit_app()
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
            quit_app()
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
            quit_app()
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
                if self._device_type == 'iOS':
                    self._frida.bypass_ssl_ios()
                else:
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
                {"name": "PAUSE", "value": "TRUE" if self._frida.config["pause"] == "--pause" else "FALSE" , "description": "The application should be paused on start? Default set to FALSE", "required": False},
                {"name": "METHOD", "value": "SPAWN" if self._frida.config["method"] == '-f' else "FRONTMOST", "description": "The method of attaching to the application: frontmost or spawn. Default SPAWN"}])
            return 0
        elif cmd == "exit":
            quit_app()
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
            quit_app()
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
                threading.Thread(target=self._frida.bypass_root, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "MODE", "value": "SERIAL" if self._frida.config["mode"] == "-U" else "REMOTE", "description": "The Type of Connection with frida-server: Serial or Remote. Default set to Serial", "required": False},
                {"name": "APP", "value": self._frida.config["app"], "description": "The application package name: com.example.android"},
                {"name": "HOST", "value": self._frida.config["host"], "description": "If MODE set to Remote, specify HOST. Default set to 127.0.0.1", "required": False},
                {"name": "PAUSE", "value": "TRUE" if self._frida.config["pause"] == "--pause" else "FALSE" , "description": "The application should be paused on start? Default set to FALSE", "required": False},
                {"name": "METHOD", "value": "SPAWN" if self._frida.config["method"] == '-f' else "FRONTMOST", "description": "The method of attaching to the application: frontmost or spawn. Default SPAWN"}])
            return 0
        elif cmd == "exit":
            quit_app()
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
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def generate_apk(self, cmd, data):
        self._apktool.config = data
        if cmd == "run": 
            if self._apktool.config["apk"]:
                self._apktool.generate_apk()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "DIR_NAME", "value": self._apktool.config["dir_name"], "description": "The directory that needs to be patched. Default: base", 'required': False},
                {"name": "PATH", "value": self._apktool.config["path"], "description": "The path where to save the apk. Default to: ~/.mmsf/loot/apks", "required": False},
                {"name": "APK", "value": self._apktool.config["apk"], "description": "The target output name. Default to: base", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def sign_apk(self, cmd, data):
        self._apktool.config = data
        if cmd == "run": 
            if self._apktool.config["in_apk"]:
                self._apktool.sign_apk()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "IN_APK", "value": self._apktool.config["in_apk"], "description": "The APK that needs to be signed. Default: base_usigned.apk", 'required': False},
                {"name": "PATH", "value": self._apktool.config["path"], "description": "The path where to save the apk. Default to: ~/.mmsf/loot/apks", "required": False},
                {"name": "OUT_APK", "value": self._apktool.config["out_apk"], "description": "The target output name. Default to: base_patched.apk", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def install_apk(self, cmd, data):
        self._apktool.config = data
        if cmd == "run": 
            if self._apktool.config["apk"]:
                print(Fore.GREEN + "[+] Installing apk.." + Fore.RESET)
                self._apktool.install_apk()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APK", "value": self._apktool.config["apk"], "description": "The APK that is going to be installed. Default: base_patched.apk", 'required': True},
                {"name": "PATH", "value": self._apktool.config["path"], "description": "The path where the apk is located. Default to: ~/.mmsf/loot/apks", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    # Patch apk and sign
    def patch_apk(self, cmd, data):
        self._objection.config = data
        if self._objection.config["abi"] == "autodetect":
            self._objection.config["abi"] = self.get_architecture()
        if cmd == "run": 
            if self._objection.config["apk"]:
                self._objection.patch_apk()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APK", "value": self._objection.config["apk"], "description": "The APK that is going to be patched. Default: ~/.mmsf/loot/apks/base.apk", 'required': True},
                {"name": "ABI", "value": self._objection.config["abi"], "description": "The architecture of the target device. Default to: autodetect", "required": False},
                {"name": "NETWORK", "value": self._objection.config["network"], "description": "Include a network_security_config.xml file allowing for user added CA's to be trusted on Android 7+. Default to False", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    # Get the Device's arch
    def get_architecture(self):
        cmd = f"{Constants.ADB.value} shell getprop ro.product.cpu.abi"
        return subprocess.run(cmd.split(), stdout=PIPE, stderr=PIPE).stdout.decode().strip()

    # Pull apk from device
    def pull_apk(self):
        cmd_to_run = [Constants.ADB.value, 'shell', 'pm', 'path', self._apktool.config["app"]]
        output = subprocess.run(cmd_to_run, stderr=DEVNULL, stdout=PIPE).stdout.decode().splitlines()
        pattern = re.compile(r"package:(.*?\.apk)")
        if len(output) > 1:
            print(Fore.YELLOW + '[*] It seems like the app is a Split One. Continue downloading the base.apk. For complete APK use splitapk module'  + Fore.RESET)
        for line in output:
            file_path = pattern.findall(line)[0]
            file_name = os.path.splitext(os.path.basename(file_path))
            if self._apktool.config["apk"] == "base":
                self._apktool.config["apk"] = file_name[0]
            self._apktool.reconfigure()
            pull_cmd = [Constants.ADB.value, 'pull', file_path, os.path.join(self._apktool.config["path"], self._apktool.config["apk"])]
            p = subprocess.run(pull_cmd, stdout=PIPE, stderr=PIPE)
            print(Fore.GREEN + '[+] Pulling apk...' + Fore.RESET)
            print(Fore.GREEN + '[+] ' +  p.stdout.decode().strip() + Fore.RESET)
            print(Fore.GREEN + f'[+] Data pulled successfully to {self._apktool.config["path"]}' + Fore.RESET)
            return
        print(Fore.RED + '[-] The application does not exist. Try again' + Fore.RESET)
                
    def getapk(self, cmd, data):
        self._apktool.config = data
        if cmd == "run": 
            if self._apktool.config["app"]:
                threading.Thread(target=self.pull_apk, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APP", "value": self._apktool.config["app"], "description": "The application name: MyApplication"},
                {"name": "PATH", "value": self._apktool.config["path"], "description": "The path where to save the apk. Default to: ~/.mmsf/loot/apks", "required": False},
                {"name": "APK", "value": self._apktool.config["apk"], "description": "The target output name. Default to: base", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def extract_backup(self, cmd, data):
        self._other_tools.config = data
        if cmd == "run": 
            if self._other_tools.config["app"]:
                threading.Thread(target=self._other_tools.extract_backup, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APP", "value": self._other_tools.config["app"], "description": "The application package name: com.example.android"},
                {"name": "PATH", "value": self._other_tools.config["path"], "description": "The path where to save the backup. Default to: ~/.mmsf/loot/data/", "required": False},
                {"name": "PASSWORD", "value": self._other_tools.config["password"], "description": "The password used for backup encryption. Default to: None", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def restore_backup(self, cmd, data):
        self._other_tools.config = data
        if cmd == "run": 
            if self._other_tools.config["app"]:
                threading.Thread(target=self._other_tools.restore_backup, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APP", "value": self._other_tools.config["app"], "description": "The application package name: com.example.android"},
                {"name": "PATH", "value": self._other_tools.config["path"], "description": "The path where the backup is located. Default to: ~/.mmsf/loot/data/", "required": False},
                {"name": "PASSWORD", "value": self._other_tools.config["password"], "description": "The password used for backup encryption. Default to: None", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def generate_jsinterface(self, cmd, data):
        self._other_tools._generate_deeplink_data = data
        if cmd == "run": 
            if self._other_tools._generate_deeplink_data["server"] and self._other_tools._generate_deeplink_data["scheme"] and self._other_tools._generate_deeplink_data["package"] and self._other_tools._generate_deeplink_data["component"] and self._other_tools._generate_deeplink_data["deeplink_uri"] and self._other_tools._generate_deeplink_data["param"] and self._other_tools._generate_deeplink_data["js_interface"]:
                threading.Thread(target=self._other_tools.generate_jsinterface, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "SERVER", "value": self._other_tools._generate_deeplink_data["server"], "description": "The server you are using to host the files. Default to: http://127.0.0.1:8000"},
                {"name": "FILENAME", "value": self._other_tools._generate_deeplink_data["filename"], "description": "The file name. Default to: steal.html", "required": False},
                {"name": "SCHEME", "value": self._other_tools._generate_deeplink_data["scheme"], "description": "The deeplink's scheme."},
                {"name": "PACKAGE", "value": self._other_tools._generate_deeplink_data["package"], "description": "The application package name: com.example.android"},
                {"name": "COMPONENT", "value": self._other_tools._generate_deeplink_data["component"], "description": "The vulnerable activity. e.g. com.example.android/.WebViewActivity"},
                {"name": "DEEPLINK_URI", "value": self._other_tools._generate_deeplink_data["deeplink_uri"], "description": "The deeplink URI."},
                {"name": "PARAM", "value": self._other_tools._generate_deeplink_data["param"], "description": "The deeplink's vulnerable parameter."},
                {"name": "JS_INTERFACE", "value": self._other_tools._generate_deeplink_data["js_interface"], "description": "The vulnerable JavaScript Interface in form of AndroidInterfaceName.getUserSession()"},
                {"name": "PATH", "value": self._other_tools._generate_deeplink_data["path"], "description": "The path where to store the files. Default to: ~/.mmsf/loot/", "required": False},
                {"name": "POC_FILENAME", "value": self._other_tools._generate_deeplink_data["poc_filename"], "description": "The POC filename. Default to: launch.html", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def generate_deeplink(self, cmd, data):
        self._other_tools._generate_deeplink_data_d = data
        if cmd == "run": 
            if self._other_tools._generate_deeplink_data_d["scheme"] and self._other_tools._generate_deeplink_data_d["package"] and self._other_tools._generate_deeplink_data_d["component"] and self._other_tools._generate_deeplink_data_d["deeplink_uri"]:
                threading.Thread(target=self._other_tools.generate_deeplink, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "SCHEME", "value": self._other_tools._generate_deeplink_data_d["scheme"], "description": "The deeplink's scheme."},
                {"name": "PACKAGE", "value": self._other_tools._generate_deeplink_data_d["package"], "description": "The application package name: com.example.android"},
                {"name": "COMPONENT", "value": self._other_tools._generate_deeplink_data_d["component"], "description": "The vulnerable activity. e.g. com.example.android/.WebViewActivity"},
                {"name": "DEEPLINK_URI", "value": self._other_tools._generate_deeplink_data_d["deeplink_uri"], "description": "The deeplink URI."},
                {"name": "PATH", "value": self._other_tools._generate_deeplink_data_d["path"], "description": "The path where to store the files. Default to: ~/.mmsf/loot/", "required": False},
                {"name": "EXTRAS", "value": self._other_tools._generate_deeplink_data_d["extras"], "description": "The extra values in form of TYPE KEY VALUE. e.g. S com.example.REDIRECT_URL https://interactsh.io. To remove an extra value, just type remove KEY", "required": False}
            ])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

        # Analyze Keystore
    def keystore_analyze(self, cmd, data):
        pass

    # Bypass Fingerprint detection using frida android
    def bypass_android_biometrics_frida(self, cmd, data):
        self._frida.config = data
        if cmd == "run":
            if self._frida.config["mode"] == '-R':
                if not self._frida.config["host"]:
                    print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                    return 0    
            if self._frida.config["app"]:
                threading.Thread(target=self._frida.bypass_android_biometrics, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "MODE", "value": "SERIAL" if self._frida.config["mode"] == "-U" else "REMOTE", "description": "The Type of Connection with frida-server: Serial or Remote. Default set to Serial", "required": False},
                {"name": "APP", "value": self._frida.config["app"], "description": "The application package name: com.example.android"},
                {"name": "HOST", "value": self._frida.config["host"], "description": "If MODE set to Remote, specify HOST. Default set to 127.0.0.1", "required": False},
                {"name": "PAUSE", "value": "TRUE" if self._frida.config["pause"] == "--pause" else "FALSE" , "description": "The application should be paused on start? Default set to FALSE", "required": False},
                {"name": "METHOD", "value": "SPAWN" if self._frida.config["method"] == '-f' else "FRONTMOST", "description": "The method of attaching to the application: frontmost or spawn. Default SPAWN"}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2
    
    # Bypass Fingerprint detection using frida ios
    def bypass_ios_biometrics_frida(self, cmd, data):
        self._frida.config = data
        if cmd == "run":
            if self._frida.config["mode"] == '-R':
                if not self._frida.config["host"]:
                    print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                    return 0    
            if self._frida.config["app"]:
                threading.Thread(target=self._frida.bypass_ios_biometrics, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "MODE", "value": "SERIAL" if self._frida.config["mode"] == "-U" else "REMOTE", "description": "The Type of Connection with frida-server: Serial or Remote. Default set to Serial", "required": False},
                {"name": "APP", "value": self._frida.config["app"], "description": "The application package name: com.example.android"},
                {"name": "HOST", "value": self._frida.config["host"], "description": "If MODE set to Remote, specify HOST. Default set to 127.0.0.1", "required": False},
                {"name": "PAUSE", "value": "TRUE" if self._frida.config["pause"] == "--pause" else "FALSE" , "description": "The application should be paused on start? Default set to FALSE", "required": False},
                {"name": "METHOD", "value": "SPAWN" if self._frida.config["method"] == '-f' else "FRONTMOST", "description": "The method of attaching to the application: frontmost or spawn. Default SPAWN"}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2
    
    
    # Bypass Fingerprint detection using objection ios
    def bypass_ios_biometrics_objection(self, cmd, data):
        self._objection._config["app"] = data["app"]
        if cmd == "run": 
            if self._objection._config["app"]:
                threading.Thread(target=self._objection.bypass_ios_biometrics, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APP", "value": self._objection._config["app"], "description": "The application package name: com.example.android"}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

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
    
    def bypass_jailbreak_objection_ios(self, cmd, data):
        self._objection._config["app"] = data["app"]
        if cmd == "run": 
            if self._objection._config["app"]:
                threading.Thread(target=self._objection.bypass_ios_jailbreak, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APP", "value": self._objection._config["app"], "description": "The application package name: com.example.ios"}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2
        
    def bypass_ios_jailbreak_frida(self, cmd, data):
        self._frida.config = data
        if cmd == "run":
            if self._frida.config["mode"] == '-R':
                if not self._frida.config["host"]:
                    print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                    return 0    
            if self._frida.config["app"]:
                threading.Thread(target=self._frida.bypass_ios_jailbreak, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "MODE", "value": "SERIAL" if self._frida.config["mode"] == "-U" else "REMOTE", "description": "The Type of Connection with frida-server: Serial or Remote. Default set to Serial", "required": False},
                {"name": "APP", "value": self._frida.config["app"], "description": "The application package name: com.example.android"},
                {"name": "HOST", "value": self._frida.config["host"], "description": "If MODE set to Remote, specify HOST. Default set to 127.0.0.1", "required": False},
                {"name": "PAUSE", "value": "TRUE" if self._frida.config["pause"] == "--pause" else "FALSE" , "description": "The application should be paused on start? Default set to FALSE", "required": False},
                {"name": "METHOD", "value": "SPAWN" if self._frida.config["method"] == '-f' else "FRONTMOST", "description": "The method of attaching to the application: frontmost or spawn. Default SPAWN"}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2
    
    def run_nuclei_scan(self, cmd, data):
        self._nuclei.config = data
        paths = ['Keys', 'Android']
        decompiled = False
        if cmd == "run":   
            if self._nuclei.config["dir_name"]:
                outdir = Constants.DIR_NUCLEI_SCANS.value if not self._nuclei.config.get("out_dir") else os.path.join(self._nuclei.config.get("out_dir"), 'nuclei_scans')

                if not os.path.isdir(outdir):
                    os.mkdir(outdir)
                for path in paths:
                    print(Fore.YELLOW + f"[*] Executing nuclei in background for {path} templates." + Fore.RESET)
                    threading.Thread(target=self._nuclei._start_scan, args=([path])).start()
                return 1
            elif self._nuclei.config["app_name"] and self._nuclei.config["app_name"] in self.all_apps:
                def previous_decompilation():
                    return os.path.isdir(os.path.join(Constants.DIR_PULLED_APKS.value,self._nuclei.config["app_name"]))

                previous_decom = previous_decompilation()
                decompiled = previous_decom
                for path in paths:
                    data_scan = {
                        "dir_name": self._nuclei.config["app_name"],
                        "app": self._nuclei.config["app_name"],
                        "path": Constants.DIR_PULLED_APKS.value,
                        "mode": "d",
                        "apk": self._nuclei.config["app_name"],
                        "out_apk": Constants.PATCHED_APK.value,
                        "in_apk": Constants.GENERATED_APK.value,
                    }
                    if not decompiled or not previous_decom:
                        self.getapk("run", data_scan)
                        print(Fore.GREEN + '[*] Decompiling apk..' + Fore.RESET)
                        self._apktool._decompile_apk(os.path.join(data_scan["path"],data_scan["apk"]))
                        decompiled = True
                        previous_decom = True
                    print(Fore.YELLOW + f"[*] Executing nuclei in background for {path} templates." + Fore.RESET)
                    threading.Thread(target=self._nuclei._start_scan, args=([path])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APP_NAME", "value": self._nuclei.config["app_name"], "description": "The application name in form of com.example.android. Omit it if you set the DIR_NAME", "required": False},
                {"name": "OUT_DIR", "value": self._nuclei.config["out_dir"], "description": "The directory where scans are saved. Default to ~/.mmsf/loot/data/nuclei_scans", "required": False},
                {"name": "DIR_NAME", "value": self._nuclei.config["dir_name"], "description": "The directory to be scanned. Omit it if you set the APP_NAME", "required": False},
                {"name": "OUT_FILE", "value": self._nuclei.config["out_file"], "description": "The output of the nuclei. Default to app_name_nuclei_output", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2
        
    def nsuserdefaults_modify(self, cmd, data):
        self._frida.config = data
        if cmd == "run":
            if self._frida.config["mode"] == '-R':
                if not self._frida.config["host"]:
                    print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                    return 0    
            if self._frida.config["app"]:
                threading.Thread(target=self._frida.nsuserdefaults_modify, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "MODE", "value": "SERIAL" if self._frida.config["mode"] == "-U" else "REMOTE", "description": "The Type of Connection with frida-server: Serial or Remote. Default set to Serial", "required": False},
                {"name": "APP", "value": self._frida.config["app"], "description": "The application package name: com.example.android"},
                {"name": "HOST", "value": self._frida.config["host"], "description": "If MODE set to Remote, specify HOST. Default set to 127.0.0.1", "required": False},
                {"name": "PAUSE", "value": "TRUE" if self._frida.config["pause"] == "--pause" else "FALSE" , "description": "The application should be paused on start? Default set to FALSE", "required": False},
                {"name": "METHOD", "value": "SPAWN" if self._frida.config["method"] == '-f' else "FRONTMOST", "description": "The method of attaching to the application: frontmost or spawn. Default SPAWN"},
                {"name": "KEY", "value": self._frida.config["key"], "description": "The NSUserDefaults Key to be modified"},
                {"name": "VALUE", "value": self._frida.config["value"], "description": "The newly value to be added to NSUserDefaults key"}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2
        
    def nsuserdefaults_retrieve(self, cmd, data):
        self._frida.config = data
        if cmd == "run":
            if self._frida.config["mode"] == '-R':
                if not self._frida.config["host"]:
                    print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                    return 0    
            if self._frida.config["app"]:
                threading.Thread(target=self._frida.nsuserdefaults_retrieve, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "MODE", "value": "SERIAL" if self._frida.config["mode"] == "-U" else "REMOTE", "description": "The Type of Connection with frida-server: Serial or Remote. Default set to Serial", "required": False},
                {"name": "APP", "value": self._frida.config["app"], "description": "The application package name: com.example.android"},
                {"name": "HOST", "value": self._frida.config["host"], "description": "If MODE set to Remote, specify HOST. Default set to 127.0.0.1", "required": False},
                {"name": "PAUSE", "value": "TRUE" if self._frida.config["pause"] == "--pause" else "FALSE" , "description": "The application should be paused on start? Default set to FALSE", "required": False},
                {"name": "METHOD", "value": "SPAWN" if self._frida.config["method"] == '-f' else "FRONTMOST", "description": "The method of attaching to the application: frontmost or spawn. Default SPAWN"}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def list_readable_files(self, directory_path):
        """Lists readable files within a specified directory.

        Args:
            directory_path (str): The path to the directory.

        Returns:
            list: A list of absolute paths of readable files.
        """

        command = f"adb shell ls -la {directory_path}"
        output = subprocess.check_output(command.split()).decode("utf-8").splitlines()

        readable_files = []
        for line in output:
            if line.strip():
                file_info = line.split()
                permissions = file_info[0]
                file_name = file_info[-1]
                if len(permissions) != 10:
                    continue
                if permissions[7] == 'r' and (file_name != '.' and file_name != '..'):  # Check if the file is readable
                    full_path = f"{directory_path}/{file_name}"
                    readable_files.append(full_path)

        return readable_files

    def pull_apks(self):
        cmd_to_run = [Constants.ADB.value, 'shell', 'pm', 'path', self._apktool._config_split["app"]]
        output = subprocess.run(cmd_to_run, stderr=DEVNULL, stdout=PIPE).stdout.decode().splitlines()
        pattern = re.compile(r"package:(.*?\.apk)")
        print(Fore.GREEN + '[+] Pulling apks...' + Fore.RESET)

        for line in output:
            file_path = Path(pattern.findall(line)[0]).parent
            pull_files = self.list_readable_files(file_path)
            dst = os.path.join(self._apktool._config_split["path"],self._apktool._config_split["app"])
            os.mkdir(dst)
            for file in pull_files:
                pull_cmd = [Constants.ADB.value, 'pull', file, dst]
                p = subprocess.run(pull_cmd, stdout=PIPE, stderr=PIPE)
                print(Fore.GREEN + '[+] ' +  p.stdout.decode().strip() + Fore.RESET)
            print(Fore.GREEN + f'[+] Data pulled successfully to {dst}' + Fore.RESET)
            return
        print(Fore.RED + '[-] The application does not exist. Try again' + Fore.RESET)

    def getapks(self, cmd, data):
        self._apktool._config_split = data
        if cmd == "run": 
            if self._apktool._config_split["app"]:
                threading.Thread(target=self.pull_apks, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APP", "value": self._apktool._config_split["app"], "description": "The application name: MyApplication"},
                {"name": "PATH", "value": self._apktool._config_split["path"], "description": "The path where to save the apks. Default to: ~/.mmsf/loot/apks", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def install_apks(self, cmd, data):
        self._apktool._config_split = data
        if cmd == "run": 
            if self._apktool._config_split["path"] or self._apktool._config_split["apks"]:
                print(Fore.GREEN + "[+] Installing apks.." + Fore.RESET)
                self._apktool.install_apks()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APKS", "value": self._apktool._config_split["apks"], "description": "The APKs that are going to be installed. Example: base.apk, split_config.en.apk", 'required': False},
                {"name": "PATH", "value": self._apktool._config_split["path"], "description": "The path where the APKs are located. Default to: ~/.mmsf/loot/apks", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2
        
    def generate_apks(self, cmd, data):
        self._apktool._config_split = data
        if cmd == "run": 
            if self._apktool._config_split["path"]:
                print(Fore.GREEN + "[+] Generating apks.." + Fore.RESET)
                self._apktool.generate_apks()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APKS", "value": self._apktool._config_split["apks"], "description": "The APKs that are going to be installed. Default: base_patched.apk", 'required': True},
                {"name": "PATH", "value": self._apktool._config_split["path"], "description": "The path where the apk is located. Default to: ~/.mmsf/loot/apks", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def sign_apks(self, cmd, data):
        self._apktool._config_split = data
        if cmd == "run": 
            if self._apktool._config_split["path"] or self._apktool._config_split["apks"]:
                print(Fore.GREEN + "[+] Signing apks.." + Fore.RESET)
                self._apktool.sign_apks()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APKS", "value": self._apktool._config_split["apks"], "description": "The APKs that are going to be signed. Example: base.apk, split_config.en.apk", 'required': False},
                {"name": "PATH", "value": self._apktool._config_split["path"], "description": "The path where the APKs are located. Default to: ~/.mmsf/loot/apks", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2
    
    def decompile_apks(self, cmd, data):
        self._apktool._config_split = data
        if cmd == "run": 
            if self._apktool._config_split["path"] or self._apktool._config_split["apks"]:
                print(Fore.GREEN + "[+] Decompiling apks.." + Fore.RESET)
                self._apktool.decompile_apks()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "APKS", "value": self._apktool._config_split["apks"], "description": "The APKs that are going to be decompiled. Example: base.apk, split_config.en.apk", 'required': False},
                {"name": "PATH", "value": self._apktool._config_split["path"], "description": "The path where the APKs are located. Default to: ~/.mmsf/loot/apks", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2