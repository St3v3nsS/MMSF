import readline
import shlex
from Classes.constants import Constants

from Classes.utils import back, listmodules, print_help, unknown_cmd


class ContentProvider:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Exploit the exported content provider to extract data"
        self._name = "provider"
    
    def execute(self, mmsf):
        def handle_query(mmsf):
            content = {
                "uri": "",
                "projection": [],
                "selection": "",
                "selection_args": []
            }
            while True:
                set_data = ["uri", "projection", "selection", "selection_args"]
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
                    return mmsf.query_provider(cmd, data)

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (provider/query)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (provider/query/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "uri":
                                content["uri"] = args[0].lower()
                            elif cmd.lower() == "projection":
                                content["projection"].append(args[0])
                            elif cmd.lower() == "selection":
                                content["selection"] = args[0]
                            elif cmd.lower() == "selection_args":
                                content["selection_args"].append(args[0])
                        else:
                            if execute(cmd.lower(), content):
                                break
                else:
                    if execute(value, content) == 2:
                        return 1 

        def handle_insert(mmsf):
            content = {
                "uri": "",
                "insert_values": [],
            }
            while True:
                set_data = ["uri", "insert_values"]
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
                    return mmsf.insert_provider(cmd, data)

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (provider/insert)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (provider/insert/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "uri":
                                content["uri"] = args[0].lower()
                            elif cmd.lower() == "insert_values":
                                args[0] = f'--{args[0]}'
                                content["insert_values"].extend(' '.join(args))
                        else:
                            if execute(cmd.lower(), content):
                                break
                else:
                    if execute(value, content) == 2:
                        return 1 

        def handle_read(mmsf):
            content = {
                "uri": ""
            }
            while True:
                set_data = ["uri"]
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
                    return mmsf.read_provider(cmd, data)

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (provider/read)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (provider/read/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if cmd.lower() == "uri"  and args:
                            content["uri"] = args[0].lower()
                        else:
                            if execute(cmd.lower(), content):
                                break
                else:
                    if execute(value, content) == 2:
                        return 1 

        def handle_update(mmsf):
            content = {
                "uri": "",
                "selection": "",
                "selection_args": [],
                "update_values": []
            }
            while True:
                set_data = ["uri", "update_values", "selection", "selection_args"]
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
                    return mmsf.update_provider(cmd, data)

                readline.set_completer(cmd_completer)
                
                value = shlex.split(input('mmsf (provider/update)> '))
                if len(value) < 1:
                    continue
                else:
                    value = value[0].lower()
                if value == "set":
                    while True:
                        
                        readline.set_completer(data_completer)
                        inpt = shlex.split(input('mmsf (provider/update/set)> '))
                        if len(inpt) > 1:
                            cmd, *args = inpt
                        elif len(inpt) < 1:
                            continue
                        else:
                            cmd = inpt[0]
                            args = None
                        if args:
                            if cmd.lower() == "uri":
                                content["uri"] = args[0].lower()
                            elif cmd.lower() == "update_values":
                                args[0] = f'--{args[0]}'
                                content["update_values"].extend(" ".join(args))
                            elif cmd.lower() == "selection":
                                content["selection"] = args[0]
                            elif cmd.lower() == "selection_args":
                                content["selection_args"].append(args[0])
                        else:
                            if execute(cmd.lower(), content):
                                break
                else:
                    if execute(value, content) == 2:
                        return 1 


        modules = ["query", "update", "insert", "read"]
        descriptions = [
            "Query the exported content provider to extract data.", 
            "Update the exported content provider data",
            "Insert data in the exported content provider",
            "Read file using the exported content provider"]

        while True:
            def init_completer(text, state):
                    options = [i for i in modules if i.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

            readline.set_completer(init_completer)

            input_val = shlex.split(input('mmsf (provider)> '))
            if len(input_val) < 1:
                continue
            if len(input_val) > 2:
                continue
            elif input_val[0].lower() == "exit":
                quit()
            elif input_val[0].lower() == "listmodules":
                listmodules(modules, descriptions)
            elif input_val[0].lower() == "usemodule":
                action = input_val[1].lower()
                if action not in modules:
                    unknown_cmd()
                elif action == "query":
                    handle_query(mmsf)
                elif action == "insert":
                    handle_insert(mmsf)
                elif action == "read":
                    handle_read(mmsf)
                else:
                    handle_update(mmsf)
            elif input_val[0].lower() == "back":
                back()
                break
            elif input_val[0].lower() == "help" or input_val[0] == "?":
                print_help()