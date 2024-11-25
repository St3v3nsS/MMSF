import readline
import shlex

from colorama import Fore
from Classes.constants import Constants
from Classes.utils import listmodules, print_help
from Classes.utils import unknown_cmd
from Classes.utils import back

class DeepLink:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Launch a deeplink with supplied value or generate malicious files to steal sensitive data"
        self._name = "deeplink"
        self._data = {
            "server": "http://127.0.0.1:8000/",
            "filename": "steal.html",
            "scheme": "",
            "package": "",
            "component": "",
            "deeplink_uri": "",
            "param": "",
            "js_interface": "",
            "path": Constants.DIR_LOOT_PATH.value,
            "poc_filename": "launch.html"
        }
    
    def execute(self, mmsf):
        def launch_deeplink():
            deeplink = ""
            while True:
                set_data = ["data_uri"]
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
                        status = mmsf.open_deeplink(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)

                values = shlex.split(input('mmsf (deeplink/launch)> '))
                if len(values) >= 1:
                    value = values[0].lower()
                else:
                    continue
                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        cmds = shlex.split(input('mmsf (deeplink/launch/set)> '))
                        if len(cmds) == 2:
                            cmd, *args = cmds
                        elif len(cmds) < 1:
                            continue
                        else:
                            cmd = cmds[0]
                            args = None
                        if cmd.lower() == "data_uri" and args:
                            deeplink = args[0].lower()
                        else:
                            if execute(cmd.lower(), deeplink):
                                break
                else:
                    if execute(value, deeplink) == 2:
                        break
        
        def generate_jsinterface():
            data = {
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
            while True:
                set_data = self._data.keys()
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
                        status = mmsf.generate_jsinterface(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)

                values = shlex.split(input('mmsf (deeplink/jsinterface)> '))
                if len(values) >= 1:
                    value = values[0].lower()
                else:
                    continue
                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        cmds = shlex.split(input('mmsf (deeplink/jsinterface/set)> '))
                        if len(cmds) == 2:
                            cmd, *args = cmds
                        elif len(cmds) < 1:
                            continue
                        else:
                            cmd = cmds[0]
                            args = None
                        if cmd.lower() == "server" and args:
                            data["server"] = args[0].lower()
                        elif cmd.lower() == "filename" and args:
                            data["filename"] = args[0].lower()
                        elif cmd.lower() == "scheme" and args:
                            data["scheme"] = args[0]
                        elif cmd.lower() == "package" and args:
                            data["package"] = args[0]
                        elif cmd.lower() == "component" and args:
                            data["component"] = args[0]
                        elif cmd.lower() == "deeplink_uri" and args:
                            data["deeplink_uri"] = args[0]
                        elif cmd.lower() == "param" and args:
                            data["param"] = args[0]
                        elif cmd.lower() == "js_interface" and args:
                            data["js_interface"] = args[0]
                        elif cmd.lower() == "path" and args:
                            data["path"] = args[0].lower()
                        elif cmd.lower() == "poc_filename" and args:
                            data["poc_filename"] = args[0]
                        else:
                            if execute(cmd.lower(), data):
                                break
                else:
                    if execute(value, data) == 2:
                        break
                    
        def generate_deeplink():
            data = {
                "scheme": "deeplink",
                "package": "com.example.com",
                "component": "com.example.com.WebViewActivity",
                "deeplink_uri": "host.com",
                "extras": [],
                "path": Constants.DIR_LOOT_PATH.value
            }
            while True:
                set_data = self._data.keys()
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
                        status = mmsf.generate_deeplink(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)

                values = shlex.split(input('mmsf (deeplink/generate)> '))
                if len(values) >= 1:
                    value = values[0].lower()
                else:
                    continue
                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        cmds = shlex.split(input('mmsf (deeplink/generate/set)> '))
                        if len(cmds) == 4:
                            cmd, *args = cmds
                        elif len(cmds) == 2:
                            cmd, *args = cmds
                        elif len(cmds) < 1:
                            continue
                        else:
                            cmd = cmds[0]
                            args = None
                        if cmd.lower() == "scheme" and args:
                            data["scheme"] = args[0]
                        elif cmd.lower() == "package" and args:
                            data["package"] = args[0]
                        elif cmd.lower() == "component" and args:
                            data["component"] = args[0]
                        elif cmd.lower() == "deeplink_uri" and args:
                            data["deeplink_uri"] = args[0]
                        elif cmd.lower() == "path" and args:
                            data["path"] = args[0].lower()
                        elif cmd.lower() == "extras" and args:
                            data["extras"].append({"type": args[0].upper()[0], "key": args[1], "value": args[2]})
                        elif cmd.lower() == "remove" and args:
                            data["extras"] = [i for i in data["extras"] if i["key"] != args[0]]
                        else:
                            if execute(cmd.lower(), data):
                                break
                else:
                    if execute(value, data) == 2:
                        break
                                
        modules = ["launch", "jsinterface", "generate"]
        descriptions = [
            "Launch a deeplink",
            "Generate a deeplink PoC for exported JS interface",
            "Generate a simple deeplink PoC"]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (deeplink)> '))
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
                elif action == "launch":
                    launch_deeplink()
                elif action == "jsinterface":
                    generate_jsinterface()
                elif action == "generate":
                    generate_deeplink()
            elif input_val[0].lower() == "back":
                back()
                break 
            elif input_val[0].lower() == "help" or input_val[0] == "?":
                print_help()           