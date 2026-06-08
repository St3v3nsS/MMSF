import os
import shutil
from signal import SIGINT
import tempfile
import subprocess
from colorama import Fore
from subprocess import DEVNULL, PIPE
from Classes.constants import Constants
from Classes.utils import execute_frida_command, execute_frida_command_bg, stop_frida_session, find_command

class Frida:
    _config: dict

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, data):
        self._config = data

    def __repr__(self) -> str:
        pass

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, __o: object) -> bool:
        """Compare two class instances."""
        if __o.id == self.id:
            return True
        return False

    def __init__(self, low_power_mode=False) -> None:
        self.__init_frida()
        self.low_power_mode = low_power_mode
        self._config = {
            "mode": "-U",
            "app": "",
            "host": "127.0.0.1",
            "pause": "",
            "method": "-f"
        }
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = tempfile.mkstemp(dir=self.temp_dir, suffix=".js")[1]
        self.files = {
            'ssl-android':            os.path.join(self.temp_dir, 'frida-ssl-android.log'),
            'ssl-ios':                os.path.join(self.temp_dir, 'frida-ssl-ios.log'),
            'root-android':           os.path.join(self.temp_dir, 'frida-root-android.log'),
            'biometrics-ios':         os.path.join(self.temp_dir, 'frida-biometrics-ios.log'),
            'biometrics-android':     os.path.join(self.temp_dir, 'frida-biometrics-android.log'),
            'jailbreak-ios':          os.path.join(self.temp_dir, 'frida-jailbreak-ios.log'),
            'nsuserdefaults-modify':  os.path.join(self.temp_dir, 'frida-nsuserdefaults-modify.log'),
            'nsuserdefaults-retrieve':os.path.join(self.temp_dir, 'frida-nsuserdefaults-retrieve.log'),
            'ssl-flutter':            os.path.join(self.temp_dir, 'frida-ssl-flutter.log'),
            'task-hijacking':         os.path.join(self.temp_dir, 'frida-task-hijacking.log'),  # ← NEW
            'ssl-pinning-v2':         os.path.join(self.temp_dir, 'frida-ssl-pinning-v2.log'),
        }
        
        for file in self.files.keys():
            if (os.path.exists(self.files[file])):
                os.remove(self.files[file])
    
    def __del__(self):
        shutil.rmtree(self.temp_dir)

    def __init_frida(self):
        common_paths = ["/tmp/frida-server", "/data/local/tmp/frida-server"]
        for fpath in common_paths:
            p = subprocess.run(f'{Constants.ADB.value} shell ls {fpath}'.split(), stderr=PIPE, stdout=PIPE)
            if any("No such file or directory" in s for s in [p.stderr.decode(), p.stdout.decode()]):
                continue

            subprocess.run(f'{Constants.ADB.value} shell su -c "setprop persist.device_config.runtime_native.usap_pool_enabled false"'.split(), 
               stderr=subprocess.DEVNULL, 
               stdout=subprocess.DEVNULL, 
               timeout=5)
            subprocess.run(f'{Constants.ADB.value} shell su -c "setenforce 0"'.split(), stderr=DEVNULL, stdout=DEVNULL)
            cmd = f'{Constants.ADB.value} shell su -c "{fpath} -P &"'
            p = subprocess.Popen(cmd.split(), stdin=PIPE, stderr=PIPE, stdout=PIPE)

        subprocess.run([Constants.ADB.value, 'forward', 'tcp:27042', 'tcp:27042'], stderr=DEVNULL, stdout=DEVNULL)

        p = subprocess.run(['frida-ps', '-U'], stdout=PIPE, stderr=PIPE)
        if "Failed to enumerate processes: unable to find process with name 'system_server'" in p.stdout.decode():
            print(Fore.RED + '[-] frida is missing. Check your installation or install via mmsfupdate frida_server... Exitting... ')
            quit()

        print(Fore.BLUE + '[*] Frida is running' + Fore.RESET)

    def copy_file(self, type, api_v=''):
        path = Constants.DIR_FRIDA_SCRIPTS.value
        if type == "ssl":
            file = os.path.join(path, 'bypass_ssl_pinning_various_methods.js')
        elif type == "ssl-ios":
            file = os.path.join(path, 'ios13-pinning-bypass.js')
        elif type == "root":
            file = os.path.join(path, 'antiroot_bypass.js')
        elif type == "ios_biometrics":
            file = os.path.join(path, 'Fingerprint_bypasses/fingerprint-bypass-ios.js')
        elif type == "android_biometrics":
            file = os.path.join(path, f'Fingerprint_bypasses/fingerprint-android-{api_v}.js')
        elif type == "android_biometrics_crypto":
            file = os.path.join(path, 'Fingerprint_bypasses/fingerprint-bypass-via-exception-handling.js')
        elif type == "ios_jailbreak_bypass":
            file = os.path.join(path, 'ios-jailbreak-detection-bypass.js')
        elif type == "nsuserdefaults-modify":
            file = os.path.join(path, 'nsuserdefaults-modify.js')
            print(Fore.RED + file + Fore.RESET)
        elif type == "nsuserdefaults-retrieve":
            file = os.path.join(path, 'nsuserdefaults-retrieve.js')
            print(Fore.RED + file + Fore.RESET)
        elif type == "ssl-flutter":
            file = os.path.join(path, 'disable_flutter_tls.js')
        elif type == "task_hijacking":
            file = os.path.join(path, 'hook_task_hijacking.js')
        else:
            file = tempfile.mkstemp(dir=self.temp_dir, suffix=".js")
        
        with open(self.temp_file,'r') as secondfile:
            for line in secondfile:
                if (type == "root" and "[+] Antiroot bypass [+]" in line) or (type == "ssl" and "[#] Android Bypass for various Certificate Pinning methods [#]" in line) or (type == "ios_jailbreak_bypass" and "jailbreakPaths" in line) or (type == "ssl-flutter" and "disableFlutterTLS" in line):
                    return
        
        with open(file,'r') as firstfile, open(self.temp_file,'a') as secondfile:
            # read content from first file
            for line in firstfile:
                # write content to second file
                secondfile.write(line)

    def bypass_ssl(self):
        def exec_running():
            self.copy_file("ssl")
            print(Fore.GREEN + '[+] The command was executed successfully!' + Fore.RESET)
            
        def exec_new():
            self.copy_file("ssl")
            outfile = self.files['ssl-android']
            execute_frida_command(self.config,self.temp_file,outfile)

        found = find_command('frida', self.config["app"])
        if not found:
            exec_new()
        else:
            exec_running()

    def bypass_ssl_ios(self):
        def exec_running():
            self.copy_file("ssl-ios")
            print(Fore.GREEN + '[+] The command was executed successfully!' + Fore.RESET)
            
        def exec_new():
            self.copy_file("ssl-ios")
            outfile = self.files['ssl-ios']
            execute_frida_command(self.config,self.temp_file,outfile)

        found = find_command('frida', self.config["app"])
        if not found:
            exec_new()
        else:
            exec_running()

    def bypass_root(self):
        def exec_running():
            self.copy_file("root")
            print(Fore.GREEN + '[+] The command was executed successfully!' + Fore.RESET)
            
        def exec_new():
            self.copy_file("root")
            outfile = self.files['root-android']
            execute_frida_command(self.config,self.temp_file,outfile)

        found = find_command('frida', self.config["app"])
        if not found:
            exec_new()
        else:
            exec_running()
            
    def bypass_ios_biometrics(self):
        def exec_running():
            self.copy_file("ios_biometrics")
            print(Fore.GREEN + '[+] The command was executed successfully!' + Fore.RESET)
            
        def exec_new():
            self.copy_file("ios_biometrics")
            outfile = self.files['biometrics-ios']
            execute_frida_command(self.config,self.temp_file,outfile)

        found = find_command('frida', self.config["app"])
        if not found:
            exec_new()
        else:
            exec_running()
            
    def bypass_android_biometrics(self):
        def exec_running():
            self.copy_file("android_biometrics", api_version)
            print(Fore.GREEN + '[+] The command was executed successfully!' + Fore.RESET)
            
        def exec_new():
            self.copy_file("android_biometrics", api_version)
            outfile = self.files['biometrics-android']
            execute_frida_command(self.config,self.temp_file,outfile)

        api_version = subprocess.run(f'{Constants.ADB.value} shell getprop ro.build.version.release'.split(), stdout=PIPE, stderr=DEVNULL).stdout.decode().strip().split('.')[0]
        print(Fore.BLUE + f'[*] Detected Android API v{api_version}' + Fore.RESET)
        found = find_command('frida', self.config["app"])
        if not found:
            exec_new()
        else:
            exec_running()
            
    def bypass_android_biometrics_crypto_object(self):
        def exec_running():
            self.copy_file("android_biometrics_crypto")
            print(Fore.GREEN + '[+] The command was executed successfully!' + Fore.RESET)
            
        def exec_new():
            self.copy_file("android_biometrics_crypto")
            outfile = self.files['biometrics-ios']
            execute_frida_command(self.config,self.temp_file,outfile)

        found = find_command('frida', self.config["app"])
        if not found:
            exec_new()
        else:
            exec_running()
            
    def bypass_ios_jailbreak(self):
        def exec_running():
            self.copy_file("ios_jailbreak_bypass")
            print(Fore.GREEN + '[+] The command was executed successfully!' + Fore.RESET)
            
        def exec_new():
            self.copy_file("ios_jailbreak_bypass")
            outfile = self.files['jailbreak-ios']
            execute_frida_command(self.config, self.temp_file, outfile)

        found = find_command('frida', self.config["app"])
        if not found:
            exec_new()
        else:
            exec_running()

    def nsuserdefaults_modify(self):
        def exec_running():
            self.copy_file("nsuserdefaults-modify")
            self.config["method"] = "-F"
            outfile = self.files['nsuserdefaults-modify']
            execute_frida_command(self.config, self.temp_file, outfile, True)
            # print(Fore.GREEN + '[+] The command was executed successfully!' + Fore.RESET)
            
        def exec_new():
            self.copy_file("nsuserdefaults-modify")
            cmd = f'frida {self._config["mode"]} {self.config["method"]} {self._config["app"]} -l {self.temp_file} {self._config["pause"]}'
            outfile = self.files['nsuserdefaults-modify']
            execute_frida_command(self.config, self.temp_file, outfile, True)

        found = find_command('frida', self.config["app"])
        if not found:
            exec_new()
        else:
            exec_running()

    def nsuserdefaults_retrieve(self):
        def exec_running():
            self.copy_file("nsuserdefaults-retrieve")
            self.config["method"] = "-F"
            outfile = self.files['nsuserdefaults-retrieve']
            execute_frida_command(self.config, self.temp_file, outfile, True)
            # print(Fore.GREEN + '[+] The command was executed successfully!' + Fore.RESET)
            
        def exec_new():
            self.copy_file("nsuserdefaults-retrieve")
            cmd = f'frida {self._config["mode"]} {self.config["method"]} {self._config["app"]} -l {self.temp_file} {self._config["pause"]}'
            outfile = self.files['nsuserdefaults-retrieve']
            execute_frida_command(self.config, self.temp_file, outfile, True)

        found = find_command('frida', self.config["app"])
        if not found:
            exec_new()
        else:
            exec_running()

    def bypass_flutter_ssl(self):
        def exec_running():
            self.copy_file("ssl-flutter")
            print(Fore.GREEN + '[+] The command was executed successfully!' + Fore.RESET)

        def exec_new():
            self.copy_file("ssl-flutter")
            outfile = self.files['ssl-flutter']
            execute_frida_command(self.config, self.temp_file, outfile, False, "Attached SSL Pinning on Flutter")

        found = find_command('frida', self.config["app"])
        if not found:
            exec_new()
        else:
            exec_running()

    @staticmethod
    def _normalize_cert(cert_pem: str) -> str:
        """
        Accept any of:
          - A file path to a .pem / .crt file
          - A full PEM string (with -----BEGIN/END CERTIFICATE----- headers)
          - Raw base64 body only
        Returns ONLY the raw base64 body (no headers, no blank lines).
        """
        raw = cert_pem.strip()
        if os.path.isfile(raw):
            with open(raw, 'r') as f:
                raw = f.read().strip()
        lines = []
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith('-----'):
                continue
            lines.append(line)
        return '\n'.join(lines)

    def copy_file_v2(self, proxy_host, proxy_port, cert_pem):
        """
        Merge config.js (with injected values) + all hook scripts into
        self.temp_file, ready for: frida -U -l <temp_file> -f <package>
        """
        scripts_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'Frida_Scripts', 'sslpinning'
        )

        # Normalise cert → raw base64 body, then re-wrap cleanly
        b64_body = self._normalize_cert(cert_pem)
        if not b64_body:
            raise ValueError('[!] CERT_PEM is empty or could not be parsed.')
        clean_pem = f'-----BEGIN CERTIFICATE-----\n{b64_body}\n-----END CERTIFICATE-----'
        print(Fore.BLUE + f'[*] Certificate loaded ({len(b64_body)} base64 chars)' + Fore.RESET)

        # Reset temp file
        open(self.temp_file, 'w').close()

        # 1. Inject proxy/cert values into config.js
        config_path = os.path.join(scripts_dir, 'config.js')
        with open(config_path, 'r') as f:
            config_src = f.read()

        # Replace the entire template-literal PEM block (headers + placeholder)
        import re
        config_src = re.sub(
            r'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----',
            clean_pem,
            config_src,
            flags=re.DOTALL
        )
        config_src = config_src.replace(
            "const PROXY_HOST = '127.0.0.1';",
            f"const PROXY_HOST = '{proxy_host}';"
        ).replace(
            "const PROXY_PORT = 8000;",
            f"const PROXY_PORT = {proxy_port};"
        )

        with open(self.temp_file, 'a') as out:
            out.write(config_src)
            out.write('\n\n')

        # 2. Append hook scripts in the correct load order
        hook_scripts = [
            'native-connect-hook.js',
            'native-tls-hook.js',
            os.path.join('android', 'android-proxy-override.js'),
            os.path.join('android', 'android-system-certificate-injection.js'),
            os.path.join('android', 'android-certificate-unpinning.js'),
            os.path.join('android', 'android-certificate-unpinning-fallback.js'),
        ]

        with open(self.temp_file, 'a') as out:
            for script in hook_scripts:
                script_path = os.path.join(scripts_dir, script)
                print(Fore.YELLOW + f'[*] Appending: {script}' + Fore.RESET)
                with open(script_path, 'r') as f:
                    out.write(f'\n// \u2500\u2500 {script} \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n')
                    out.write(f.read())
                    out.write('\n')

    def bypass_ssl_v2(self, proxy_host, proxy_port, cert_pem):
        """
        SSL Pinning bypass using the httptoolkit multi-script stack.
        Equivalent to running:
          frida -U -l config.js -l native-connect-hook.js -l native-tls-hook.js
                -l android/android-proxy-override.js
                -l android/android-system-certificate-injection.js
                -l android/android-certificate-unpinning.js
                -l android/android-certificate-unpinning-fallback.js
                -f <package>
        All scripts are merged into a single temp file and loaded as one.
        """
        print(Fore.YELLOW + '[*] Building combined SSL Pinning v2 script...' + Fore.RESET)
        self.copy_file_v2(proxy_host, proxy_port, cert_pem)
        outfile = self.files['ssl-pinning-v2']
        execute_frida_command(self.config, self.temp_file, outfile)

    def hook_task_hijacking(self):
        """
        Spawn/attach to the victim app, load the task-hijacking hook script,
        and keep the frida session running in background so MMSF stays usable.
        New activity lifecycle events print live as they happen.
        """
        def exec_new():
            self.copy_file("task_hijacking")
            outfile = self.files['task-hijacking']
            execute_frida_command_bg(
                self.config,
                self.temp_file,
                outfile,
                self._active_sessions,
                session_key='task-hijacking',
                confirmation='[MMSF] Task Hijacking hooks loaded'
            )

        def exec_running():
            # frida already attached to this app — just hot-reload the extra script
            self.copy_file("task_hijacking")
            print(Fore.GREEN + '[+] Task-hijacking hooks appended to live frida session.' + Fore.RESET)

        found = find_command('frida', self.config["app"])
        if not found:
            exec_new()
        else:
            exec_running()

    def stop_task_hijacking(self):
        """Detach the background task-hijacking frida session."""
        stop_frida_session(self._active_sessions, 'task-hijacking')