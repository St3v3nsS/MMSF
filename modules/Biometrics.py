import readline
import shlex

from colorama import Fore

from Classes.constants import Constants
from Classes.utils import listmodules, print_help, unknown_cmd, back



class Biometrics:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Bypass Biometrics authentication on both iOS/Android"
        self._name = "biometrics"
    
    def execute(self, mmsf):
        def handle_frida_ios():
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
                        status = mmsf.bypass_ios_biometrics_frida(cmd,data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ e + Fore.RESET)
                    finally:
                        return status

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (biometrics/frida/ios)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (biometrics/frida/ios/set)> '))
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

        def handle_frida_android():
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
                        status = mmsf.bypass_android_biometrics_frida(cmd,data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ e + Fore.RESET)
                    finally:
                        return status


                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (biometrics/frida/android)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (biometrics/frida/android/set)> '))
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
        
        def handle_objection_ios():
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

                def execute(cmd, data):
                    status = 0
                    try:
                        status = mmsf.bypass_ios_biometrics_objection(cmd,data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ e + Fore.RESET)
                    finally:
                        return status

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (biometrics/objection/ios)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (biometrics/objection/ios/set)> '))
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
                            if execute(cmd.lower(), objection_data):
                                break
                else:
                    if execute(value, objection_data) == 2:
                        return 1 
                   
        def handle_objection():
            while True:
                def init_completer(text, state):
                        options = [i for i in ["ios", "android"] if i.startswith(text)]
                        if state < len(options):
                            return options[state]
                        else:
                            return None

                readline.set_completer(init_completer)

                input_val = shlex.split(input('mmsf (biometrics/objection)> '))
                if len(input_val) < 1:
                    continue
                if len(input_val) > 2:
                    continue
                elif input_val[0].lower() == "exit":
                    quit()
                elif input_val[0].lower() == "listmodules":
                    listmodules(["ios", "android"], descriptions)
                elif input_val[0].lower() == "usemodule":
                    action = input_val[1].lower()
                    if action not in ["ios", "android"]:
                        unknown_cmd()
                    elif action == "ios":
                        handle_objection_ios()
                    elif action == "android":
                        print("Not yet implemented")
                elif input_val[0].lower() == "back":
                    back()
                    break
        
        def handle_frida():
            while True:
                def init_completer(text, state):
                        options = [i for i in ["ios", "android"] if i.startswith(text)]
                        if state < len(options):
                            return options[state]
                        else:
                            return None

                readline.set_completer(init_completer)

                input_val = shlex.split(input('mmsf (biometrics/frida)> '))
                if len(input_val) < 1:
                    continue
                if len(input_val) > 2:
                    continue
                elif input_val[0].lower() == "exit":
                    quit()
                elif input_val[0].lower() == "listmodules":
                    listmodules(["ios", "android"], descriptions)
                elif input_val[0].lower() == "usemodule":
                    action = input_val[1].lower()
                    if action not in ["ios", "android"]:
                        unknown_cmd()
                    elif action == "ios":
                        handle_frida_ios()
                    elif action == "android":
                        handle_frida_android()
                elif input_val[0].lower() == "back":
                    back()
                    break
        
        modules = ["objection", "frida"]
        descriptions = [
            "Bypass the biometrics authentication using Objection", 
            "Frida Script to bypass the biometrics Authentication"
            ]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (biometrics)> '))
            if len(input_val) < 1:
                continue
            if len(input_val) > 2:
                continue
            elif input_val[0].lower() == "exit":
                quit()
            elif input_val[0].lower() == "listmodules" or input_val[0].lower() == "show":
                listmodules(modules, descriptions)
            elif input_val[0].lower() == "usemodule":
                action = input_val[1].lower()
                if action not in modules:
                    unknown_cmd()
                elif action == "objection":
                    handle_objection()
                elif action == "frida":
                    handle_frida()
            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() == "help" or input_val[0] == "?":
                print_help()