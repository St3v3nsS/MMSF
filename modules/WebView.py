import readline
import shlex
from colorama import Fore
from Classes.constants import Constants
from Classes.utils import listmodules, print_help, unknown_cmd, back, print_show_table, quit_app


class WebView:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "WebView security testing — JS interfaces, file access, protocol handlers, cleanup"
        self._name = "webview"

    def execute(self, mmsf):

        # ── detect ────────────────────────────────────────────────────────────
        def handle_detect():
            data = {
                "apk_path":    "",
                "decoded_path": ""
            }
            while True:
                set_data = ["apk_path", "decoded_path"]

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
                        status = mmsf.webview_detect(cmd, data)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (webview/detect)> '))
                if len(value) < 1:
                    continue
                value = value[0].lower()

                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (webview/detect/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "apk_path" and args:
                            data["apk_path"] = args[0]
                        elif cmd.lower() == "decoded_path" and args:
                            data["decoded_path"] = args[0]
                        else:
                            if execute(cmd.lower(), data):
                                break
                else:
                    if execute(value, data) == 2:
                        return 1

        # ── frida ────────────────────────────────────────────────────────────
        def handle_frida():
            data = {
                "mode":   "-U",
                "app":    "",
                "host":   "127.0.0.1",
                "pause":  "",
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

                def execute(cmd, d):
                    status = 0
                    try:
                        status = mmsf.webview_frida(cmd, d)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (webview/frida)> '))
                if len(value) < 1:
                    continue
                value = value[0].lower()

                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (webview/frida/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "mode" and args:
                            data["mode"] = '-R' if args[0].lower() == "remote" else '-U'
                        elif cmd.lower() == "app" and args:
                            data["app"] = args[0]
                        elif cmd.lower() == "host" and args:
                            data["host"] = args[0]
                        elif cmd.lower() == "pause" and args:
                            data["pause"] = "--pause" if args[0].lower() == "true" else ""
                        elif cmd.lower() == "method" and args:
                            data["method"] = "-F" if args[0].lower() == "frontmost" else "-f"
                        else:
                            if execute(cmd.lower(), data):
                                break
                else:
                    if execute(value, data) == 2:
                        return 1

        # ── deeplink ─────────────────────────────────────────────────────────
        def handle_deeplink():
            data = {
                "package":    "",
                "url_scheme": "",
                "extra_key":  "url",
                "payloads":   "default"
            }
            while True:
                set_data = ["package", "url_scheme", "extra_key", "payloads"]

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

                def execute(cmd, d):
                    status = 0
                    try:
                        status = mmsf.webview_deeplink(cmd, d)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (webview/deeplink)> '))
                if len(value) < 1:
                    continue
                value = value[0].lower()

                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (webview/deeplink/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "package" and args:
                            data["package"] = args[0]
                        elif cmd.lower() == "url_scheme" and args:
                            data["url_scheme"] = args[0]
                        elif cmd.lower() == "extra_key" and args:
                            data["extra_key"] = args[0]
                        elif cmd.lower() == "payloads" and args:
                            # "default" or comma-separated custom payloads
                            data["payloads"] = args[0]
                        else:
                            if execute(cmd.lower(), data):
                                break
                else:
                    if execute(value, data) == 2:
                        return 1

        # ── fileaccess ────────────────────────────────────────────────────────
        def handle_fileaccess():
            data = {
                "package":   "",
                "file_path": "/sdcard/test.html",
                "probe":     "file"    # file | content | asset
            }
            while True:
                set_data = ["package", "file_path", "probe"]

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

                def execute(cmd, d):
                    status = 0
                    try:
                        status = mmsf.webview_fileaccess(cmd, d)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (webview/fileaccess)> '))
                if len(value) < 1:
                    continue
                value = value[0].lower()

                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (webview/fileaccess/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "package" and args:
                            data["package"] = args[0]
                        elif cmd.lower() == "file_path" and args:
                            data["file_path"] = args[0]
                        elif cmd.lower() == "probe" and args:
                            if args[0].lower() in ("file", "content", "asset"):
                                data["probe"] = args[0].lower()
                            else:
                                print(Fore.RED + "[-] probe must be: file | content | asset" + Fore.RESET)
                        else:
                            if execute(cmd.lower(), data):
                                break
                else:
                    if execute(value, data) == 2:
                        return 1

        # ── cleanup ───────────────────────────────────────────────────────────
        def handle_cleanup():
            data = {
                "mode":    "-U",
                "app":     "",
                "host":    "127.0.0.1",
                "pause":   "",
                "method":  "-F"    # frontmost by default — app must be open
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

                def execute(cmd, d):
                    status = 0
                    try:
                        status = mmsf.webview_cleanup(cmd, d)
                    except Exception as e:
                        print(Fore.RED + '[-] ' + str(e) + Fore.RESET)
                    return status

                readline.set_completer(cmd_completer)
                value = shlex.split(input('mmsf (webview/cleanup)> '))
                if len(value) < 1:
                    continue
                value = value[0].lower()

                if value == "set":
                    while True:
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (webview/cleanup/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "mode" and args:
                            data["mode"] = '-R' if args[0].lower() == "remote" else '-U'
                        elif cmd.lower() == "app" and args:
                            data["app"] = args[0]
                        elif cmd.lower() == "host" and args:
                            data["host"] = args[0]
                        elif cmd.lower() == "pause" and args:
                            data["pause"] = "--pause" if args[0].lower() == "true" else ""
                        elif cmd.lower() == "method" and args:
                            data["method"] = "-F" if args[0].lower() == "frontmost" else "-f"
                        else:
                            if execute(cmd.lower(), data):
                                break
                else:
                    if execute(value, data) == 2:
                        return 1

        # ── top-level menu ────────────────────────────────────────────────────
        modules = ["detect", "frida", "deeplink", "fileaccess", "cleanup"]
        descriptions = [
            "Static scan for dangerous WebView flags in decoded APK (smali + XML)",
            "Frida hooks — intercept loadUrl, addJavascriptInterface, evaluateJavascript at runtime",
            "Inject payloads via deep link URL schemes into WebView (javascript:/file:// probes)",
            "Protocol handler abuse — file://, content://, android_asset:// access probes",
            "Check WebView cleanup on logout (cache, cookies, history, session state)"
        ]

        while True:
            def init_completer(text, state):
                options = [i for i in modules if i.startswith(text)]
                if state < len(options):
                    return options[state]
                return None

            readline.set_completer(init_completer)
            input_val = shlex.split(input('mmsf (webview)> '))
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
                elif action == "detect":
                    handle_detect()
                elif action == "frida":
                    handle_frida()
                elif action == "deeplink":
                    handle_deeplink()
                elif action == "fileaccess":
                    handle_fileaccess()
                elif action == "cleanup":
                    handle_cleanup()
            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() in ("help", "?"):
                print_help()
