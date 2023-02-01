import readline
import shlex
from Classes.constants import Constants
from Classes.utils import back, listmodules, unknown_cmd

class HandleAPK:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Generate, sign, pull and install an APK"
        self._name = "handleapk"
    
    def execute(self, mmsf):
        def handle_pull_apk(mmsf):
            set_data = ["app", "path", "apk"]
            data_scan = {
                "dir_name": "base",
                "app": "",
                "path": Constants.DIR_PULLED_APKS.value,
                "mode": "d",
                "apk": "base",
                "out_apk": Constants.PATCHED_APK.value,
                "in_apk": Constants.GENERATED_APK.value,
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
                    return mmsf.getapk(cmd, data)
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (handleapk/pull)> '))
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
                        inpt = shlex.split(input('mmsf (handleapk/pull/set)> '))
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
                            elif cmd.lower() == "apk":
                                data_scan["apk"] = args[0]
                        else:                            
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break 

        def handle_generate_apk(mmsf):
            set_data = ["dir_name", "path", "apk"]
            data_scan = {
                "dir_name": "base",
                "app": "",
                "path": Constants.DIR_PULLED_APKS.value,
                "mode": "d",
                "apk": "base",
                "out_apk": Constants.PATCHED_APK.value,
                "in_apk": Constants.GENERATED_APK.value,
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
                    return mmsf.generate_apk(cmd, data)
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (handleapk/generate)> '))
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
                        inpt = shlex.split(input('mmsf (handleapk/generate/set)> '))
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

        def handle_sign_apk(mmsf):
            set_data = ["in_apk", "path", "out_apk"]
            data_scan = {
                "dir_name": "base",
                "app": "",
                "path": Constants.DIR_PULLED_APKS.value,
                "mode": "d",
                "apk": "base",
                "out_apk": Constants.PATCHED_APK.value,
                "in_apk": Constants.GENERATED_APK.value,
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
                    return mmsf.sign_apk(cmd, data)
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (handleapk/sign)> '))
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
                        inpt = shlex.split(input('mmsf (handleapk/sign/set)> '))
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
                            elif cmd.lower() == "in_apk":
                                data_scan["in_apk"] = args[0]
                            elif cmd.lower() == "out_apk":
                                data_scan["out_apk"] = args[0]
                        else:
                            print(cmd.lower())
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break 

        def handle_install_apk(mmsf):
            set_data = ["dir_name", "path", "apk"]
            data_scan = {
                "dir_name": "base",
                "app": "",
                "path": Constants.DIR_PULLED_APKS.value,
                "mode": "d",
                "apk": "base",
                "out_apk": Constants.PATCHED_APK.value,
                "in_apk": Constants.GENERATED_APK.value,
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
                    mmsf.install_apk(cmd, data)
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (handleapk/install)> '))
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
                        inpt = shlex.split(input('mmsf (handleapk/sign/set)> '))
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
                            elif cmd.lower() == "apk":
                                data_scan["apk"] = args[0]
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break 

        modules = ["pull", "sign", "generate", "install"]
        descriptions = [
            "Pull apk from device", 
            "Sign custom apk",
            "Generate custom apk",
            "Install apk to device"]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (handleapk)> '))
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
                    handle_pull_apk(mmsf)
                elif action == "generate":
                    handle_generate_apk(mmsf)
                elif action == "sign":
                    handle_sign_apk(mmsf)
                else:
                    handle_install_apk(mmsf)
            elif input_val[0].lower() == "back":
                back()
                break