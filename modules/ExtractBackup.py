import os
import readline
import shlex
from Classes.constants import Constants
from Classes.utils import back, listmodules, print_help, unknown_cmd

class ExtractBackup:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Extract or restore backup from Android Application"
        self._name = "backup"
    
    def execute(self, mmsf):
        def handle_extract(mmsf):
            set_data = ["app", "password", "path"]
            data_scan = {
                "app": "",
                "path": Constants.DIR_LOOT_DATA.value,
                "password": ""
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
                    return mmsf.extract_backup(cmd, data)
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (backup/extract)> '))
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
                        inpt = shlex.split(input('mmsf (backup/extract/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "app":
                                data_scan["app"] = args[0]
                            elif cmd.lower() == "path":
                                data_scan["path"] = args[0]
                            elif cmd.lower() == "password":
                                data_scan["password"] = args[0]
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break
        
        def handle_restore(mmsf):
            set_data = ["app", "password", "path"]
            data_scan = {
                "app": "",
                "path": Constants.DIR_LOOT_DATA.value,
                "password": ""
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
                    return mmsf.restore_backup(cmd, data)
                    
                readline.set_completer(cmd_completer)

                # get user input
                input_val = shlex.split(input('mmsf (backup/restore)> '))
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
                        inpt = shlex.split(input('mmsf (backup/restore/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "app":
                                data_scan["app"] = args[0]
                            elif cmd.lower() == "path":
                                data_scan["path"] = args[0]
                            elif cmd.lower() == "password":
                                data_scan["password"] = args[0]
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break

        modules = ["extract", "restore"]
        descriptions = [
            "Extract backup from APK", 
            "Restore backup to APK"]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (backup)> '))
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
                elif action == "extract":
                    handle_extract(mmsf)
                elif action == "restore":
                    handle_restore(mmsf)

            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() == "help" or input_val[0] == "?":
                print_help()