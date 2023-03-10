import os
import shutil
import subprocess
from subprocess import DEVNULL, PIPE
from colorama import Fore
from Classes.constants import Constants
import xml.etree.ElementTree as ET


class apktool:
    
    id: str
    _config: dict

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, data):
        self._config = data

    def __init__(self, low_power_mode=False) -> None:
        self._config = {
            "dir_name": "base",
            "app": "",
            "path": Constants.DIR_PULLED_APKS.value,
            "mode": "d",
            "apk": "base",
            "out_apk": Constants.PATCHED_APK.value,
            "in_apk": Constants.GENERATED_APK.value,
        }
        self.low_power_mode = low_power_mode
        self.reconfigure()
        self.__init_java()
        self.__init_apktool()

    def __init_apktool(self):
        print(Fore.BLUE + "[*] apktool is running!" + Fore.RESET)

    def __init_java(self):
        print(Fore.BLUE + "[*] java is running!" + Fore.RESET)       

    def reconfigure(self, sign=False):
        if self.config["apk"].endswith(".apk"):
            self.config["apk"] = self.config["apk"][:-len(".apk")]
        self.config["apk"] += '.apk'
        if sign:
            self._generated_apk = os.path.join(self.config["path"], self.config['in_apk'].rstrip('.apk') + '.apk') if self.config["in_apk"] != 'base' or self.config["path"] != Constants.DIR_PULLED_APKS.value  else Constants.GENERATED_APK.value
            self._patched_apk = os.path.join(self.config["path"], self.config['out_apk'].rstrip('.apk') + '_patched.apk') if self.config["out_apk"] != 'base' or self.config["path"] != Constants.DIR_PULLED_APKS.value  else Constants.PATCHED_APK.value
        else:
            self._generated_apk = os.path.join(self.config["path"], self.config['apk'].rstrip('.apk') + '.apk') if self.config["apk"] != 'base' or self.config["path"] != Constants.DIR_PULLED_APKS.value  else Constants.GENERATED_APK.value
            self._patched_apk = os.path.join(self.config["path"], self.config['apk'].rstrip('.apk') + '_patched.apk') if self.config["apk"] != 'base' or self.config["path"] != Constants.DIR_PULLED_APKS.value  else Constants.PATCHED_APK.value
        self._apk_dir = os.path.join(self.config["path"], self.config["dir_name"])

    def _decompile_apk(self, path_to_apk="default"):
        apk_path = self._get_default(path_to_apk)
        print(apk_path)
        cmd_to_run = ['apktool', 'd', apk_path, '-o', self._apk_dir,'-f']
        p = subprocess.run(cmd_to_run, stderr=PIPE, stdout=DEVNULL)
        self._handle_errors(p)

    def generate_apk(self):
        self.reconfigure()
        cmd_to_run = ['apktool', 'b', '-o', self._generated_apk, self._apk_dir]
        p = subprocess.run(cmd_to_run, stderr=PIPE, stdout=DEVNULL)
        self._handle_errors(p)
        print(Fore.GREEN + '[+] APK generated to: ' + self._generated_apk + Fore.RESET)

    def sign_apk(self):
        self.reconfigure(sign=True)
        pwd = "123456"
        keystore_path = os.path.join(Constants.DIR_UTILS_PATH.value ,'keystore.jsk')
        if not os.path.isfile(keystore_path):
            keytool_cmd = ['keytool', '-genkey', '-noprompt', '-keystore', keystore_path, '-alias', 'alias_name', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000', '-storepass', pwd, '-keypass', pwd, '-dname', "CN=signer.com, OU=ID, O=IB, L=John, S=Doe, C=GB"]
            p = subprocess.run(keytool_cmd, stderr=PIPE, stdout=PIPE)
            self._handle_errors(p)
            
        else:
            cmd_to_run = ['apksigner', 'sign', '--ks', keystore_path, '--out', self._patched_apk, self._generated_apk]
            p = subprocess.run(cmd_to_run, input=pwd.encode('UTF-8'), stderr=PIPE, stdout=DEVNULL)
            self._handle_errors(p)
            print(Fore.GREEN + '[+] APK Signed: ' + self._patched_apk + Fore.RESET)

    def install_apk(self):
        self.reconfigure()
        cmd_to_exec = [Constants.ADB.value, 'install', '-r', self.config["apk"]]
        p = subprocess.run(cmd_to_exec, stderr=PIPE, stdout=DEVNULL)
        if "INSTALL_FAILED_TEST_ONLY" in p.stderr.decode():
            p2 = subprocess.run(cmd_to_exec[:-1] + ['-t'] + [self.config["apk"]], stderr=PIPE, stdout=DEVNULL)
            self._handle_errors(p2)
        else:
            self._handle_errors(p)

    def _handle_errors(self, p):
        if p.stderr:
            print(Fore.RED + '[-] ' + p.stderr.decode() + Fore.RESET)
        else:
            print(Fore.GREEN + "[+] Success" + Fore.RESET)
       
    def _get_default(self, path_to_apk="default"):
        print(self._patched_apk)
        print(path_to_apk)
        return self._patched_apk if path_to_apk == "default" else path_to_apk

    def _modify_network_config(self, path_to_apk="default"):
        if path_to_apk == "default":
            path_to_apk = self._apk_dir
        
        path = os.path.join(path_to_apk, "res/xml/network_security_config.xml")

        def network_file_exists():
            return os.path.isfile(path)

        def create():
            if not os.path.isdir(os.path.join(path_to_apk, "res/xml")):
                os.makedirs(os.path.join(path_to_apk, "res/xml"))
            print(Fore.GREEN + '[*] Creating Network Security Config..' + Fore.RESET)    
            write_xml_file()
            add_to_manifest()


        def write_xml_file():
            shutil.copy(os.path.join(Constants.DIR_INSTALLDIR.value, 'apktool_files/network_security_config.xml'), path)

        def modify():
            mytree = ET.parse(path)
            myroot = mytree.getroot()
            base_config = myroot.find("base-config")
            if base_config is not None:
                trust_anchors = base_config.find("trust-anchors")
                if trust_anchors is not None:
                    ET.SubElement(trust_anchors, 'certificates')
                    for temp in myroot.iter('certificates'):
                        if 'src' not in temp.attrib:
                            temp.set("src", "user")
            mytree.write(path)

        def add_to_manifest():
            manifest_path = os.path.join(path_to_apk, "AndroidManifest.xml")
            mytree = ET.parse(manifest_path)
            ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
            myroot = mytree.getroot()
            myroot.find('application').set("android:networkSecurityConfig", "@xml/network_security_config")
            print(Fore.GREEN + '[*] Adding to Manifest file..' + Fore.RESET)

            mytree.write(file=manifest_path,default_namespace='android')

        self._apk_dir = os.path.join(self.config["path"], self.config["apk"])
        if not os.path.isdir(self._apk_dir): 
            self._decompile_apk(os.path.join(self.config["path"], self.config["apk"]))

        if network_file_exists():
            modify()
        else:
            create()
        print(Fore.GREEN + '[*] Generating apk..' + Fore.RESET)
        self.generate_apk()
        print(Fore.GREEN + '[*] Signing apk..' + Fore.RESET)
        self.sign_apk()
        print(Fore.GREEN + '[*] Installing apk..' + Fore.RESET)
        self.install_apk()