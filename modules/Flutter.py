import readline
import shlex

from colorama import Fore
from Classes.constants import Constants
from Classes.utils import listmodules, print_help, unknown_cmd, back, quit_app


class Flutter:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Flutter application security testing — SSL bypass via Frida hook or ReFlutter APK patch"
        self._name = "flutter"

    def execute(self, mmsf):

        # ── frida ─────────────────────────────────────────────────────────────
        def handle_frida():
            frida_data = {
                "mode": "-U",
                "app": "",
                "host": "127.0.0.1",
                "pause": "",
                "method": "-f"
            }
            while True:
                set_data = ["mode", "app", "host", "pause", "method"]

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
                        status = mmsf.bypass_flutter_ssl_frida(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (flutter/frida)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()

                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (flutter/frida/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "mode" and args:
                            frida_data["mode"] = '-R' if args[0].lower() == "remote" else '-U'
                        elif cmd.lower() == "app" and args:
                            frida_data["app"] = args[0]
                        elif cmd.lower() == "host" and args:
                            frida_data["host"] = args[0]
                        elif cmd.lower() == "pause" and args:
                            frida_data["pause"] = "--pause" if args[0].lower() == "true" else ""
                        elif cmd.lower() == "method" and args:
                            frida_data["method"] = "-F" if args[0].lower() == "frontmost" else "-f"
                        else:
                            if execute(cmd.lower(), frida_data):
                                break
                else:
                    if execute(value, frida_data) == 2:
                        return 1

        # ── reflutter ─────────────────────────────────────────────────────────
        def handle_reflutter():
            reflutter_data = {
                "app": "",
                "apk_path": "",
                "burp_host": "127.0.0.1"
            }
            while True:
                set_data = ["app", "apk_path", "burp_host"]

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
                        status = mmsf.reflutter_sslpinning(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (flutter/reflutter)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()

                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (flutter/reflutter/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "app" and args:
                            reflutter_data["app"] = args[0]
                        elif cmd.lower() == "apk_path" and args:
                            reflutter_data["apk_path"] = args[0]
                        elif cmd.lower() == "burp_host" and args:
                            reflutter_data["burp_host"] = args[0]
                        else:
                            if execute(cmd.lower(), reflutter_data):
                                break
                else:
                    if execute(value, reflutter_data) == 2:
                        return 1

        # ── top-level menu ────────────────────────────────────────────────────
        modules = ["frida", "reflutter"]
        descriptions = [
            "Hook libflutter.so at runtime via Frida — no APK modification, works on live app",
            "Patch Flutter APK using ReFlutter to intercept traffic — requires reinstall"
        ]

        while True:
            def init_completer(text, state):
                options = [i for i in modules if i.startswith(text)]
                if state < len(options):
                    return options[state]
                return None

            readline.set_completer(init_completer)
            input_val = shlex.split(input('mmsf (flutter)> '))
            if len(input_val) < 1:
                continue
            if len(input_val) > 2:
                continue
            elif input_val[0].lower() == "exit":
                quit_app()
            elif input_val[0].lower() in ("listmodules", "show"):
                listmodules(modules, descriptions)
            elif input_val[0].lower() == "usemodule":
                if len(input_val) < 2:
                    unknown_cmd()
                    continue
                action = input_val[1].lower()
                if action not in modules:
                    unknown_cmd()
                elif action == "frida":
                    handle_frida()
                elif action == "reflutter":
                    handle_reflutter()
            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() in ("help", "?"):
                print_help()