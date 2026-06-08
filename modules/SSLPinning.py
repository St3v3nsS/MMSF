import os
import readline
import shlex
from Classes.constants import Constants
from Classes.utils import back, listmodules, print_help, print_show_table, unknown_cmd, quit_app
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
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
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
                                print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                            return status
                        else:
                            print(Fore.RED + "[-] Set the required values first!" + Fore.RESET)
                            return 0              
                    elif cmd == "show":
                        print_show_table([
                            {"name": "APP", "value": mmsf._objection.config["app"], "description": "The application package name: com.example.android"}])
                        return 0
                    elif cmd == "exit":
                        quit_app()
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
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
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
                                print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
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
                        quit_app()
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

        def handle_frida_v2():
            frida_v2_data = {
                "mode":       "-U",
                "app":        "",
                "host":       "127.0.0.1",
                "method":     "-f",
                "proxy_host": "127.0.0.1",
                "proxy_port": "8080",
                "cert_pem":   "",
            }

            set_data = ["app", "mode", "host", "method", "proxy_host", "proxy_port", "cert_pem"]

            def data_completer(text, state):
                options = [i for i in set_data if i.startswith(text)]
                return options[state] if state < len(options) else None

            def cmd_completer(text, state):
                options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                return options[state] if state < len(options) else None

            def _resolve_cert(raw):
                raw = raw.strip()
                if os.path.isfile(raw):
                    with open(raw, 'r') as f:
                        return f.read().strip()
                return raw

            def _run(data):
                if not data["app"]:
                    print(Fore.RED + '[-] APP is required.' + Fore.RESET)
                    return 0
                if not data["cert_pem"]:
                    print(Fore.RED + '[-] CERT_PEM is required (PEM string or path to .pem file).' + Fore.RESET)
                    return 0
                cert = _resolve_cert(data["cert_pem"])
                mmsf._frida.config = {
                    "mode":   data["mode"],
                    "app":    data["app"],
                    "host":   data["host"],
                    "method": data["method"],
                    "pause":  "",
                }
                try:
                    return mmsf.bypass_ssl_frida_v2(data["proxy_host"], data["proxy_port"], cert)
                except Exception as e:
                    print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return 0

            def _show(data):
                print_show_table([
                    {"name": "APP",        "value": data["app"],
                     "description": "Target package name: com.example.android"},
                    {"name": "PROXY_HOST", "value": data["proxy_host"],
                     "description": "Intercepting proxy IP. Default: 127.0.0.1", "required": False},
                    {"name": "PROXY_PORT", "value": data["proxy_port"],
                     "description": "Intercepting proxy port. Default: 8080",    "required": False},
                    {"name": "CERT_PEM",   "value": "(set)" if data["cert_pem"] else "(not set)",
                     "description": "CA certificate PEM string or path to .pem/.crt file"},
                    {"name": "MODE",       "value": "SERIAL" if data["mode"] == "-U" else "REMOTE",
                     "description": "Serial or Remote. Default: SERIAL",          "required": False},
                    {"name": "METHOD",     "value": "SPAWN" if data["method"] == "-f" else "FRONTMOST",
                     "description": "Attach method. Default: SPAWN",              "required": False},
                    {"name": "HOST",       "value": data["host"],
                     "description": "Frida remote host (MODE=REMOTE only)",       "required": False},
                ])
                return 0

            while True:
                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (sslpinning/frida_v2)> '))
                if not value:
                    continue
                cmd = value[0].lower()

                if cmd == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (sslpinning/frida_v2/set)> '))
                        if len(inpt) > 1:
                            k, *args = inpt
                        elif len(inpt) == 1:
                            k, args = inpt[0], None
                        else:
                            continue
                        kl = k.lower()
                        if kl == "app" and args:
                            frida_v2_data["app"] = args[0]
                        elif kl == "proxy_host" and args:
                            frida_v2_data["proxy_host"] = args[0]
                        elif kl == "proxy_port" and args:
                            frida_v2_data["proxy_port"] = args[0]
                        elif kl == "cert_pem" and args:
                            frida_v2_data["cert_pem"] = " ".join(args)
                        elif kl == "mode" and args:
                            frida_v2_data["mode"] = "-U" if args[0].upper() in ("SERIAL", "USB") else "-R"
                        elif kl == "method" and args:
                            frida_v2_data["method"] = "-f" if args[0].upper() == "SPAWN" else "-F"
                        elif kl == "host" and args:
                            frida_v2_data["host"] = args[0]
                        elif kl == "run":
                            _run(frida_v2_data)
                            break
                        else:
                            break
                elif cmd == "show":
                    _show(frida_v2_data)
                elif cmd == "run":
                    if _run(frida_v2_data) == 2:
                        return 1
                elif cmd == "exit":
                    quit_app()
                elif cmd == "back":
                    back()
                    return 1

        def handle_burp_ca():
            pass

        modules = ["objection", "frida", "frida_v2", "flutter", "burp_ca", "network_config"]
        descriptions = [
            "Bypass the SSL Pinning using Objection",
            "Frida Script to bypass the SSL Pinning",
            "Frida v2 — httptoolkit multi-script SSL bypass (proxy + cert injection + unpinning)",
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
                quit_app()
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
                elif action == "frida_v2":
                    handle_frida_v2()
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