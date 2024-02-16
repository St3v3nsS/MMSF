import readline
import shlex

from colorama import Fore
from Classes.constants import Constants
from Classes.utils import back, unknown_cmd


class FindPackage:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Find the package name of an application and/or its details by supplying a filter keyword"
        self._name = "find"
    
    def execute(self, mmsf):
        while True:
            set_data = ["filter"]
            data = {
                "apps": mmsf.all_apps,
                "query": ""
            }
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
                    status = mmsf.find_app(cmd, data)
                except Exception as e:
                    print(Fore.RED + '[-] '+ str(e) + Fore.RESET)
                return status

            readline.set_completer(cmd_completer)

            value = shlex.split(input('mmsf (find)> '))
            if len(value) >= 1:
                command = value[0].lower()
            else:
                unknown_cmd()

            if command == "back":
                back()
                break
            elif command == "set":
                while True:
                    readline.set_completer(data_completer)
                    cmds = shlex.split(input('mmsf (find/set)> '))
                    if len(cmds) >= 2:
                        cmd, *args = cmds
                    elif len(cmds) < 1:
                        continue
                    else:
                        cmd = cmds[0]
                        args = None
                    if cmd.lower() == "filter" and args:
                        data["query"] = args[0].lower()
                    else:
                        if execute(cmd.lower(), data):
                            break
            else:
                if execute(command, data) == 2:
                    break 