import readline
import shlex
from Classes.constants import Constants
from colorama import Fore

from Classes.utils import back, quit_app


class Nuclei:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Run a nuclei scan against a directory or an APK."
        self._name = "nuclei"
    
    def execute(self, mmsf):
        data_scan = {
            "dir_name": "",
            "out_file": "",
            "app_name": "",
            "out_dir": ""
        }
        while True:
            set_data = ["out_file", "dir_name", "app_name", "out_dir"] + mmsf.all_apps

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
                    status = mmsf.run_nuclei_scan(cmd, data)
                except Exception as e:
                    print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                return status

            readline.set_completer(cmd_completer)
            try:
                input_val = shlex.split(input('mmsf (nuclei)> '))

                if len(input_val) >= 1:
                    command = input_val[0].lower()
                elif len(input_val) < 1:
                    continue
                if command == "back":
                    back()
                    break
                elif command == "set":
                    # wait for data to be set
                    while True:
                        readline.set_completer(data_completer)
                        try:
                            inpt = shlex.split(input('mmsf (nuclei/set)> '))
                            if len(inpt) > 1:
                                cmd, *args = inpt
                            elif len(inpt) < 1:
                                continue
                            else:
                                cmd = inpt[0]
                                args = None
                            if cmd == "exit":
                                quit_app()
                            if args:
                                if cmd.lower() == "dir_name":
                                    data_scan["dir_name"] = args[0]
                                elif cmd.lower() == "out_file":
                                    data_scan["out_file"] = args[0]
                                elif cmd.lower() == "app_name":
                                    data_scan["app_name"] = args[0]
                                elif cmd.lower() == "out_dir":
                                    data_scan["out_dir"] = args[0]
                            else:                            
                                if execute(cmd.lower(), data_scan):
                                    break
                        except Exception as e:
                            quit()
                else:
                    if execute(command, data_scan) == 2:
                        return 1 
            except:
                quit()