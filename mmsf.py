#!/usr/bin/python3

import os
import requests
from asyncio.subprocess import DEVNULL
from enum import Enum
import subprocess
from subprocess import PIPE
from tempfile import gettempdir
import warnings
from colorama import Fore
import readline
import shlex
from signal import signal, SIGINT
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")
# Set the unbuffered output
os.environ.setdefault('PYTHONUNBUFFERED', '1')

class Commands(Enum):

    COMMAND_PACKAGEINFO={"cmd": f"run app.package.info -a ", "display": Fore.GREEN + "[+] Running package info ...", "fname": "package_info.txt"}
    COMMAND_ATTACKSURFACE={"cmd": f"run app.package.attacksurface ", "display": Fore.GREEN + "[+] Running attack surface ..", "fname": "attack_surface.txt"}
    COMMAND_ACTIVITYINFO={"cmd": f"run app.activity.info -u -a ", "display": Fore.GREEN + "[+] Running activity info ...", "fname": "activity_info.txt"}
    COMMAND_PROVIDERINFO={"cmd": f"run app.provider.info -a ", "display": Fore.GREEN + "[+] Running provider information ...", "fname": "content_providers.txt"}
    COMMAND_FINDURIS={"cmd": f"run scanner.provider.finduris -a ", "display": Fore.GREEN + "[+] Finding providers uris ...", "fname": "finduris.txt"}
    COMMAND_SQLTABLES={"cmd": f"run scanner.provider.sqltables -a ", "display": Fore.GREEN + "[+] Scanning for SQL Tables ...", "fname": "sql_tables.txt"}
    COMMAND_SQLINJECTION={"cmd": f"run scanner.provider.injection -a ", "display": Fore.GREEN + "[+] Scanning for injection...", "fname": "injection.txt"}
    COMMAND_PATHTRAVERSAL={"cmd": f"run scanner.provider.traversal -a ", "display": Fore.GREEN + "[+] Scanning for path traversal ...", "fname": "traversal.txt"}
    COMMAND_BROADCASTRECEIVERS={"cmd": f"run app.broadcast.info -a ", "display": Fore.GREEN + "[+] Finding broadcast receivers ...", "fname": "broadcast_receivers.txt"}
    COMMAND_SERVICES={"cmd": f"run app.service.info -a ", "display": Fore.GREEN + "[+] Running app.service.info ...", "fname": "service_info.txt"}
    COMMAND_BROWSABLE={"cmd": f"run scanner.activity.browsable -a ", "display": Fore.GREEN + "[+] Running scanner.activity.browsable ...", "fname": "browsable.txt"}
    COMMAND_MANIFEST={"cmd": f"run app.package.manifest ", "display": Fore.GREEN + "[+] Gathering manifest data ...", "fname": "AndroidManifest.xml"}    

    START_ACTIVITY={"cmd": f"run app.activity.start --component ", "display": Fore.YELLOW + "[+] Starting the activity ..."}
    SEND_BROADCAST={"cmd": f"run app.broadcast.send --component", "display": Fore.YELLOW + "[+] Sending the broadcast message ..."}
    QUERY_CONTENT={"cmd": f"run app.provider.query ", "display": Fore.YELLOW + "[+] Querying the content provider ..."}
    FIND_APP={"cmd": f"run app.package.list", "display": Fore.YELLOW + "[+] Finding the application details ..."}
    LAUNCH_DEEPLINK={"cmd": "run app.activity.start --action android.intent.action.VIEW --data-uri ", "display": Fore.YELLOW + "[+] Launching deeplink attack ..."}
    SNIFF_DATA={"cmd": "run app.broadcast.sniff", "display": Fore.YELLOW + "[+] Sniffing for data ..."}

class Constants(Enum):
    DELIM = " " * 10  + "|  "

