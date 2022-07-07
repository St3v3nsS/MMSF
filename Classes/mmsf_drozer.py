import subprocess
from subprocess import DEVNULL, PIPE

from Classes.commands import Commands
from .constants import Constants
from colorama import Fore
import requests


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
        self._outdir = "/drozer_" + self.app_name + "_results"
        if self.full_path:
            self.full_path = self.full_path

    @full_path.setter
    def full_path(self, outdir):
        self._full_path = outdir.rstrip("/") + self._outdir

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
        self._agent_apk_path = '~/.mmsf/utils/drozer-agent.apk'
        self.__init_drozer()
        self._app_name, self._find_app_query, self._send_type, self._full_path, self._outdir = "", "", "", "", ""
        self._sniff_data = {
            "authority": "",
            "scheme": "",
            "path": "",
            "type": "",
            "category": ""
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
            "component": "",
            "extras": [],
            "deeplink": "",
            "intent_action": "",
            "mimetype": ""
        }

    def __check_is_running(self):
        return subprocess.run(self._drozer_devices, stdout=PIPE, stderr=DEVNULL).stdout.decode().splitlines()

    def __start_agent(self):
        return subprocess.run([self._adb, 'shell', 'am', 'startservice', '-n', 'com.mwr.dz/.services.ServerService', '-c', 'com.mwr.dz.START_EMBEDDED'], stderr=PIPE, stdout=DEVNULL)

    def __adb_forward_tcp(self):
        subprocess.run([self._adb, 'forward', 'tcp:31415', 'tcp:31415'], stderr=DEVNULL, stdout=DEVNULL)

    def __init_drozer(self):
        
        if not self.__check_is_running():
            print(Fore.RED + "[-] Drozer is not running... Trying to wake the Agent... "+ Fore.RESET)
            stderr = self.__start_agent().stderr.decode().splitlines()
            if stderr and "Not found" in stderr[0]:
                print(Fore.RED + "[-] Drozer Agent is not installed on the phone. Installing ..." + Fore.RESET)
                self.__download_agent()
                self.__install_agent()
                self.__start_agent()
                self.__adb_forward_tcp()
            else:
                self.__adb_forward_tcp()
        else:
            print(Fore.BLUE + "[*] Drozer Agent is waiting for your commands!" + Fore.RESET)

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
        print(Fore.BLUE + '[*] All checks are done! Files saved to ' + self._drozer.full_path + Fore.RESET)

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
        
    # start activity using intent
    def start_activity(self):
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
                fcmd += f' --selection-args {" ".join(self.provider["selection_args"])}'
            if self.content_provider["uri"]:
                fcmd += f"{self.content_provider['uri']}"
        final_command = self._drozer_cmd + ['-c', f'{Commands.QUERY_CONTENT.value["cmd"]} {fcmd.strip()}', '--debug']
        print(Commands.QUERY_CONTENT.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.QUERY_CONTENT.value["cmd"]} {fcmd.strip()}" --debug' + Fore.RESET)
        output = subprocess.run(final_command, stdout=DEVNULL, stderr=PIPE).stderr.decode()
        if "exception in module" in output:
            print(Fore.RED + f"[-] Could not get a ContentProviderClient for {self.content_provider['uri']}" + Fore.RESET)

    # Open DeepLinks
    def open_deeplink(self):
        final_command = self._drozer_cmd + ['-c', f'{Commands.LAUNCH_DEEPLINK.value["cmd"]} {self.deeplink}', '--debug']
        print(Commands.FIND_APP.value["display"] + "\nCommand used: " + " ".join(self._drozer_cmd) + f' -c "{Commands.LAUNCH_DEEPLINK.value["cmd"]}{self.deeplink}" --debug' + Fore.RESET)
        output = subprocess.run(final_command, stdout=DEVNULL, stderr=PIPE).stderr.decode()
        if "exception in module" in output:
            print(Fore.RED + "[-] No Activity found to handle Intent { act=android.intent.action.VIEW dat="+ self.deeplink + " flg=0x10000000 (has extras) }" + Fore.RESET)

    # Sniff broadcast data
    def sniff_broadcast_data(self):
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
        fcmd = ""
        if self.content_provider:
            if self.content_provider["insert_values"]:
                fcmd += f'{" ".join(self.provider["projection"])}'
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
                fcmd += f'{" ".join(self.provider["projection"])}'
            if self.content_provider["selection"]:
                fcmd += f' --selection {self.provider["selection"]}'
            if self.content_provider["selection_args"]:
                fcmd += f' --selection-args {" ".join(self.provider["selection_args"])}'
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
