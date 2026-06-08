import readline
import shlex
import threading
import xml.etree.ElementTree as ET

from colorama import Fore
from Classes.constants import Constants
from Classes.utils import listmodules, print_help, unknown_cmd, back


class TaskHijacking:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Exploit Android Task Hijacking (StrandHogg 1.0) via taskAffinity + singleTask misconfiguration"
        self._name = "taskhijacking"

    def execute(self, mmsf):

        # ── detect ────────────────────────────────────────────────────────────
        def handle_detect():
            data = {"manifest_path": "", "mode": "detect"}

            while True:
                set_data = ["manifest_path"]

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
                        status = mmsf.taskhijacking(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (taskhijacking/detect)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()

                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (taskhijacking/detect/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "manifest_path" and args:
                            data["manifest_path"] = args[0]
                        else:
                            if execute(cmd.lower(), data):
                                break
                else:
                    if execute(value, data) == 2:
                        return 1

        # ── generate ──────────────────────────────────────────────────────────
        def handle_generate():
            data = {
                "target_package": "",
                "target_activity": "",
                "attacker_package": "com.evil.hijack",
                "phishing_text": "Session expired. Please login again.",
                "loot_path": Constants.DIR_LOOT_PATH.value,
                "mode": "generate",
            }

            while True:
                set_data = ["target_package", "target_activity", "attacker_package",
                            "phishing_text", "loot_path"]

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
                        status = mmsf.taskhijacking(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (taskhijacking/generate)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()

                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (taskhijacking/generate/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "target_package" and args:
                            data["target_package"] = args[0]
                        elif cmd.lower() == "target_activity" and args:
                            data["target_activity"] = args[0]
                        elif cmd.lower() == "attacker_package" and args:
                            data["attacker_package"] = args[0]
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

                # ── frida_hook ────────────────────────────────────────────────────────
        def handle_frida_hook():
            data = {
                "mode":   "-U",
                "app":    "",
                "host":   "127.0.0.1",
                "pause":  "",
                "method": "-f",
                "key":    "",
                "value":  "",
            }

            set_data = ["app", "mode", "host", "method"]

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

            while True:
                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (taskhijacking/frida_hook)> '))
                if not value:
                    continue
                cmd = value[0].lower()

                if cmd == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (taskhijacking/frida_hook/set)> '))
                        if len(inpt) > 1:
                            k, *args = inpt
                        elif len(inpt) == 1:
                            k, args = inpt[0], None
                        else:
                            continue

                        kl = k.lower()
                        if kl == "app" and args:
                            data["app"] = args[0]
                        elif kl == "mode" and args:
                            data["mode"] = "-U" if args[0].upper() == "SERIAL" else "-R"
                        elif kl == "host" and args:
                            data["host"] = args[0]
                        elif kl == "method" and args:
                            data["method"] = "-f" if args[0].upper() == "SPAWN" else "-F"
                        else:
                            break

                elif cmd == "show":
                    from Classes.utils import print_show_table
                    print_show_table([
                        {"name": "APP",    "value": data["app"],
                         "description": "Target package name: com.mmsf.taskhijackingvictim"},
                        {"name": "MODE",   "value": "SERIAL" if data["mode"] == "-U" else "REMOTE",
                         "description": "Serial or Remote. Default: SERIAL", "required": False},
                        {"name": "HOST",   "value": data["host"],
                         "description": "Host if MODE=REMOTE. Default: 127.0.0.1", "required": False},
                        {"name": "METHOD", "value": "SPAWN" if data["method"] == "-f" else "FRONTMOST",
                         "description": "Attach method. Default: SPAWN", "required": False},
                    ])

                elif cmd == "run":
                    if not data["app"]:
                        print(Fore.RED + "[-] Set APP first!" + Fore.RESET)
                        continue
                    try:
                        mmsf.hook_task_hijacking(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)

                elif cmd == "stop":
                    try:
                        mmsf.hook_task_hijacking("stop", data)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)

                elif cmd in ("back", "exit"):
                    back()
                    return 1

       # ── top-level menu ────────────────────────────────────────────────────
        modules      = ["detect", "generate", "frida_hook"]
        descriptions = [
            "Scan AndroidManifest.xml for singleTask + taskAffinity misconfigs (StrandHogg 1.0)",
            "Generate malicious APK manifest + Java payload + ADB trigger",
            "Hook victim app with Frida — live activity lifecycle monitor (runs in background)",
        ]

        while True:
            def init_completer(text, state):
                options = [i for i in modules if i.startswith(text)]
                if state < len(options):
                    return options[state]
                return None

            readline.set_completer(init_completer)
            input_val = shlex.split(input('mmsf (taskhijacking)> '))
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
                elif action == "detect":
                    handle_detect()
                elif action == "generate":
                    handle_generate()
                elif action == "frida_hook":
                    handle_frida_hook()
            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() in ("help", "?"):
                print_help()