class MassiveMobileSecurityFramework:

    id: str
    _full_path: str
    _app_name: str
    _drozer_cmd: list
    _drozer_devices: list
    _adb: str
    _agent_apk_path: str
    _query: str
    _cmd: str
    _send_type: str
    _outdir: str
    _all_apps: list
    _deeplink: str
    _component: str
    _extras: str
    _intent_action: str
    _mimetype: str
    _uri: str
    _category: str
    _sniff_data: dict
    _content_provider: dict

    def __init__(self) -> None:
        self.__init_print()
        self._drozer_cmd = ['drozer', 'console', 'connect']
        self._drozer_devices = ['drozer', 'console', 'devices']
        self._adb = "/opt/genymobile/genymotion/tools/adb"
        self.command = ["back", "run", "set", "show", "exit"]
        self._agent_apk_path = gettempdir() + '/' + 'drozer-agent.apk'
        self._frida_path = gettempdir() + '/' + 'frida-server'
        self.__init_frida()
        self.__init_objection()
        self.__init_reflutter()
        self.__init_drozer()
        self._all_apps = self.getAllApps()
        self._app_name, self._query, self._cmd , self._send_type, self._full_path = "", "", "", "", ""
        self._outdir, self._deeplink, self._extras, self._intent_action, self._component = "", "", "", "", ""
        self._mimetype, self._projection, self._selection, self._uri, self._category = "", "", "", "", ""
        self._sniff_data = {
            "authority": "",
            "scheme": "",
            "path": "",
            "type": ""
        }
        self._content_provider = {
            "uri": "",
            "selection": "",            
            "projection": [],
            "selection_args": [],
            "insert_values": [],
            "update_values": []
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

    def __init_drozer(self):
        proc = subprocess.run(self._drozer_devices, stdout=PIPE, stderr=DEVNULL)
        stdout = proc.stdout.decode().splitlines()
        if not stdout:
            print(Fore.RED + "[-] Drozer is not running... Trying to wake the Agent... "+ Fore.RESET)
            proc2 = subprocess.run([self._adb, 'shell', 'am', 'startservice', '-n', 'com.mwr.dz/.services.ServerService', '-c', 'com.mwr.dz.START_EMBEDDED'], stderr=PIPE, stdout=DEVNULL)
            if proc2.stderr.decode().splitlines() and "Not found" in proc2.stderr.decode().splitlines()[0]:
                print(Fore.RED + "[-] Drozer Agent is not installed on the phone. Installing ..." + Fore.RESET)
                self.__download_agent()
                self.__install_agent()
            else:
                subprocess.run([self._adb, 'forward', 'tcp:31415', 'tcp:31415'], stderr=DEVNULL, stdout=DEVNULL)
        else:
            print(Fore.BLUE + "[*] Drozer Agent is waiting for your commands!" + Fore.RESET)

    def __init_frida(self):
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
        subprocess.run([self._adb, 'shell', 'chmod + x /tmp/frida-server'], stderr=DEVNULL, stdout=DEVNULL)
        subprocess.run([self._adb, 'shell', '/tmp/frida-server &'], stderr=DEVNULL, stdout=DEVNULL)
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

    def __download_agent(self): 
        url = "https://github.com/mwrlabs/drozer/releases/download/2.3.4/drozer-agent-2.3.4.apk"
        drozer_agent = requests.get(url)
        open(self._agent_apk_path, 'wb').write(drozer_agent.content)

    def __install_agent(self):
        print(Fore.BLUE + "[*] Installing apk... Please be patient"+ Fore.RESET)
        proc = subprocess.run([self._adb, 'install', self._agent_apk_path], stderr=PIPE, stdout=DEVNULL)
        if proc.stderr:
            print(proc.stderr)
            exit(-1)
        else:
            print(Fore.BLUE + "[*] Successfully installed Drozer Agent!" + Fore.RESET)
    
    # getters
    @property
    def cmd(self):
        return self._cmd

    @property
    def query(self):
        return self._query

    @property
    def app_name(self):
        return self._app_name

    @property
    def full_path(self):
        return self._full_path

    @property
    def send_type(self):
        return self._send_type

    @property
    def drozer_cmd(self):
        return self._drozer_cmd

    @property
    def all_apps(self):
        return self._all_apps

    @property
    def deeplink(self):
        return self._deeplink

    @property
    def component(self):
        return self._component

    @property
    def extras(self):
        return self._extras

    @property
    def intent_action(self):
        return self._intent_action

    @property
    def mimetype(self):
        return self._mimetype
    
    @property
    def uri(self):
        return self._uri

    @property
    def data(self):
        return self._sniff_data

    @property
    def category(self):
        return self._category

    @property
    def content_provider(self):
        return self._content_provider

    # setters
    @component.setter
    def component(self, component):
        self._component = component

    @extras.setter
    def extras(self, extras):
        self._extras = extras

    @intent_action.setter
    def intent_action(self, intent_action):
        self._intent_action = intent_action

    @mimetype.setter
    def mimetype(self, mimetype):
        self._mimetype = mimetype

    @deeplink.setter
    def deeplink(self, deeplink):
        self._deeplink = deeplink

    @send_type.setter
    def send_type(self, send_type):
        self._send_type = send_type

    @cmd.setter
    def cmd(self, cmd):
        self._cmd = cmd

    @query.setter
    def query(self, query):
        self._query = query
    
    @app_name.setter
    def app_name(self, app_name):
        self._app_name = app_name
        self._outdir = "/drozer_" + self.app_name + "_results"
        if self.full_path:
            self.full_path = self.full_path

    @full_path.setter
    def full_path(self, outdir):
        self._full_path = outdir.rstrip("/") + self._outdir

    @uri.setter
    def uri(self, uri):
        self._uri = uri

    @data.setter
    def data(self, data):
        self._sniff_data = data

    @category.setter
    def category(self, category):
        self._category = category

    @content_provider.setter
    def content_provider(self, provider):
        self._content_provider = provider

    # methods
    # run specific drozer scan
    def _run(self, cmd):
        command = cmd.value["cmd"] + self._app_name
        fname = cmd.value["fname"]
        msg = cmd.value["display"]

        final_command = self._drozer_cmd + ['-c', command, '--debug']
        print(msg)
        print(Fore.YELLOW + '[*] Command used ' + " ".join(final_command))
        with open(self._full_path + '/' + fname, "w") as outfile:
            subprocess.run(final_command, stdout=outfile, stderr=DEVNULL)

    # run all drozer scans
    def run_all(self):
        print(Fore.BLUE + "[*] Run all scans... This might take a while..."+ Fore.RESET)
        subprocess.run(['mkdir', self._full_path], stderr=DEVNULL)

        for command in (Commands):
            if command.name.startswith("COMMAND_"):
                self._run(command)
        print(Fore.BLUE + '[*] All checks are done! Files saved to ' + self._full_path + Fore.RESET)

    # Find specific app using drozer
    def find_app(self) -> list:
        final_command = self._drozer_cmd + ['-c', f'{Commands.FIND_APP.value["cmd"]} -f {self.query}', '--debug']
        print(Commands.FIND_APP.value["display"] + " Command used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.FIND_APP.value["cmd"]} -f {self.query}" --debug')
        output = subprocess.run(final_command, stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()
        apps = []

        for val in output[2:]:
            print(Fore.GREEN + '[+] ' + val)
            apps.append(val.split(" ")[0])

        return apps
        
    # Get a list of all installed apps
    def getAllApps(self) -> list:
        final_command = self._drozer_cmd + ['-c', Commands.FIND_APP.value["cmd"], '--debug']
        return list(map(lambda x: x.split(" ")[0] ,subprocess.run(final_command, stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()[2:])) 

    # start activity using intent
    def startActivity(self):
        # check if any non-required data is set and store the values
        if self._extras:
            for extra in self._extras:
                self._cmd += f" --extra {extra}"
        if self._deeplink:
            self._cmd += f" --data-uri {self._deeplink}"
        if self._intent_action:
            self._cmd += f" --action {self._intent_action}"
        if self._mimetype:
            self._cmd += f" --mimetype {self._mimetype}"

        # launch the drozer command
        code = f'{Commands.START_ACTIVITY.value["cmd"]}{self._app_name} {self._component}{self._cmd}\nexit'

        # print the command for PoCs
        print(Fore.YELLOW + Commands.START_ACTIVITY.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c \"{Commands.START_ACTIVITY.value["cmd"]}{self._app_name} {self._component}{self._cmd}\" --debug' + Fore.RESET)
        output = subprocess.run(self.drozer_cmd, input=code, stdout=DEVNULL, stderr=PIPE, encoding='UTF-8')
        
        # check for any errors and print to the console
        stderr = output.stderr.splitlines()
        if "warning" in output.stderr.lower():
            print(Fore.RED + f"[-] {stderr[2]}" + Fore.RESET)

    # Query the content provider
    def query_provider(self):
        fcmd = ""
        if self.content_provider:
            if self.content_provider["projection"]:
                fcmd += f' --projection {" ".join(self.provider["projection"])}'
            if self.content_provider["selection"]:
                fcmd += f' --selection {self.provider["selection"]}'
            if self.content_provider["selection_args"]:
                fcmd += f' --data-path {" ".join(self.provider["selection_args"])}'
            if self.content_provider["uri"]:
                fcmd += f"{self.content_provider['uri']}"
        final_command = self._drozer_cmd + ['-c', f'{Commands.QUERY_CONTENT.value["cmd"]} {fcmd.strip()}', '--debug']
        print(Commands.QUERY_CONTENT.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.QUERY_CONTENT.value["cmd"]} {fcmd.strip()}" --debug' + Fore.RESET)
        output = subprocess.run(final_command, stdout=DEVNULL, stderr=PIPE).stderr.decode()
        if "exception in module" in output:
            print(Fore.RED + f"[-] Could not get a ContentProviderClient for {self.content_provider['uri']}" + Fore.RESET)

    # Open DeepLinks
    def openDeeplink(self):
        fcmd = ""
        if self.intent_action:
            fcmd += f" --action {self.intent_action}"
        if self.data:
            if self.data["scheme"]:
                fcmd += f' --data-scheme {self.data["scheme"]}'
            if self.data["authority"]:
                fcmd += f' --data-authority {self.data["authority"]}'
            if self.data["path"]:
                fcmd += f' --data-path {self.data["path"]}'
            if self.data["type"]:
                fcmd += f' --data-type {self.data["type"]}'
        final_command = self._drozer_cmd + ['-c', f'{Commands.LAUNCH_DEEPLINK.value["cmd"]} {self.deeplink}', '--debug']
        print(Commands.FIND_APP.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.LAUNCH_DEEPLINK.value["cmd"]}{self.deeplink}" --debug' + Fore.RESET)
        output = subprocess.run(final_command, stdout=DEVNULL, stderr=PIPE).stderr.decode()
        if "exception in module" in output:
            print(Fore.RED + "[-] No Activity found to handle Intent { act=android.intent.action.VIEW dat="+ self.deeplink + " flg=0x10000000 (has extras) }" + Fore.RESET)

    # Sniff broadcast data
    def sniffData(self):
        fcmd = ""
        if self.intent_action:
            fcmd += f" --action {self.intent_action}"
        if self.data:
            if self.data["scheme"]:
                fcmd += f' --data-scheme {self.data["scheme"]}'
            if self.data["authority"]:
                fcmd += f' --data-authority {self.data["authority"]}'
            if self.data["path"]:
                fcmd += f' --data-path {self.data["path"]}'
            if self.data["type"]:
                fcmd += f' --data-type {self.data["type"]}'
        if self._category:
            fcmd += f" --category {self.category}"
        final_command = self.drozer_cmd + ['-c', f'{Commands.SNIFF_DATA.value["cmd"]}{fcmd}', '--debug']
        print(Commands.SNIFF_DATA.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.SNIFF_DATA.value["cmd"]}{fcmd}" --debug' + Fore.RESET)
        p = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=DEVNULL, bufsize=1, universal_newlines=True)
        while p.poll() is None:
            #line = p.stdout.read(2)
            line = p.stdout.readline()
            if line:
                if 'No broadcast receiver registered' in line:
                    print(Fore.RED + '[-] No broadcast receiver registered.' + Fore.RESET)
                    p.kill()
                    break
                elif 'CryptographyDeprecationWarning' or 'Selecting' in line:
                    pass
                else:
                    print(line.strip())

    # Insert Data in content provider
    def insert_provider(self):
        pass

    # Update data in content provider
    def update_provider(self):
        pass

    # Read data using content provider
    def read_provider(self):
        pass

    # Bypass SSL Pinning 
    def bypass_ssl(self):
        pass

    # Bypass ROOT detection by hooking System.Exit
    def bypass_root_exit(self):
        pass
    
    # Bypass root using frida
    def bypass_root_frida(self):
        pass

    # Patch apk and sign
    def patch_apk(self):
        pass

    # Patch IPA
    def patch_ipa(self):
        pass

    # Use reflutter to patch ssl pinning apk
    def reflutter_sslpinning(self):
        pass

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
        pass

    # Analyze Keystore
    def keystore_analyze(self):
        pass

def display(commands):
    print("Available data: " + " ".join(commands))

def back():
    print(Fore.YELLOW + "Returning to previous menu ..."+ Fore.RESET)

def quit():
    print(Fore.RED + "Quitting ..." + Fore.RESET)
    exit(0)

def unknown_cmd():
    print(Fore.RED + "[-] Unknown command" + Fore.RESET)

def listmodules(modules, descriptions):
    # Pretty print the available modules using string lengths 
    print("Available modules: ")

    max_value = len(max(modules + ["MODULE"], key=len))
    total = max_value + len(max(descriptions + ["DESCRIPTION"], key=len)) + len(Constants.DELIM.value) + 1
    
    header = "MODULE" + " " * (max_value - len("MODULE")) + Constants.DELIM.value + "DESCRIPTION"
    
    # print the header
    print("-"*total)
    print(header)
    print("-"*total)
    
    # print the values
    for i, data in enumerate(modules):
        print(data + " " * (max_value - len(data)) + Constants.DELIM.value + descriptions[i])
    
    # end the printing function
    print("-"*total)

def print_show_table(params):
    # Pretty print the show table by using the max value

    max_len_param = len("Param")
    max_len_required = len("REQUIRED")
    max_len_value = len("VALUE")
    max_len_desc = len("DESCRIPTION")
    
    # get the max values
    for data in params:
        value = data["value"]
        if type(data["value"]) == list:
            value = "[" + " ,".join(data["value"]) + "]"
        l1 = len(data["name"])
        l2 = len(value)
        l3 = len(data["description"])
        if  l1 > max_len_param:
            max_len_param = l1
        if l2 > max_len_value:
            max_len_value = l2
        if l3 > max_len_desc:
            max_len_desc = l3

    total_len = max_len_param + max_len_required + max_len_value + len(Constants.DELIM.value)*3 + max_len_desc + 1
    
    header = "PARAM" + " " * (max_len_param - len("PARAM")) + Constants.DELIM.value + "REQUIRED" + " " * (max_len_required-len("REQUIRED")) + Constants.DELIM.value + "VALUE" + " "* (max_len_value - len("VALUE")) + Constants.DELIM.value + "DESCRIPTION" + " "*max_len_desc
    dash = "-"

    # printing the data
    print(dash*total_len)
    print(header)
    print(dash*total_len)

    for data in params:
        # handle the required field
        required = "True"
        if "required" in data.keys():
            required = "False"  
        # value + " " * max - len(value) so it looks nice
        value = data["value"]
        if type(data["value"]) == list:
            value = "[" + ", ".join(data["value"]) + "]"
        
        print(data['name']  + " " * (max_len_param - len(data['name'])) + Constants.DELIM.value + required.upper() + " " * (max_len_required - len(required)) + Constants.DELIM.value + value  + " "* (max_len_value - len(value)) + Constants.DELIM.value + data["description"]+ " "*max_len_desc)
    print(dash * total_len)

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
            options = [i for i in mmsf.commands if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def execute(cmd):
            if cmd == "run":
                if mmsf.content_provider["uri"]:
                    mmsf.query_provider()
                    return 1
                else:
                    print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                    return 0              
            elif cmd == "show":
                print_show_table([
                    {"name": "URI", "value": mmsf.content_provider["uri"], "description": "The Content Provider URI to be tested."},
                    {"name": "PROJECTION", "value": mmsf.content_provider["projection"], "description": "The columns to SELECT, as in 'SELECT <projection> FROM table'.", "required": False},
                    {"name": "SELECTION", "value": mmsf.content_provider["selection"], "description": "The Condition to apply to the query, as in \"WHERE <condition>\". e.g. selection \"id=?\"", "required": False},
                    {"name": "SELECTION-ARGS", "value": mmsf.content_provider["selection_args"], "description": "The parameter to replace the '?' in the selection", "required": False}])
                return 0
            elif cmd == "exit":
                quit()
            elif cmd == "back":
                back()
                return 2

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
                if cmd.lower() == "uri"  and args:
                    content["uri"] = args[0].lower()
                elif cmd.lower() == "projection" and args:
                    content["projection"].append(args[0])
                elif cmd.lower() == "selection" and args:
                    content["selection"] = args[0]
                elif cmd.lower() == "selection_args" and args:
                    content["selection_args"].append(args[0])
                else:
                    mmsf.content_provider = content
                    if execute(cmd.lower()):
                        break
        else:
            if execute(value) == 2:
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
            options = [i for i in mmsf.commands if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def execute(cmd):
            if cmd == "run":
                if mmsf.content_provider["uri"] and mmsf.content_provider["insert_values"]:
                    mmsf.insert_provider()
                    return 1
                else:
                    print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                    return 0              
            elif cmd == "show":
                print_show_table([
                    {"name": "URI", "value": mmsf.content_provider["uri"], "description": "The Content Provider URI to be tested."},
                    {"name": "INSERT_VALUES", "value": mmsf.content_provider["insert_values"], "description": "The values required for insert. Choose between string, boolean, double, float, integer, long, short. e.g: string pass pass"}])
                return 0
            elif cmd == "exit":
                quit()
            elif cmd == "back":
                back()
                return 2

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
                if cmd.lower() == "uri"  and args:
                    content["uri"] = args[0].lower()
                elif cmd.lower() == "insert_values" and args:
                    args[0] = f'--{args[0]}'
                    content["insert_values"].extend(' '.join(args))
                else:
                    mmsf.content_provider = content
                    if execute(cmd.lower()):
                        break
        else:
            if execute(value) == 2:
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
            options = [i for i in mmsf.commands if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def execute(cmd):
            if cmd == "run":
                if mmsf.content_provider["uri"]:
                    mmsf.read_provider()
                    return 1
                else:
                    print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                    return 0              
            elif cmd == "show":
                print_show_table([
                    {"name": "URI", "value": mmsf.content_provider["uri"], "description": "The Content Provider URI to be tested."}])
                return 0
            elif cmd == "exit":
                quit()
            elif cmd == "back":
                back()
                return 2

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
                    mmsf.content_provider = content
                    if execute(cmd.lower()):
                        break
        else:
            if execute(value) == 2:
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
            options = [i for i in mmsf.commands if i.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        def execute(cmd):
            if cmd == "run":
                if mmsf.content_provider["uri"] and mmsf.content_provider["update_values"] and mmsf.content_provider["selection"] and mmsf.content_provider["selection_args"]:
                    mmsf.update_provider()
                    return 1
                else:
                    print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                    return 0              
            elif cmd == "show":
                print_show_table([
                    {"name": "URI", "value": mmsf.content_provider["uri"], "description": "The Content Provider URI to be tested."},
                    {"name": "UPDATE_VALUES", "value": mmsf.content_provider["update_values"], "description": "The values required for update. Choose between string, boolean, double, float, integer, long, short. e.g: --string pass pass"},
                    {"name": "SELECTION", "value": mmsf.content_provider["selection"], "description": "The Condition to apply to the query, as in \"WHERE <condition>\". e.g. selection \"id=?\""},
                    {"name": "SELECTION_ARGS", "value": mmsf.content_provider["selection_args"], "description": "The parameter to replace the '?' in the selection"}])
                return 0
            elif cmd == "exit":
                quit()
            elif cmd == "back":
                back()
                return 2

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
                if cmd.lower() == "uri"  and args:
                    content["uri"] = args[0].lower()
                elif cmd.lower() == "update_values":
                    args[0] = f'--{args[0]}'
                    content["update_values"].extend(" ".join(args))
                elif cmd.lower() == "selection":
                    content["selection"] = args[0]
                elif cmd.lower() == "selection_args":
                    content["selection_args"].append(args[0])
                else:
                    mmsf.content_provider = content
                    if execute(cmd.lower()):
                        break
        else:
            if execute(value) == 2:
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
                options = [i for i in mmsf.commands if i.startswith(text)]
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
                    elif len(inpt) < 2 and inpt[0] in mmsf.commands:
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
                options = [i for i in mmsf.commands if i.startswith(text)]
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
                options = [i for i in mmsf.commands if i.startswith(text)]
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
                options = [i for i in mmsf.commands if i.startswith(text)]
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
                options = [i for i in mmsf.commands if i.startswith(text)]
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
                options = [i for i in mmsf.commands if i.startswith(text)]
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
        
def main():

    mmsf = MassiveMobileSecurityFramework()
    apps = mmsf.all_apps
    initial_commands = ["usemodule", "exit", "listmodules"]
    readline.parse_and_bind("tab: complete")
    modules = ["scan", "broadcast", "intent", "provider", "find", "deeplink", "sniff"]
    descriptions = [
        "Scan the application to retrieve crucial information such as exported activities, path traversal, SQL injections, attack vector and so on.", 
        "Send a broadcast intent.",
        "Start an intent using supplied values like: extra values, action, mimetype or data.",
        "Query the exported content provider to extract data.",
        "Find the package name of an application and/or its details by supplying a filter keyword.", 
        "Launch a deeplink with supplied value",
        "Sniffing a broadcast intent"]

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