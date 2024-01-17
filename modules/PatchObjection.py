import readline
import shlex

from colorama import Fore
from Classes.constants import Constants
from Classes.utils import back, listmodules, print_help, unknown_cmd

class PatchObjection:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Patch IPA or APK"
        self._name = "patchobjection"
    
    def execute(self, mmsf):
        def handle_patch_apk(mmsf):
            set_data = ["apk", "abi", "network"]
            data_scan = {
                "app": "",
                "apk": "~/.mmsf/loot/apks/base.apk",
                "network": False,
                "abi": "autodetect"
            }
            # waiting for input 
            while True:

                # set the autocompleters
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

                # The commands to be executed
                def execute(cmd, data):
                    status = 0
                    try:
                        status = mmsf.patch_apk(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ e + Fore.RESET)
                    finally:
                        return status
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (patchobjection/apk)> '))
                if len(input_val) >= 1:
                    command = input_val[0].lower()
                elif len(input_val) < 1:
                    continue
                else:
                    unknown_cmd()
                if command == "back":
                    back()
                    break
                elif command == "set":
                    # wait for data to be set
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (patchobjection/apk/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "apk":
                                data_scan["apk"] = args[0]
                            elif cmd.lower() == "abi":
                                data_scan["abi"] = args[0]
                            elif cmd.lower() == "network":
                                data_scan["network"] = args[0]
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break
        
        def handle_patch_ipa(mmsf):
            set_data = ["apk", "abi", "network"]
            data_scan = {
                "app": "",
                "apk": "~/.mmsf/loot/apks/base.apk",
                "network": False,
                "abi": "autodetect"
            }
            # waiting for input 
            while True:

                # set the autocompleters
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

                # The commands to be executed
                def execute(cmd, data):
                    status = 0
                    try:
                        status = mmsf.patch_ipa(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ e + Fore.RESET)
                    finally:
                        return status
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (patchobjection/ipa)> '))
                if len(input_val) >= 1:
                    command = input_val[0].lower()
                elif len(input_val) < 1:
                    continue
                else:
                    unknown_cmd()
                if command == "back":
                    back()
                    break
                elif command == "set":
                    # wait for data to be set
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (patchobjection/ipa/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "apk":
                                data_scan["apk"] = args[0]
                            elif cmd.lower() == "abi":
                                data_scan["abi"] = args[0]
                            elif cmd.lower() == "network":
                                data_scan["network"] = args[0]
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break

        modules = ["apk", "ipa"]
        descriptions = [
            "Push frida gadget on APK", 
            "Push Frida Gadget on IPA"]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (patchobjection)> '))
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
                elif action == "apk":
                    handle_patch_apk(mmsf)
                elif action == "ipa":
                    handle_patch_ipa(mmsf)

            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() == "help" or input_val[0] == "?":
                print_help()