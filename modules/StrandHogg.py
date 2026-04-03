import readline
import shlex

from colorama import Fore
from Classes.constants import Constants
from Classes.utils import listmodules, print_help, unknown_cmd, back


class StrandHogg:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "StrandHogg 2.0 (CVE-2020-0096) — Runtime task injection via startActivities() to overlay phishing UI on any app"
        self._name = "strandhogg"

    def execute(self, mmsf):

        # ── check ─────────────────────────────────────────────────────────────
        def handle_check():
            data = {}

            while True:
                def cmd_completer(text, state):
                    options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    return None

                def execute(cmd, data):
                    status = 0
                    try:
                        status = mmsf.strandhogg_check(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (strandhogg/check)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()

                # check has no set params — run immediately
                if execute(value, data) == 2:
                    return 1

        # ── generate ──────────────────────────────────────────────────────────
        def handle_generate():
            multi_target = []
            data = {
                "target_package": "",
                "attacker_package": "com.evil.strandhogg2",
                "c2_url": "http://YOUR_C2/loot",
                "phishing_text": "Your session has expired. Please verify your identity.",
                "loot_path": Constants.DIR_LOOT_PATH.value,
                "multi_target": multi_target
            }

            while True:
                set_data = ["target_package", "add_target", "attacker_package",
                            "c2_url", "phishing_text", "loot_path"]

                def data_completer(text, state):
                    options = [i for i in set_data if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    return None

                def cmd_completer(text, state):
                    options = [i for i in Constants.MMSF_COMMANDS.value if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    return None

                def execute(cmd, data):
                    status = 0
                    try:
                        status = mmsf.strandhogg_generate(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (strandhogg/generate)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()

                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (strandhogg/generate/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "target_package" and args:
                            data["target_package"] = args[0]
                        elif cmd.lower() == "add_target" and args:
                            data["multi_target"].append(args[0])
                            print(Fore.GREEN + f"[+] Added target: {args[0]}" + Fore.RESET)
                        elif cmd.lower() == "attacker_package" and args:
                            data["attacker_package"] = args[0]
                        elif cmd.lower() == "c2_url" and args:
                            data["c2_url"] = args[0]
                        elif cmd.lower() == "phishing_text" and args:
                            data["phishing_text"] = " ".join(args)
                        elif cmd.lower() == "loot_path" and args:
                            data["loot_path"] = args[0]
                        else:
                            if execute(cmd.lower(), data):
                                break
                else:
                    if execute(value, data) == 2:
                        return 1

        # ── top-level menu ────────────────────────────────────────────────────
        modules = ["check", "generate"]
        descriptions = [
            "Check device vulnerability to StrandHogg 2.0 (CVE-2020-0096) via ADB",
            "Generate StrandHogg 2.0 runtime payload — no manifest config, attacks multiple apps"
        ]

        while True:
            def init_completer(text, state):
                options = [i for i in modules if i.startswith(text)]
                if state < len(options):
                    return options[state]
                return None

            readline.set_completer(init_completer)
            input_val = shlex.split(input('mmsf (strandhogg)> '))
            if len(input_val) < 1:
                continue
            if len(input_val) > 2:
                continue
            elif input_val[0].lower() == "exit":
                quit()
            elif input_val[0].lower() in ("listmodules", "show"):
                listmodules(modules, descriptions)
            elif input_val[0].lower() == "usemodule":
                if len(input_val) < 2:
                    unknown_cmd()
                    continue
                action = input_val[1].lower()
                if action not in modules:
                    unknown_cmd()
                elif action == "check":
                    handle_check()
                elif action == "generate":
                    handle_generate()
            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() in ("help", "?"):
                print_help()