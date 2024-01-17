import readline
import shlex
from Classes.constants import Constants
from colorama import Fore


class Intent:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Start an intent using supplied values like: extra values, action, mimetype or data"
        self._name = "intent"
    
    def execute(self, mmsf):
        while True:
            set_data = ["data_uri", "extra", "component", "action", "mimetype", "app_name"] + mmsf.all_apps
            actions = ["android.intent.action.VIEW", "android.intent.action.MAIN", "android.intent.action.SEND", "android.intent.action.SENDTO", "android.intent.action.SEARCH"]
            extras_type = ["parcelable", "long", "byte", "double", "charsequence", "boolean", "int", "Bundle", "string", "char", "serializable", "short"]
            activity_data = {
                "component": "",
                "extras": [],
                "deeplink": "",
                "intent_action": "",
                "mimetype": "",
                "app_name": ""
            }
            def extras_type_completer(text, state):
                options = [i for i in extras_type if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

            def data_completer(text, state):
                options = [i for i in set_data + actions if i.startswith(text)]
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
                    status = mmsf.start_activity(cmd, data)
                except Exception as e:
                    print(Fore.RED + '[-] '+ e + Fore.RESET)
                finally:
                    return status

            readline.set_completer(cmd_completer)
            extra = []
            value = shlex.split(input('mmsf (intent)> '))
            if len(value) < 1:
                continue
            else:
                value = value[0].lower()
            if value == "set":
                while True:
                    readline.set_completer(data_completer)
                    cmds = shlex.split(input('mmsf (intent/set)> '))
                    if len(cmds) >= 2:
                        cmd, *args = cmds
                    elif len(cmds) < 1:
                        continue
                    else:
                        cmd = cmds[0]
                        args = None
                    if cmd.lower() == "extra":
                        
                        while True:
                            readline.set_completer(extras_type_completer)
                            cmdds = shlex.split(input('mmsf (intent/set/extra)> '))
                            if len(cmdds) < 2:
                                if len(cmdds) == 1:
                                    if execute(cmdds[0].lower(), activity_data):
                                        break
                                else:
                                    print(Fore.RED + "[-] The expected arguments should be in form of TYPE KEY VALUE" + Fore.RESET)
                            elif len(cmdds) == 2:
                                if cmdds[0] == "remove":
                                    extras = [i for i in extra if cmdds[1] not in i]
                                    extra = extras
                                    break
                            else:
                                extra += [f"{cmdds[0]} {cmdds[1]} {cmdds[2]}"]
                                break
                        activity_data["extras"] = extra
                    elif cmd.lower() == "action" and args:
                        activity_data["intent_action"] = args[0]
                    elif cmd.lower() == "component" and args:
                        activity_data["component"] = args[0]
                    elif cmd.lower() == "app_name" and args:
                        activity_data["app_name"] = args[0]
                    elif cmd.lower() == "mimetype" and args:
                        activity_data["mimetype"] = args[0]
                    elif cmd.lower() == "data_uri" and args:
                        activity_data["deeplink"] = args[0]
                    else:
                        if execute(cmd.lower(), activity_data):
                            break
            else:
                if execute(value, activity_data) == 2:
                    break     