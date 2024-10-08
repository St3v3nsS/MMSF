import readline
import shlex

from colorama import Fore
from Classes.constants import Constants
from Classes.utils import back, listmodules, print_help, unknown_cmd

class SplitApk:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Generate, sign, pull and install SplitApks"
        self._name = "splitapk"
    
    def execute(self, mmsf):
        def handle_pull_apks(mmsf):
            set_data = ["app", "path", "apks", "patched_apks"]
            data_scan = {
                "apks": [],
                "path": Constants.DIR_PULLED_APKS.value,
                "patched_apks": [],
                "app": ""
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
                        status = mmsf.getapks(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                    return status
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (splitapk/pull)> '))
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
                        inpt = shlex.split(input('mmsf (splitapk/pull/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "path":
                                data_scan["path"] = args[0]
                            elif cmd.lower() == "app":
                                data_scan["app"] = args[0]
                            elif cmd.lower() == "apks":
                                data_scan["apks"] = args[0]
                        else:                            
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break 

        def handle_generate_apks(mmsf):
            set_data = ["app", "path", "apks", "patched_apks"]
            data_scan = {
                "apks": [],
                "path": Constants.DIR_PULLED_APKS.value,
                "patched_apks": [],
                "app": ""
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
                        status = mmsf.generate_apks(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                    return status
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (splitapk/generate)> '))
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
                        inpt = shlex.split(input('mmsf (splitapk/generate/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "path":
                                data_scan["path"] = args[0]
                            elif cmd.lower() == "dir_name":
                                data_scan["dir_name"] = args[0]
                            elif cmd.lower() == "apk":
                                data_scan["apk"] = args[0]
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break

        def handle_sign_apks(mmsf):
            set_data = ["app", "path", "apks", "patched_apks"]
            data_scan = {
                "apks": [],
                "path": Constants.DIR_PULLED_APKS.value,
                "patched_apks": [],
                "app": ""
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
                        status = mmsf.sign_apks(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                    return status
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (splitapk/sign)> '))
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
                        inpt = shlex.split(input('mmsf (splitapk/sign/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "path":
                                data_scan["path"] = args[0]
                            elif cmd.lower() == "apks":
                                data_scan["apks"] = args[0]
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break 
        

        def handle_decompile_apks(mmsf):
            set_data = ["app", "path", "outname", "apks"]
            data_scan = {
                "apks": [],
                "path": Constants.DIR_PULLED_APKS.value,
                "outname": "",
                "app": ""
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
                        status = mmsf.decompile_apks(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                    return status
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (splitapk/decompile)> '))
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
                        inpt = shlex.split(input('mmsf (splitapk/decompile/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "path":
                                data_scan["path"] = args[0]
                            elif cmd.lower() == "apks":
                                data_scan["apks"] = args[0]
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break 

        def handle_install_apks(mmsf):
            set_data = ["app", "path", "apks", "patched_apks"]
            data_scan = {
                "apks": [],
                "path": Constants.DIR_PULLED_APKS.value,
                "patched_apks": [],
                "app": ""
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
                        status = mmsf.install_apks(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                    return status
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (splitapk/install)> '))
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
                        inpt = shlex.split(input('mmsf (splitapk/install/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "path":
                                data_scan["path"] = args[0]
                            elif cmd.lower() == "apks":
                                data_scan["apks"] = args[0]
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break 

        modules = ["pull", "sign", "generate", "install", "decompile"]
        descriptions = [
            "Pull SplitApks from device", 
            "Sign custom SplitApks",
            "Generate custom SplitApks",
            "Install SplitApks to device", 
            "Decompile SplitApks"]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (splitapk)> '))
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
                elif action == "pull":
                    handle_pull_apks(mmsf)
                elif action == "generate":
                    handle_generate_apks(mmsf)
                elif action == "sign":
                    handle_sign_apks(mmsf)
                elif action == "decompile":
                    handle_decompile_apks(mmsf)
                else:
                    handle_install_apks(mmsf)
            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() == "help" or input_val[0] == "?":
                print_help()