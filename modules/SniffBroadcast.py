import readline
import shlex
from Classes.constants import Constants


class SniffBroadcast:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Sniffing a broadcast intent"
        self._name = "sniff"
    
    def execute(self, mmsf):
        while True:
            set_data = ["data_authority", "data_path", "data_scheme", "data_type", "action", "category"]
            sniffdata = {
                "authority": "",
                "scheme": "",
                "path": "",
                "type": "",
                "intent_action": "",
                "category": ""

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
                return mmsf.sniff_broadcast_data(cmd, data)

            readline.set_completer(cmd_completer)
            data = shlex.split(input('mmsf (sniff)> '))
            if len(data) > 0:
                value = data[0].lower()
            else:
                continue
            if value == "set":
                while True:

                    readline.set_completer(data_completer)
                    cmds = shlex.split(input('mmsf (sniff/set)> '))
                    if len(cmds) >= 2:
                        cmd, *args = cmds
                    elif len(cmds) < 1:
                        continue
                    else:
                        cmd = cmds[0]
                        args = None
                    if cmd.lower() == "action" and args:
                        sniffdata["intent_action"] = args[0]
                    elif cmd.lower() == "category" and args:
                        sniffdata["category"] = args[0]
                    elif cmd.lower() == "data_authority" and args:
                        sniffdata["authority"] = f'{args[0]} {args[1]}'
                    elif cmd.lower() == "data_path" and args:
                        sniffdata["path"] = args[0]
                    elif cmd.lower() == "data_scheme" and args:
                        sniffdata["scheme"] = args[0]
                    elif cmd.lower() == "data_type" and args:
                        sniffdata["type"] = args[0]
                    else:
                        if execute(cmd.lower(), sniffdata):
                            break
            else:
                if execute(value, sniffdata) == 2:
                    break