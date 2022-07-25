from ntpath import join
import os
import subprocess
from subprocess import DEVNULL, PIPE

from Classes.commands import Commands
from .constants import Constants
from colorama import Fore
import requests

# Set the unbuffered output
os.environ.setdefault('PYTHONUNBUFFERED', '1')

class drozer:
    id: str
    _app_name: str
    _outdir: str
    _full_path: str
    _find_app_query: str
    _send_type: str
    _content_provider: dict
    _sniff_data: dict
    _activity: dict

    # getters
    @property
    def app_name(self):
        return self._app_name

    @property
    def full_path(self):
        return self._full_path

    @property
    def find_app_query(self):
        return self._find_app_query

    @property
    def send_type(self):
        return self._send_type

    @property
    def sniff_data(self):
        return self._sniff_data

    @property
    def content_provider(self):
        return self._content_provider

    @property
    def activity(self):
        return self._activity

    # setters
    @app_name.setter
    def app_name(self, app_name):
        self._app_name = app_name
        self._outdir = Constants.DIR_SCANS_PATH.value + "/drozer_" + self.app_name + "_results"
        if self.full_path:
            self.full_path = self.full_path

    @full_path.setter
    def full_path(self, outdir):
        self._full_path = os.path.join(outdir, self._outdir)

    @find_app_query.setter
    def find_app_query(self, data):
        self._find_app_query = data

    @send_type.setter
    def send_type(self, data):
        self._send_type = data

    @sniff_data.setter
    def sniff_data(self, data):
        self._sniff_data = data

    @content_provider.setter
    def content_provider(self, provider):
        self._content_provider = provider

    @activity.setter
    def activity(self, data):
        self._activity = data

    def __repr__(self) -> str:
        pass

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, __o: object) -> bool:
        """Compare two class instances."""
        if __o.id == self.id:
            return True
        return False

    def __init__(self) -> None:
        self._drozer_cmd = ['drozer', 'console', 'connect']
        self._drozer_devices = ['drozer', 'console', 'devices']
        self._agent_apk_path = os.path.join(Constants.DIR_UTILS_PATH.value, 'drozer-agent.apk')
        self.__init_drozer()
        self._app_name, self._find_app_query, self._send_type, self._full_path, self._outdir = "", "", "", "", Constants.DIR_SCANS_PATH.value
        self._sniff_data = {
            "authority": "",
            "scheme": "",
            "path": "",
            "type": "",
            "category": "",
            "intent_action": ""
        }
        self._content_provider = {
            "uri": "",
            "selection": "",            
            "projection": [],
            "selection_args": [],
            "insert_values": [],
            "update_values": []
        }
        self._activity = {
            "app_name": "",
            "component": "",
            "extras": [],
            "deeplink": "",
            "intent_action": "",
            "mimetype": ""
        }

    def __check_is_running(self):
        try:
            p = subprocess.run(self._drozer_devices, capture_output=True)
            return p.stdout.decode().splitlines()
        except Exception as e:
            return False

    def __start_agent(self):
        try:
            p = subprocess.run([Constants.ADB.value, 'shell', 'am', 'startservice', '-n', 'com.mwr.dz/.services.ServerService', '-c', 'com.mwr.dz.START_EMBEDDED'], stderr=DEVNULL, stdout=DEVNULL)
            return p.stderr.decode().splitlines()
        except Exception as e:
            return ["Not Found"]

    def __adb_forward_tcp(self):
        subprocess.run([Constants.ADB.value, 'forward', 'tcp:31415', 'tcp:31415'], stderr=DEVNULL, stdout=DEVNULL)

    def __init_drozer(self):
        
        if not self.__check_is_running():
            print(Fore.RED + "[-] Drozer is not running... Trying to wake the Agent... "+ Fore.RESET)
            stderr = self.__start_agent()
            if stderr and "Not found" in stderr[0] or 'error' in stderr[0]:
                print(Fore.RED + "[-] Drozer Agent is not installed on the phone. Installing ..." + Fore.RESET)
                self.__download_agent()
                self.__install_agent()
                self.__start_agent()
                self.__adb_forward_tcp()
            else:
                self.__adb_forward_tcp()
        else:
            print(Fore.BLUE + "[+] Drozer Agent is running!" + Fore.RESET)

    def __download_agent(self): 
        url = "https://github.com/mwrlabs/drozer/releases/download/2.3.4/drozer-agent-2.3.4.apk"
        drozer_agent = requests.get(url)
        open(self._agent_apk_path, 'wb').write(drozer_agent.content)

    def __install_agent(self):
        print(Fore.BLUE + "[*] Installing apk... Please be patient"+ Fore.RESET)
        proc = subprocess.run([Constants.ADB.value, 'install', self._agent_apk_path], stderr=PIPE, stdout=DEVNULL)
        if proc.stderr:
            print(proc.stderr)
            exit(-1)
        else:
            print(Fore.GREEN + "[+] Successfully installed Drozer Agent!" + Fore.RESET)

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
        if not os.path.isdir(self.full_path):
            try:
                os.mkdir(self.full_path)
            except OSError as e:
                print(Fore.LIGHTBLUE_EX + '[DEBUG] ' + e + Fore.RESET)

        for command in (Commands):
            if command.name.startswith("COMMAND_"):
                self._run(command)
        print(Fore.BLUE + '[*] All checks are done! Files saved to ' + self.full_path + Fore.RESET)

    # Find specific app using drozer
    def find_app(self) -> list:
        final_command = self._drozer_cmd + ['-c', f'{Commands.FIND_APP.value["cmd"]} -f {self.find_app_query}', '--debug']
        print(Commands.FIND_APP.value["display"] + " Command used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.FIND_APP.value["cmd"]} -f {self.find_app_query}" --debug')
        output = subprocess.run(final_command, stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()
        apps = []

        for val in output[2:]:
            print(Fore.GREEN + '[+] ' + val)
            apps.append(val.split(" ")[0])

        return apps
        
    # start activity using intent
    def start_activity(self):
        fcmd = ""
        # check if any non-required data is set and store the values
        if self._activity["extras"]:
            for extra in self._activity["extras"]:
                fcmd += f" --extra {extra}"
        if self._activity["deeplink"]:
            fcmd += f" --data-uri {self._activity['deeplink']}"
        if self._activity["intent_action"]:
            fcmd += f" --action {self._activity['intent_action']}"
        if self.activity['mimetype']:
            fcmd += f" --mimetype {self._activity['mimetype']}"

        # launch the drozer command
        code = f'{Commands.START_ACTIVITY.value["cmd"]}{self._activity["app_name"]} {self._activity["component"]}{fcmd}\nexit'

        # print the command for PoCs
        print(Fore.YELLOW + Commands.START_ACTIVITY.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c \"{Commands.START_ACTIVITY.value["cmd"]}{self._activity["app_name"]} {self._activity["component"]}{fcmd}\" --debug' + Fore.RESET)
        output = subprocess.run(self._drozer_cmd, input=code, stdout=DEVNULL, stderr=PIPE, encoding='UTF-8')
        
        # check for any errors and print to the console
        stderr = output.stderr.splitlines()
        if "warning" in output.stderr.lower():
            print(Fore.RED + f"[-] {stderr[2]}" + Fore.RESET)

    # start activity using intent
    def send_broadcast(self):
        fcmd = ""
        if self.activity["app_name"] and self.activity["component"]:
            fcmd += f'--component {self.activity["app_name"]} {self.activity["component"]}'
        # check if any non-required data is set and store the values
        if self._activity["extras"]:
            for extra in self._activity["extras"]:
                fcmd += f" --extra {extra}"
        if self._activity["deeplink"]:
            fcmd += f" --data-uri {self._activity['deeplink']}"
        if self._activity["intent_action"]:
            fcmd += f" --action {self._activity['intent_action']}"
        if self.activity['mimetype']:
            fcmd += f" --mimetype {self._activity['mimetype']}"

        # launch the drozer command
        code = f'{Commands.SEND_BROADCAST.value["cmd"]}{fcmd}\nexit'

        # print the command for PoCs
        print(Fore.YELLOW + Commands.SEND_BROADCAST.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c \"{Commands.SEND_BROADCAST.value["cmd"]}{fcmd}\" --debug' + Fore.RESET)
        output = subprocess.run(self._drozer_cmd, input=code, stdout=DEVNULL, stderr=PIPE, encoding='UTF-8')
        
        # check for any errors and print to the console
        stderr = output.stderr.splitlines()
        if "warning" in output.stderr.lower() and len(stderr)>=3:
            print(Fore.RED + f"[-] Error: {' '.join(stderr[2:])}" + Fore.RESET)
        else:
            print(Fore.GREEN + '[+] Command ran successfully' + Fore.RESET)

    # Query the content provider
    def query_provider(self):
        fcmd = ""
        if self.content_provider:
            if self.content_provider["projection"]:
                fcmd += f' --projection {" ".join(self.content_provider["projection"])}'
            if self.content_provider["selection"]:
                fcmd += f' --selection {self.content_provider["selection"]}'
            if self.content_provider["selection_args"]:
                fcmd += f' --selection-args {" ".join(self.content_provider["selection_args"])}'
            if self.content_provider["uri"]:
                fcmd += f"{self.content_provider['uri']}"
        final_command = self._drozer_cmd + ['-c', f'{Commands.QUERY_CONTENT.value["cmd"]} {fcmd.strip()}', '--debug']
        print(Commands.QUERY_CONTENT.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.QUERY_CONTENT.value["cmd"]} {fcmd.strip()}" --debug' + Fore.RESET)
        output = subprocess.run(final_command, stdout=DEVNULL, stderr=PIPE).stderr.decode()
        if "exception in module" in output:
            print(Fore.RED + f"[-] Could not get a ContentProviderClient for {self.content_provider['uri']}" + Fore.RESET)

    # Open DeepLinks
    def open_deeplink(self):
        final_command = self._drozer_cmd + ['-c', f'{Commands.LAUNCH_DEEPLINK.value["cmd"]} {self.activity["deeplink"]}', '--debug']
        print(Commands.LAUNCH_DEEPLINK.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.LAUNCH_DEEPLINK.value["cmd"]}{self.activity["deeplink"]}" --debug' + Fore.RESET)
        output = subprocess.run(final_command, stdout=DEVNULL, stderr=PIPE).stderr.decode()
        if "exception in module" in output:
            print(Fore.RED + "[-] No Activity found to handle Intent { act=android.intent.action.VIEW dat="+ self.activity["deeplink"] + " flg=0x10000000 (has extras) }" + Fore.RESET)

    # Sniff broadcast data
    def sniff_broadcast_data(self):
        fcmd = ""
        if self.sniff_data:
            if self.sniff_data["intent_action"]:
                fcmd += f" --action {self.sniff_data['intent_action']}"
            if self.sniff_data["scheme"]:
                fcmd += f' --data-scheme {self.sniff_data["scheme"]}'
            if self.sniff_data["authority"]:
                fcmd += f' --data-authority {self.sniff_data["authority"]}'
            if self.sniff_data["path"]:
                fcmd += f' --data-path {self.sniff_data["path"]}'
            if self.sniff_data["type"]:
                fcmd += f' --data-type {self.sniff_data["type"]}'
        if self.sniff_data['category']:
            fcmd += f" --category {self.sniff_data['category']}"
        final_command = self._drozer_cmd + ['-c', f'{Commands.SNIFF_DATA.value["cmd"]}{fcmd}', '--debug']
        print(Commands.SNIFF_DATA.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.SNIFF_DATA.value["cmd"]}{fcmd}" --debug' + Fore.RESET)
        p = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=DEVNULL, bufsize=1, universal_newlines=True)
        while p.poll() is None:
            #line = p.stdout.read(2)
            line = p.stdout.readline()
            if line.strip():
                print(line.strip())
                if 'No broadcast receiver registered' in line.strip():
                    # print(Fore.RED + '[-] No broadcast receiver registered.' + Fore.RESET)
                    p.kill()
                    break
                # elif 'CryptographyDeprecationWarning' or 'Selecting' in line.strip():
                #     pass
                # else:
                #     print(line.strip())

    # Insert Data in content provider
    def insert_provider(self):
        fcmd = ""
        if self.content_provider:
            if self.content_provider["insert_values"]:
                fcmd += f'{" ".join(self.content_provider["projection"])}'
            if self.content_provider["uri"]:
                fcmd += f" {self.content_provider['uri']}"
        final_command = self._drozer_cmd + ['-c', f'{Commands.INSERT_PROVIDER.value["cmd"]} {fcmd.strip()}', '--debug']
        print(Commands.INSERT_PROVIDER.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.INSERT_PROVIDER.value["cmd"]} {fcmd.strip()}" --debug' + Fore.RESET)
        output = subprocess.run(final_command, stdout=DEVNULL, stderr=PIPE).stderr.decode()
        if "exception in module" in output:
            print(Fore.RED + f"[-] Could not get a ContentProviderClient for {self.content_provider['uri']}" + Fore.RESET)

    # Update data in content provider
    def update_provider(self):
        fcmd = ""
        if self.content_provider:
            if self.content_provider["update_values"]:
                fcmd += f'{" ".join(self.content_provider["projection"])}'
            if self.content_provider["selection"]:
                fcmd += f' --selection {self.provider["selection"]}'
            if self.content_provider["selection_args"]:
                fcmd += f' --selection-args {" ".join(self.content_provider["selection_args"])}'
            if self.content_provider["uri"]:
                fcmd += f"{self.content_provider['uri']}"
        final_command = self._drozer_cmd + ['-c', f'{Commands.UPDATE_PROVIDER.value["cmd"]} {fcmd.strip()}', '--debug']
        print(Commands.UPDATE_PROVIDER.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.UPDATE_PROVIDER.value["cmd"]} {fcmd.strip()}" --debug' + Fore.RESET)
        output = subprocess.run(final_command, stdout=DEVNULL, stderr=PIPE).stderr.decode()
        if "exception in module" in output:
            print(Fore.RED + f"[-] Could not get a ContentProviderClient for {self.content_provider['uri']}" + Fore.RESET)

    # Read data using content provider
    def read_provider(self):
        fcmd = ""
        if self.content_provider:
            if self.content_provider["projection"]:
                fcmd += f' --projection {" ".join(self.content_provider["projection"])}'
            if self.content_provider["selection"]:
                fcmd += f' --selection {self.content_provider["selection"]}'
            if self.content_provider["selection_args"]:
                fcmd += f' --data-path {" ".join(self.content_provider["selection_args"])}'
            if self.content_provider["uri"]:
                fcmd += f"{self.content_provider['uri']}"
        final_command = self._drozer_cmd + ['-c', f'{Commands.QUERY_CONTENT.value["cmd"]} {fcmd.strip()}', '--debug']
        print(Commands.QUERY_CONTENT.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.QUERY_CONTENT.value["cmd"]} {fcmd.strip()}" --debug' + Fore.RESET)
        output = subprocess.run(final_command, stdout=DEVNULL, stderr=PIPE).stderr.decode()
        if "exception in module" in output:
            print(Fore.RED + f"[-] Could not get a ContentProviderClient for {self.content_provider['uri']}" + Fore.RESET)
