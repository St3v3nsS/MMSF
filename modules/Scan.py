import readline
import shlex
from Classes.constants import Constants
from Classes.utils import back, unknown_cmd


class Scan:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Scan the application to retrieve crucial information such as exported activities, path traversal, SQL injections, attack vector and so on"
        self._name = "scan"
    
    def execute(self, mmsf):
        set_data = ["outdir", "app_name"] + mmsf.all_apps
        data_scan = {"app_name": "", "full_path": ""}
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
                return mmsf.run_all(cmd, data)
                
            readline.set_completer(cmd_completer)

            # get user input
            input_val = shlex.split(input('mmsf (scan)> '))
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
                    inpt = shlex.split(input('mmsf (scan/set)> '))
                    if len(inpt) > 1:
                        cmd, *args = inpt
                    elif len(inpt) < 1:
                        continue
                    else:
                        cmd = inpt[0]
                        args = None
                    if args:
                        if cmd.lower() == "outdir":
                            data_scan["full_path"] = args[0]
                        elif cmd.lower() == "app_name":
                            data_scan["app_name"] = args[0]
                    else:
                        if execute(cmd.lower(), data_scan):
                            break
            else:
                if execute(command, data_scan) == 2:
                    break 