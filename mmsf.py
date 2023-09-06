#!/usr/bin/python3

import os
import pkgutil
import readline
import shlex
from signal import signal, SIGINT
from Classes.MassiveMobileSecurityFramework import MassiveMobileSecurityFramework
from Classes.utils import listmodules, search, unknown_cmd
from colorama import Fore

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Type \'exit\' to exit')

def init_modules():
    print(Fore.GREEN + '... Initiating modules ...' + Fore.RESET)
    modules = []
    __path__ = [os.path.dirname(os.path.abspath(__file__)) + '/modules']
    for importer, modname, ispkg in pkgutil.walk_packages(path=__path__):
            p = __import__("modules." + modname)
            m = getattr(p, modname)
            c = getattr(m, modname)
            instance = c()
            modules.append(instance)

    return modules

def main():
    """
    modules: the modules instances
    details_: list of tuples for (name, description) for listmodules
    modules_dict: dict {name: instance} to perfom commands based on received name
    """
    
    modules = init_modules()
    details_ = [(x.name, x.description) for x in modules]
    modules_dict = {}
    for module in modules:
        modules_dict[module.name] = module
    modules_names, descriptions = zip(*details_) 

    mmsf = MassiveMobileSecurityFramework()
    initial_commands = ["usemodule", "exit", "listmodules", "search"]
    readline.parse_and_bind("tab: complete")

    while True:
        def init_completer(text, state):
                options = [i for i in initial_commands if i.startswith(text)]
                if state < len(options):
                    return options[state]
                else:
                    return None

        readline.set_completer(init_completer)

        input_val = shlex.split(input('mmsf> '))
        if len(input_val) < 1:
            continue
        if len(input_val) > 2:
            unknown_cmd()
        elif input_val[0].lower() == "exit":
            quit()
        elif input_val[0].lower() == "listmodules":
            listmodules(list(modules_names), list(descriptions))
        elif input_val[0].lower() == "usemodule":
            if len(input_val) == 2:
                action = input_val[1].lower()
                if action not in modules_names:
                    unknown_cmd()
                else:
                    modules_dict[action].execute(mmsf)
            else:
                print(Fore.RED + '[-] Usage: usemodule modulename' + Fore.RESET)
        elif input_val[0].lower() == "search":
            if len(input_val) == 2:
                action = input_val[1].lower()
                search(action, modules_dict)

if __name__ == "__main__":
    signal(SIGINT, handler)
    main()
    
