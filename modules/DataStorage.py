import readline
import shlex

from colorama import Fore
from Classes.constants import Constants

from Classes.utils import back, listmodules, print_help, unknown_cmd


class DataStorage:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Exploit Different Data Storage Issues"
        self._name = "datastorage"
    
    def execute(self, mmsf):
        def handle_nsuserdefaults():
            modules = ["retrieve", "modify"]
            descriptions = [
                "Get the data stored in NSUserDefaults space",
                "Modify any data stored in the NSUserDefaults space"
            ]

            while True:
                def init_completer(text, state):
                        options = [i for i in modules if i.startswith(text)]
                        if state < len(options):
                            return options[state]
                        else:
                            return None

                readline.set_completer(init_completer)

                input_val = shlex.split(input('mmsf (datastorage/nsuserdefaults)> '))
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
                    elif action == "retrieve":
                        handle_nsuserdefaults_retrieve()
                    elif action == "modify":
                        handle_nsuserdefaults_modify()
                elif input_val[0].lower() == "back":
                    back()
                    break
                elif input_val[0].lower() == "help" or input_val[0] == "?":
                    print_help()

        def handle_nsuserdefaults_retrieve():
            frida_data = {
                "mode": "-U",
                "app": "",
                "host": "127.0.0.1",
                "pause": "",
                "method": '-f'
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
                        status = mmsf.nsuserdefaults_retrieve(cmd,data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ e + Fore.RESET)
                    finally:
                        return status

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (datastorage/nsuserdefaults/retrieve)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (datastorage/nsuserdefaults/retrieve/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
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
                                frida_data["method"] = '-F'
                            else:
                                frida_data["method"] = '-f'
                        else:
                            if execute(cmd.lower(), frida_data):
                                break
                else:
                    if execute(value, frida_data) == 2:
                        return 1 


        def handle_nsuserdefaults_modify():
            frida_data = {
                "mode": "-U",
                "app": "",
                "host": "127.0.0.1",
                "pause": "",
                "method": '-f',
                "key": "",
                "value": ""
            }
            while True:
                set_data = ["mode", "app", "host", "pause", "key", "value"]
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
                        status = mmsf.nsuserdefaults_modify(cmd,data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ e + Fore.RESET)
                    finally:
                        return status

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (datastorage/nsuserdefaults/modify)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (datastorage/nsuserdefaults/modify/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
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
                                frida_data["method"] = '-F'
                            else:
                                frida_data["method"] = '-f'
                        elif cmd.lower() == "key" and args:
                            frida_data["key"] = args[0]
                        elif cmd.lower() == "value" and args:
                            frida_data["value"] = args[0]
                        else:
                            if execute(cmd.lower(), frida_data):
                                break
                else:
                    if execute(value, frida_data) == 2:
                        return 1 

        modules = ["nsuserdefaults"]
        descriptions = [
            "Get and modify the data stored in NSUserDefaults on an iOS device"
            ]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (datastorage)> '))
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
                elif action == "nsuserdefaults":
                    handle_nsuserdefaults()
            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() == "help" or input_val[0] == "?":
                print_help()