import readline
import shlex
from Classes.constants import Constants
from Classes.utils import back, listmodules, print_help, print_show_table, unknown_cmd, quit
from colorama import Fore

class SSLPinning:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Bypass the SSL Pinning mechanism through different methods"
        self._name = "sslpinning"
    
    def execute(self, mmsf):
        def handle_frida():
            frida_data = {
                "mode": "-U",
                "app": "",
                "host": "127.0.0.1",
                "pause": "",
                "method": "-f"
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
                    status = 0
                    try:
                        status = mmsf.bypass_ssl_frida(cmd,data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ e + Fore.RESET)
                    finally:
                        return status

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (sslpinning/frida)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (sslpinning/frida/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        else:
                            if len(inpt) < 1:
                                continue
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
                        elif cmd.lower() == "method" and args:
                            if args[0].lower() == "frontmost":
                                frida_data["method"] = "-F"
                            else:
                                frida_data["method"] = '-f'
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
                        if mmsf._objection.config["app"]:
                            status = 0
                            try:
                                status = mmsf.bypass_ssl_objection()
                            except Exception as e:
                                print(Fore.RED + '[-] '+ e + Fore.RESET)
                            finally:
                                return status
                        else:
                            print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                            return 0              
                    elif cmd == "show":
                        print_show_table([
                            {"name": "APP", "value": mmsf._objection.config["app"], "description": "The application package name: com.example.android"}])
                        return 0
                    elif cmd == "exit":
                        quit()
                    elif cmd == "back":
                        back()
                        return 2

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (sslpinning/objection)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (sslpinning/objection/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "app" and args:
                            objection_data["app"] = args[0]
                        else:
                            mmsf._objection.config = objection_data
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
                    status = 0
                    try:
                        status = mmsf.bypass_network_config(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ e + Fore.RESET)
                    finally:
                        return status

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (sslpinning/network_config)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (sslpinning/network_config/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
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
                            status = 0
                            try:
                                status = mmsf.reflutter_sslpinning()
                            except Exception as e:
                                print(Fore.RED + '[-] '+ e + Fore.RESET)
                            finally:
                                return status
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
                
                value = shlex.split(input('mmsf (sslpinning/flutter)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (sslpinning/flutter/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
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
                unknown_cmd()
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
            elif input_val[0].lower() == "help" or input_val[0] == "?":
                print_help()