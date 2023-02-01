import readline
import shlex
from Classes.constants import Constants


class DeepLink:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Launch a deeplink with supplied value"
        self._name = "deeplink"
    
    def execute(self, mmsf):
        deeplink = ""
        while True:
            set_data = ["data_uri"]
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
                return mmsf.open_deeplink(cmd, data)

            readline.set_completer(cmd_completer)

            values = shlex.split(input('mmsf (deeplink)> '))
            if len(values) >= 1:
                value = values[0].lower()
            else:
                continue
            if value == "set":
                while True:
                    readline.set_completer(data_completer)
                    cmds = shlex.split(input('mmsf (deeplink/set)> '))
                    if len(cmds) == 2:
                        cmd, *args = cmds
                    elif len(cmds) < 1:
                        continue
                    else:
                        cmd = cmds[0]
                        args = None
                    if cmd.lower() == "data_uri" and args:
                        deeplink = args[0].lower()
                    else:
                        if execute(cmd.lower(), deeplink):
                            break
            else:
                if execute(value, deeplink) == 2:
                    break