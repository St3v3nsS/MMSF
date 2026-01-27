import os
import readline
import shlex

from colorama import Fore
from Classes.constants import Constants
from Classes.utils import back, listmodules, print_help, unknown_cmd, print_show_table, quit_app


class NgBackup:
    """Next-Gen Backup Module - adb backup replacement"""
    
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Next-Gen App Data Extraction (replaces adb backup)"
        self._name = "ng-backup"
    
    def execute(self, mmsf):
        """Main module entry point"""
        
        def handle_rooted(mmsf):
            """Rooted extraction submodule"""
            set_data = ["app", "path"]
            data_scan = {
                "app": "",
                "path": Constants.DIR_LOOT_DATA.value
            }
            
            while True:
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
                        status = mmsf.ngbackup_extract(cmd, data, method="rooted")
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status
                
                readline.set_completer(cmd_completer)
                
                input_val = shlex.split(input('mmsf (ng-backup/rooted)> '))
                if len(input_val) >= 1:
                    command = input_val[0].lower()
                elif len(input_val) < 1:
                    continue
                else:
                    unknown_cmd()
                    
                if command == "back":
                    back()
                    break
                elif command == "exit":
                    quit_app()
                elif command == "help" or command == "?":
                    print_help()
                elif command == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (ng-backup/rooted/set)> '))
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
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break
        
        def handle_runas(mmsf):
            """run-as extraction submodule"""
            set_data = ["app", "path"]
            data_scan = {
                "app": "",
                "path": Constants.DIR_LOOT_DATA.value
            }
            
            while True:
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
                        status = mmsf.ngbackup_extract(cmd, data, method="runas")
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status
                
                readline.set_completer(cmd_completer)
                
                input_val = shlex.split(input('mmsf (ng-backup/runas)> '))
                if len(input_val) >= 1:
                    command = input_val[0].lower()
                elif len(input_val) < 1:
                    continue
                else:
                    unknown_cmd()
                    
                if command == "back":
                    back()
                    break
                elif command == "exit":
                    quit_app()
                elif command == "help" or command == "?":
                    print_help()
                elif command == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (ng-backup/runas/set)> '))
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
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break
        
        def handle_patch(mmsf):
            """APK patching extraction submodule"""
            set_data = ["app", "path"]
            data_scan = {
                "app": "",
                "path": Constants.DIR_LOOT_DATA.value
            }
            
            while True:
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
                        status = mmsf.ngbackup_extract(cmd, data, method="patch")
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status
                
                readline.set_completer(cmd_completer)
                
                input_val = shlex.split(input('mmsf (ng-backup/patch)> '))
                if len(input_val) >= 1:
                    command = input_val[0].lower()
                elif len(input_val) < 1:
                    continue
                else:
                    unknown_cmd()
                    
                if command == "back":
                    back()
                    break
                elif command == "exit":
                    quit_app()
                elif command == "help" or command == "?":
                    print_help()
                elif command == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (ng-backup/patch/set)> '))
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
                        else:
                            if execute(cmd.lower(), data_scan):
                                break
                else:
                    if execute(command, data_scan) == 2:
                        break
        
        def handle_legacy(mmsf):
            """Legacy adb backup with UI automation"""
            set_data = ["app", "path", "password"]
            data_scan = {
                "app": "",
                "path": Constants.DIR_LOOT_DATA.value,
                "password": ""
            }
            
            while True:
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
                        status = mmsf.ngbackup_extract(cmd, data, method="legacy")
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status
                
                readline.set_completer(cmd_completer)
                
                input_val = shlex.split(input('mmsf (ng-backup/legacy)> '))
                if len(input_val) >= 1:
                    command = input_val[0].lower()
                elif len(input_val) < 1:
                    continue
                else:
                    unknown_cmd()
                    
                if command == "back":
                    back()
                    break
                elif command == "exit":
                    quit_app()
                elif command == "help" or command == "?":
                    print_help()
                elif command == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (ng-backup/legacy/set)> '))
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

        # Main module menu
        modules = ["rooted", "runas", "patch", "legacy"]
        descriptions = [
            "Extract via root access (su -c tar)", 
            "Extract via run-as (debuggable apps)",
            "Patch APK to enable debuggable flag",
            "Legacy adb backup with UI automation"
        ]

        while True:
            def init_completer(text, state):
                options = [i for i in modules if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (ng-backup)> '))
            if len(input_val) < 1:
                continue
            if len(input_val) > 2:
                continue
            elif input_val[0].lower() == "exit":
                quit_app()
            elif input_val[0].lower() == "listmodules":
                listmodules(modules, descriptions)
            elif input_val[0].lower() == "usemodule":
                if len(input_val) < 2:
                    unknown_cmd()
                    continue
                action = input_val[1].lower()
                if action not in modules:
                    unknown_cmd()
                elif action == "rooted":
                    handle_rooted(mmsf)
                elif action == "runas":
                    handle_runas(mmsf)
                elif action == "patch":
                    handle_patch(mmsf)
                elif action == "legacy":
                    handle_legacy(mmsf)
            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() == "help" or input_val[0] == "?":
                print_help()