import readline
import shlex

from colorama import Fore
from Classes.constants import Constants
from Classes.utils import back, listmodules, print_help, unknown_cmd

class WorkProfile:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Handle the Work Profile applications"
        self._name = "workprofile"
    
    def execute(self, mmsf):
        def pull_apk_by_install_to_normal(mmsf):
            set_data = ["app", "path", "apk"]
            data_scan = {
                "apk": "base.apk",
                "path": Constants.DIR_PULLED_APKS.value,
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
                        status = mmsf.workprofile_getapk(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                    return status
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (workprofile/pull_apk_user_0)> '))
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
                        inpt = shlex.split(input('mmsf (workprofile/pull_apk_user_0/set)> '))
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

        modules = ["pull_apk"]
        descriptions = [
            "Pull an apk from the Work Profile by installing the application to user 0"]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (workprofile)> '))
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
                elif action == "pull_apk":
                    pull_apk_by_install_to_normal(mmsf)

            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() == "help" or input_val[0] == "?":
                print_help()